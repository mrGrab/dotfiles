#!/usr/bin/env python3
"""
Waybar custom clock module with Google Calendar agenda and event reminders.

Long-running: prints one JSON line per minute (and on changes). Left-click
runs `custom-clock.py toggle` (month/year view), middle-click runs
`custom-clock.py refresh` (fetch now); both signal the running instance via its
pid file in $XDG_RUNTIME_DIR. Reminders are sent with notify-send using each
event's Google "popup" reminders. Class "soon" is set shortly before an event.

Requirements:
    - googleworkspace-cli (`gws`): pacman -S googleworkspace-cli
    - Google Cloud project with Calendar API enabled and a Desktop OAuth client saved as ~/.config/gws/client_secret.json
    - Publish the OAuth app ("In production"), otherwise tokens expire in 7 days
    - gws auth login --scopes https://www.googleapis.com/auth/calendar.readonly
    Never commit ~/.config/gws/ (client secret and tokens).
"""

import calendar
import html
import json
import math
import os
import select
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

FETCH_INTERVAL = 900  # seconds
FETCH_DAYS = 8  # look-ahead for reminders; the tooltip shows today + tomorrow
# GTK tooltips wrap lines wider than ~70 chars; keep every line within this
TOOLTIP_WIDTH = 66
GRID_WIDTH = 20
GAP = "   "
YEAR_COLUMNS = 3  # 3 x 20 + gaps fits TOOLTIP_WIDTH; 4 columns would wrap
AGENDA_WIDTH = TOOLTIP_WIDTH - GRID_WIDTH - len(GAP)
TITLE_MAX = AGENDA_WIDTH - len("00:00–00:00  ")
CALENDAR_URL = "https://calendar.google.com"
TODAY_COLOR = "FireBrick"
DIM = "alpha='50%'"  # past events and weekends
VIDEO_MARK = "📹 "
MAX_DAY_EVENTS = 6  # per day; the rest collapse into "+N more"
SOON_MINUTES = 10  # bar gets class "soon" this long before an event
COUNTDOWN_MINUTES = 60  # next event shows "in Nm" only when this close
GWS_EXIT_AUTH = 2
# Year view reverts to month once the cursor leaves the clock (waybar has no
# hover-out event, so poll the cursor): below the bar, or sideways off the module
YEAR_POLL = 0.5  # seconds
BAR_BOTTOM = 40  # px; bar is 31px, small margin
MODULE_REACH = 80  # px from the click point, ~half the clock width
YEAR_TIMEOUT = 60  # seconds; fallback when the cursor can't be read

CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
RUNTIME_DIR = Path(os.environ.get("XDG_RUNTIME_DIR", CACHE_DIR))
PID_FILE = RUNTIME_DIR / "waybar-custom-clock.pid"
SENT_FILE = CACHE_DIR / "waybar-custom-clock" / "notified.json"

cal = calendar.Calendar(firstweekday=calendar.MONDAY)
state_lock = threading.Lock()


@dataclass(frozen=True, slots=True)
class Event:
    id: str
    title: str
    location: str
    start: datetime
    end: datetime
    all_day: bool
    reminders: tuple[int, ...]  # popup reminder offsets, minutes
    join: str | None
    link: str


@dataclass
class State:
    events: list[Event] | None = None
    fetched_at: datetime | None = None
    error: str | None = None
    year_view: bool = False


state = State()
refresh = threading.Event()


def local_now() -> datetime:
    return datetime.now(UTC).astimezone()


# --- Google Calendar -------------------------------------------------------


def fetch_events():
    """Return (events, error). error is None, 'auth', 'missing' or a message."""
    start = local_now().replace(hour=0, minute=0, second=0, microsecond=0)
    params = {
        "calendarId": "primary",
        "timeMin": start.isoformat(),
        "timeMax": (start + timedelta(days=FETCH_DAYS)).isoformat(),
        "singleEvents": True,
        "orderBy": "startTime",
        "maxResults": 250,
    }
    try:
        proc = subprocess.run(
            ["gws", "calendar", "events", "list", "--params", json.dumps(params)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return None, "missing"
    except subprocess.TimeoutExpired:
        return None, "gws timed out"
    if proc.returncode == GWS_EXIT_AUTH:
        return None, "auth"
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return (
            None,
            f"gws exit {proc.returncode}: {(proc.stderr or proc.stdout).strip()[:200]}",
        )
    if proc.returncode != 0 or "items" not in data:
        return None, f"gws exit {proc.returncode}: {str(data.get('error', data))[:200]}"
    try:
        events = [e for e in (parse_event(i, data) for i in data["items"]) if e]
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        return None, f"bad event data: {e!r}"
    return events, None


def parse_event(item, response):
    """Normalize an API event; returns None for declined/unsupported events."""
    for attendee in item.get("attendees", []):
        if attendee.get("self") and attendee.get("responseStatus") == "declined":
            return None
    start, end = item.get("start", {}), item.get("end", {})
    all_day = "date" in start
    if all_day:
        s = datetime.combine(
            date.fromisoformat(start["date"]), datetime.min.time()
        ).astimezone()
        e = datetime.combine(
            date.fromisoformat(end["date"]), datetime.min.time()
        ).astimezone()
    elif "dateTime" in start:
        s = datetime.fromisoformat(start["dateTime"]).astimezone()
        e = datetime.fromisoformat(end["dateTime"]).astimezone()
    else:
        return None

    reminders = item.get("reminders", {})
    if reminders.get("useDefault"):
        # API defaultReminders apply to timed events only
        overrides = [] if all_day else response.get("defaultReminders", [])
    else:
        overrides = reminders.get("overrides", [])

    join = item.get("hangoutLink")
    for ep in item.get("conferenceData", {}).get("entryPoints", []):
        if not join and ep.get("entryPointType") == "video":
            join = ep.get("uri")

    return Event(
        id=item.get("id", ""),
        title=item.get("summary") or "(no title)",
        location=item.get("location", ""),
        start=s,
        end=e,
        all_day=all_day,
        reminders=tuple(
            sorted({r["minutes"] for r in overrides if r.get("method") == "popup"})
        ),
        join=join,
        link=item.get("htmlLink") or CALENDAR_URL,
    )


def fetch_loop(wake_fd):
    """Refresh events every FETCH_INTERVAL of wall time (survives suspend)."""
    last = 0.0
    while True:
        if time.time() - last >= FETCH_INTERVAL:
            last = time.time()
            events, error = fetch_events()
            with state_lock:
                state.error = error
                if events is not None:
                    state.events, state.fetched_at = events, local_now()
            if error:
                print(f"custom-clock: {error}", file=sys.stderr, flush=True)
            os.write(wake_fd, b"f")
        if refresh.wait(15):
            refresh.clear()
            last = 0.0


# --- Notifications ----------------------------------------------------------


def load_sent():
    try:
        return json.loads(SENT_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def save_sent(sent):
    SENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = SENT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(sent))
    tmp.replace(SENT_FILE)


def notify(event, now):
    if event.all_day:
        when = event.start.strftime("%a %e %b").replace("  ", " ") + ", all day"
    elif event.start <= now:
        when = f"started {int((now - event.start).total_seconds() // 60)} min ago"
    else:
        when = f"{event.start:%H:%M}–{event.end:%H:%M}"
    body = "\n".join(filter(None, [when, event.location]))
    cmd = [
        "notify-send",
        "--app-name=Calendar",
        "--icon=x-office-calendar",
        "--action=open=Open",
    ]
    if event.join:
        cmd.append("--action=join=Join")
    cmd += [event.title, html.escape(body, quote=False)]

    def run():
        try:
            choice = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            ).stdout.strip()
        except FileNotFoundError:
            return
        url = {"open": event.link, "join": event.join}.get(choice)
        if url:
            subprocess.Popen(
                ["xdg-open", url],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    threading.Thread(target=run, daemon=True).start()


def due_reminders(events, sent, now):
    """Return (due, new_sent): one entry in due per reminder to fire now.

    Each reminder fires once; late ones fire if the event hasn't ended. sent
    maps reminder keys to event end timestamps, pruned a day after the end.
    """
    new_sent = dict(sent)
    due = []
    for ev in events:
        if ev.end <= now:
            continue
        for minutes in ev.reminders:
            key = f"{ev.id}|{ev.start.isoformat()}|{minutes}"
            if key not in new_sent and ev.start - timedelta(minutes=minutes) <= now:
                due.append(ev)
                new_sent[key] = ev.end.timestamp()
    cutoff = now.timestamp() - 86400
    return due, {k: end for k, end in new_sent.items() if end >= cutoff}


# --- Rendering --------------------------------------------------------------


def month_lines(year, month, today):
    """Month grid as (plain_width, markup) lines; always 8 lines, 20 wide."""
    title = date(year, month, 1).strftime("%B %Y")
    weekdays = [(i + cal.firstweekday) % 7 for i in range(7)]
    weekend = {calendar.SATURDAY, calendar.SUNDAY}

    def cell(text, weekday, is_today=False):
        if is_today:
            return f"<span color='{TODAY_COLOR}'><b>{text}</b></span>"
        return f"<span {DIM}>{text}</span>" if weekday in weekend else text

    lines = [
        f"<b>{html.escape(title.center(GRID_WIDTH))}</b>",
        " ".join(cell(calendar.day_abbr[wd][:2], wd) for wd in weekdays),
    ]
    weeks = cal.monthdayscalendar(year, month)
    weeks += [[0] * 7] * (6 - len(weeks))
    for week in weeks:
        lines.append(
            " ".join(
                cell(f"{d:2}", wd, date(year, month, d) == today) if d else "  "
                for d, wd in zip(week, weekdays, strict=True)
            )
        )
    return lines


def truncate(text, width=TITLE_MAX):
    return text if len(text) <= width else text[: width - 1] + "…"


def countdown(delta):
    return f"in {max(1, math.ceil(delta.total_seconds() / 60))}m"


def event_line(e, now, next_event):
    """One agenda line: time, optional video mark, title, optional countdown."""
    when = "all-day    " if e.all_day else f"{e.start:%H:%M}–{e.end:%H:%M}"
    mark = VIDEO_MARK if e.join else ""
    suffix = f" · {countdown(e.start - now)}" if e is next_event else ""
    # the video mark renders two cells wide
    title = truncate(e.title, TITLE_MAX - len(suffix) - 3 * bool(mark))
    line = f"{when}  {mark}{html.escape(title, quote=False)}{suffix}"
    if e.all_day:
        return line
    if e.end <= now:
        return f"<span {DIM}>{line}</span>"
    return f"<b>{line}</b>" if e.start <= now else line


def agenda_lines(events, fetched_at, error, now):
    lines = []
    if error == "auth":
        lines.append("⚠ gws login expired")
        lines.append("<i>login command: custom-clock.py header</i>")
    elif error == "missing":
        lines.append("⚠ gws not installed")
    elif error and fetched_at:
        lines.append(f"<i>(stale, {fetched_at:%H:%M})</i>")
    elif error:
        lines.append(f"⚠ {html.escape(truncate(error, AGENDA_WIDTH - 2))}")
    if events is None:
        return lines or ["<i>loading…</i>"]

    horizon = now + timedelta(minutes=COUNTDOWN_MINUTES)
    upcoming = [e for e in events if not e.all_day and now < e.start <= horizon]
    next_event = min(upcoming, key=lambda e: e.start, default=None)
    today = now.date()
    for label, day in (("Today", today), ("Tomorrow", today + timedelta(days=1))):
        lo = datetime.combine(day, datetime.min.time()).astimezone()
        hi = lo + timedelta(days=1)
        day_events = sorted(
            (e for e in events if e.start < hi and e.end > lo),
            key=lambda e: (not e.all_day, e.start),
        )
        lines.append(f"<b>{label}</b>")
        if not day_events:
            lines.append("<i>no events</i>")
        shown = day_events
        if len(shown) > MAX_DAY_EVENTS:  # drop finished events first
            shown = [e for e in shown if e.all_day or e.end > now]
        shown = shown[:MAX_DAY_EVENTS]
        lines += [event_line(e, now, next_event) for e in shown]
        if hidden := len(day_events) - len(shown):
            lines.append(f"<i>+{hidden} more</i>")
    return lines


def starting_soon(events, now):
    return any(
        not e.all_day and now < e.start <= now + timedelta(minutes=SOON_MINUTES)
        for e in events or []
    )


def render(snap, now):
    """Waybar JSON for a State snapshot."""
    today = now.date()
    if snap.year_view:
        months = [month_lines(today.year, m, today) for m in range(1, 13)]
        rows = []
        for i in range(0, 12, YEAR_COLUMNS):
            rows += [
                GAP.join(parts)
                for parts in zip(*months[i : i + YEAR_COLUMNS], strict=True)
            ] + [""]
        body = rows[:-1]
    else:
        agenda = agenda_lines(snap.events, snap.fetched_at, snap.error, now)
        grid = month_lines(today.year, today.month, today)
        height = max(len(grid), len(agenda))
        grid += [" " * GRID_WIDTH] * (height - len(grid))
        agenda += [""] * (height - len(agenda))
        body = [g + GAP + a for g, a in zip(grid, agenda, strict=True)]
    classes = ["year" if snap.year_view else "month"]
    if starting_soon(snap.events, now):
        classes.append("soon")
    return {
        "text": now.strftime("%a %e %b  %H:%M"),
        "tooltip": "<tt>" + "\n".join(body).rstrip() + "</tt>",
        "class": classes,
    }


# --- Main loop ----------------------------------------------------------------


def cursor_pos():
    try:
        proc = subprocess.run(
            ["hyprctl", "cursorpos", "-j"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        pos = json.loads(proc.stdout)
        return int(pos["x"]), int(pos["y"])
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
        return None


def year_view_expired(anchor, pos, elapsed):
    """True once the cursor has left the clock the year view was opened from."""
    if anchor is None or pos is None:
        return elapsed > YEAR_TIMEOUT
    return pos[1] > BAR_BOTTOM or abs(pos[0] - anchor[0]) > MODULE_REACH


def send(sig):
    """Signal the running clock; no-op if the pid file is missing or stale."""
    try:
        pid = int(PID_FILE.read_text())
        args = Path(f"/proc/{pid}/cmdline").read_bytes().rstrip(b"\0").split(b"\0")
        # a recycled pid would be killed by SIGUSR*, so check it's still the clock
        if args[-1].endswith(b"custom-clock.py"):
            os.kill(pid, sig)
    except (OSError, ValueError):
        pass


def run():
    PID_FILE.write_text(str(os.getpid()))

    rfd, wfd = os.pipe()
    os.set_blocking(wfd, False)
    signal.set_wakeup_fd(wfd)

    def toggle(*_):
        state.year_view = not state.year_view

    signal.signal(signal.SIGUSR1, toggle)
    signal.signal(signal.SIGUSR2, lambda *_: refresh.set())
    threading.Thread(target=fetch_loop, args=(wfd,), daemon=True).start()

    sent = load_sent()
    last_output = None
    anchor, opened_at = None, 0.0
    while True:
        if not state.year_view:
            opened_at = 0.0
        elif not opened_at:  # just toggled: the cursor is on the clock
            anchor, opened_at = cursor_pos(), time.monotonic()
        elif year_view_expired(anchor, cursor_pos(), time.monotonic() - opened_at):
            state.year_view = False
        now = local_now()
        with state_lock:
            snap = replace(state)
        try:
            output = json.dumps(render(snap, now))
            if snap.events:
                due, new_sent = due_reminders(snap.events, sent, now)
                for ev in due:
                    notify(ev, now)
                if new_sent != sent:
                    # update first: a failed save must not re-fire reminders
                    sent = new_sent
                    save_sent(sent)
        # never leave the bar without a clock
        except (OSError, KeyError, TypeError, ValueError, AttributeError) as e:
            output = json.dumps(
                {
                    "text": now.strftime("%a %e %b  %H:%M"),
                    "tooltip": f"⚠ {html.escape(repr(e))}",
                    "class": "error",
                }
            )
        if output != last_output:
            print(output, flush=True)
            last_output = output
        # Short cap so the minute flips promptly after suspend (select uses monotonic time)
        timeout = min(60 - now.second - now.microsecond / 1e6, 5)
        if state.year_view:
            timeout = min(timeout, YEAR_POLL)
        if select.select([rfd], [], [], timeout)[0]:
            os.read(rfd, 512)


COMMANDS = {"toggle": signal.SIGUSR1, "refresh": signal.SIGUSR2}


def main():
    if len(sys.argv) == 1:
        run()
    elif len(sys.argv) == 2 and sys.argv[1] in COMMANDS:
        send(COMMANDS[sys.argv[1]])
    else:
        print(
            f"usage: {Path(sys.argv[0]).name} [{'|'.join(COMMANDS)}]", file=sys.stderr
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
