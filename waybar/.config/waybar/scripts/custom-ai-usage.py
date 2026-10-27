#!/usr/bin/env python3
"""
Waybar custom module showing AI subscription quota usage.

Bar: icon + usage % of the --primary provider (Claude/OpenAI: 5-hour window, Copilot: monthly premium requests).
Tooltip: all windows of every configured provider, primary first.

Credentials:
    - Claude:  ~/.claude/.credentials.json (Claude Code login)
    - OpenAI:  ~/.codex/auth.json (Codex CLI login)
    - Copilot: $GITHUB_COPILOT_TOKEN
A provider without credentials is left out of the tooltip.

All endpoints are undocumented and may change without notice.

Expired Claude/Codex access tokens are refreshed and written back, but only
while that CLI isn't running (it refreshes on its own and would otherwise
race us for the rotated refresh token). The last good data is cached so a
failed fetch shows the previous values marked stale.
"""

import argparse
import base64
import html
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from http.client import HTTPResponse
from pathlib import Path
from typing import Any, NamedTuple, cast

CACHE_FILE = (
    Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    / "waybar-ai-usage.json"
)
WARNING_PCT = 75
CRITICAL_PCT = 90

CLAUDE_CREDS = Path.home() / ".claude" / ".credentials.json"
CLAUDE_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
CLAUDE_TOKEN_URL = "https://platform.claude.com/v1/oauth/token"
CLAUDE_CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"  # public Claude Code ID
CLAUDE_BETA = "oauth-2025-04-20"
# the usage endpoint rate-limits hard without a Claude Code user agent
CLAUDE_USER_AGENT = "claude-cli/2.1.281 (external, cli)"
CLAUDE_WINDOWS = {
    "five_hour": "5-hour",
    "seven_day": "Weekly",
    "seven_day_opus": "Weekly Opus",
    "seven_day_sonnet": "Weekly Sonnet",
}

CODEX_AUTH = Path.home() / ".codex" / "auth.json"
OPENAI_USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"
OPENAI_TOKEN_URL = "https://auth.openai.com/oauth/token"
OPENAI_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"  # public Codex CLI ID

COPILOT_USAGE_URL = "https://api.github.com/copilot_internal/user"
COPILOT_HEADERS = {
    "Accept": "application/json",
    "Editor-Version": "vscode/1.96.2",
    "Editor-Plugin-Version": "copilot-chat/0.26.7",
    "User-Agent": "GitHubCopilotChat/0.26.7",
    "X-GitHub-Api-Version": "2025-04-01",
}
COPILOT_QUOTAS = {
    "premium_interactions": "Premium",
    "chat": "Chat",
    "completions": "Completions",
}

ICONS = {"claude": "", "openai": "", "copilot": ""}
NAMES = {"claude": "Claude", "openai": "OpenAI", "copilot": "Copilot"}

type JSON = dict[str, Any]


class Window(NamedTuple):
    label: str
    percent: float
    resets_at: float | None  # epoch seconds
    detail: str = ""


class Usage(NamedTuple):
    plan: str
    windows: list[Window]  # windows[0] is the bar value


class NotConfigured(Exception):
    """No credentials for this provider; hide it."""


class Args(argparse.Namespace):
    primary: str = "claude"


def http_json(url: str, headers: dict[str, str], body: JSON | None = None) -> JSON:
    """GET (or POST body as JSON); raises OSError or ValueError on failure."""
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers = {**headers, "Content-Type": "application/json"}
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with cast(
            HTTPResponse, urllib.request.urlopen(request, timeout=10)
        ) as response:
            return cast(JSON, json.load(response))
    except urllib.error.HTTPError as e:
        # only the error code, never the raw body: it may echo tokens back
        try:
            error = cast(JSON, json.load(e)).get("error")
        except ValueError:
            error = None
        if isinstance(error, dict):
            error = cast(JSON, error).get("code") or error.get("type")
        code = f" ({error})" if isinstance(error, str) else ""
        host = urllib.parse.urlsplit(url).hostname
        raise OSError(f"HTTP {e.code} from {host}{code}") from None


def parse_time(value: object) -> float | None:
    """ISO 8601 string or epoch number -> epoch seconds."""
    if isinstance(value, int | float):
        return float(value)
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:  # date-only values are UTC
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.timestamp()


def jwt_exp(token: str) -> float:
    """exp claim of a JWT, 0 if unreadable (treated as expired)."""
    try:
        payload = token.split(".")[1]
        claims = json.loads(
            base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        )
        return float(claims["exp"])
    except (IndexError, KeyError, TypeError, ValueError):
        return 0


def load_json(path: Path) -> JSON:
    try:
        return cast(JSON, json.loads(path.read_text()))
    except FileNotFoundError:
        raise NotConfigured from None


def ensure_can_refresh(cli: str) -> None:
    """Refuse to rotate tokens under a running CLI; it will refresh them itself."""
    if (
        subprocess.run(
            ["pgrep", "-x", cli], capture_output=True, check=False
        ).returncode
        == 0
    ):
        raise OSError(f"token expired; {cli} is running and will refresh it")


def save_if_unchanged(
    path: Path,
    refresh_token: Callable[[JSON], object],
    expected: str,
    update: Callable[[JSON], None],
    indent: int | None = None,
) -> None:
    """
    Apply update to a fresh read of path and write it back atomically, unless
    the CLI rotated the refresh token meanwhile (then its copy wins). Only the
    keys update touches change; everything else (e.g. MCP tokens) is kept.
    """
    data = load_json(path)
    if refresh_token(data) != expected:
        return
    update(data)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w") as f:  # mkstemp creates it 0600
            json.dump(data, f, indent=indent)  # keep the CLI's own formatting
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def claude_token() -> str:
    oauth = load_json(CLAUDE_CREDS).get("claudeAiOauth")
    if not oauth:
        raise NotConfigured
    if oauth["expiresAt"] / 1000 > time.time():
        return cast(str, oauth["accessToken"])

    ensure_can_refresh("claude")
    new = http_json(
        CLAUDE_TOKEN_URL,
        {"anthropic-beta": CLAUDE_BETA, "User-Agent": "claude-cli/1.0"},
        {
            "grant_type": "refresh_token",
            "client_id": CLAUDE_CLIENT_ID,
            "refresh_token": oauth["refreshToken"],
        },
    )

    def update(data: JSON) -> None:
        o = data["claudeAiOauth"]
        o["accessToken"] = new["access_token"]
        o["refreshToken"] = new.get("refresh_token") or o["refreshToken"]
        o["expiresAt"] = int((time.time() + new["expires_in"]) * 1000)

    save_if_unchanged(
        CLAUDE_CREDS,
        lambda data: data.get("claudeAiOauth", {}).get("refreshToken"),
        oauth["refreshToken"],
        update,
    )
    return cast(str, new["access_token"])


def fetch_claude() -> Usage:
    token = claude_token()
    oauth = load_json(CLAUDE_CREDS)["claudeAiOauth"]
    data = http_json(
        CLAUDE_USAGE_URL,
        {
            "Authorization": f"Bearer {token}",
            "anthropic-beta": CLAUDE_BETA,
            "User-Agent": CLAUDE_USER_AGENT,
        },
    )
    windows = [
        Window(label, float(w["utilization"]), parse_time(w.get("resets_at")))
        for key, label in CLAUDE_WINDOWS.items()
        if isinstance(w := data.get(key), dict) and w.get("utilization") is not None
    ]
    if not windows or windows[0].label != "5-hour":
        raise ValueError("unexpected response: no 5-hour window")
    return Usage(str(oauth.get("subscriptionType") or ""), windows)


def openai_tokens() -> JSON:
    tokens = load_json(CODEX_AUTH).get("tokens")
    if not tokens:
        raise NotConfigured
    if jwt_exp(tokens["access_token"]) > time.time():
        return cast(JSON, tokens)

    ensure_can_refresh("codex")
    new = http_json(
        OPENAI_TOKEN_URL,
        {},
        {
            "client_id": OPENAI_CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "scope": "openid profile email",
        },
    )
    keys = ("access_token", "refresh_token", "id_token")
    refreshed = {k: new[k] for k in keys if new.get(k)}

    def update(data: JSON) -> None:
        data["tokens"].update(refreshed)
        data["last_refresh"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    save_if_unchanged(
        CODEX_AUTH,
        lambda data: data.get("tokens", {}).get("refresh_token"),
        tokens["refresh_token"],
        update,
        indent=2,
    )
    return {**tokens, **refreshed}


def fetch_openai() -> Usage:
    tokens = openai_tokens()
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "User-Agent": "codex-cli",
    }
    if tokens.get("account_id"):
        headers["ChatGPT-Account-Id"] = tokens["account_id"]
    data = http_json(OPENAI_USAGE_URL, headers)

    windows = []
    for key in ("primary_window", "secondary_window"):
        w = (data.get("rate_limit") or {}).get(key)
        if not isinstance(w, dict):
            continue
        hours = round((w.get("limit_window_seconds") or 0) / 3600)
        label = "Weekly" if hours == 168 else f"{hours}-hour"
        windows.append(
            Window(label, float(w["used_percent"]), parse_time(w.get("reset_at")))
        )
    if not windows:
        raise ValueError("unexpected response: no rate limit windows")
    return Usage(str(data.get("plan_type") or ""), windows)


def fetch_copilot() -> Usage:
    token = os.environ.get("GITHUB_COPILOT_TOKEN")
    if not token:
        raise NotConfigured
    data = http_json(
        COPILOT_USAGE_URL, {**COPILOT_HEADERS, "Authorization": f"token {token}"}
    )
    resets_at = parse_time(
        data.get("quota_reset_date_utc") or data.get("quota_reset_date")
    )

    windows = []
    for key, label in COPILOT_QUOTAS.items():
        q = (data.get("quota_snapshots") or {}).get(key)
        if (
            not isinstance(q, dict)
            or q.get("unlimited")
            or q.get("percent_remaining") is None
        ):
            continue
        detail = ""
        if q.get("entitlement"):
            detail = (
                f"{q['entitlement'] - q.get('remaining', 0):g}/{q['entitlement']:g}"
            )
        windows.append(
            Window(label, 100 - float(q["percent_remaining"]), resets_at, detail)
        )
    if not windows or windows[0].label != "Premium":
        raise ValueError("unexpected response: no premium quota")
    return Usage(str(data.get("copilot_plan") or ""), windows)


FETCHERS: dict[str, Callable[[], Usage]] = {
    "claude": fetch_claude,
    "openai": fetch_openai,
    "copilot": fetch_copilot,
}


def countdown(resets_at: float | None) -> str:
    if resets_at is None:
        return ""
    minutes = max(0, int(resets_at - time.time()) // 60)
    days, hours, mins = minutes // 1440, minutes // 60 % 24, minutes % 60
    if days:
        return f"resets in {days}d {hours}h"
    return f"resets in {hours}h {mins}m" if hours else f"resets in {mins}m"


def level(percent: float) -> str:
    if percent >= CRITICAL_PCT:
        return "critical"
    return "warning" if percent >= WARNING_PCT else "low"


def provider_tooltip(
    name: str, usage: Usage | None, error: str, fetched_at: float
) -> str:
    title = f"<b>{ICONS[name]} {NAMES[name]}</b>"
    if usage and usage.plan:
        title += f" <small>{html.escape(usage.plan)}</small>"
    lines = [title]
    for w in usage.windows if usage else []:
        detail = f" ({w.detail})" if w.detail else ""
        lines.append(
            f"  {w.label}:\t<tt>{w.percent:>3.0f}%</tt>{detail}\t<small>{countdown(w.resets_at)}</small>"
        )
    if error:
        state = (
            f"stale since {time.strftime('%H:%M', time.localtime(fetched_at))}"
            if usage
            else "error"
        )
        lines.append(f"  <i><small>{state}: {html.escape(error)}</small></i>")
    return "\n".join(lines)


def load_cache() -> dict[str, JSON]:
    try:
        return cast(dict[str, JSON], json.loads(CACHE_FILE.read_text()))
    except (OSError, ValueError):
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="AI subscription usage for Waybar.")
    _ = parser.add_argument("--primary", choices=FETCHERS, default="claude")
    args = parser.parse_args(namespace=Args())

    def fetch(name: str) -> Usage | str | None:
        """Usage, an error message, or None if not configured."""
        try:
            return FETCHERS[name]()
        except NotConfigured:
            return None
        except (OSError, ValueError, KeyError, TypeError) as e:
            return str(e) or type(e).__name__

    with ThreadPoolExecutor() as pool:
        results = dict(zip(FETCHERS, pool.map(fetch, FETCHERS), strict=True))

    cache = load_cache()
    now = time.time()
    sections: list[str] = []
    text, classes = f"{ICONS[args.primary]} n/a", ["error"]
    # primary first, then the rest in FETCHERS order
    for name in sorted(FETCHERS, key=lambda n: n != args.primary):
        result = results[name]
        if result is None:
            if name == args.primary:  # hidden elsewhere, but explain the n/a
                sections.append(f"<b>{ICONS[name]} {NAMES[name]}</b>: not configured")
            continue
        error, fetched_at = "", now
        if isinstance(result, Usage):
            usage: Usage | None = result
            cache[name] = {"usage": result, "fetched_at": now}
        else:
            error = result
            cached = cache.get(name)
            usage = None
            if cached:
                plan, windows = cached["usage"]
                usage = Usage(plan, [Window(*w) for w in windows])
                fetched_at = cached["fetched_at"]
        sections.append(provider_tooltip(name, usage, error, fetched_at))
        if name == args.primary and usage:
            percent = usage.windows[0].percent
            text = f"{ICONS[name]} {percent:.0f}%"
            classes = [level(percent)] + (["stale"] if error else [])

    try:
        CACHE_FILE.write_text(json.dumps(cache))
    except OSError:
        pass  # cache is best-effort
    sections.append(f"<i><small>Data pulled:\t{time.strftime('%H:%M:%S')}</small></i>")
    tooltip = "\n\n".join(sections)
    # always exit 0: waybar hides the module on a non-zero exit
    print(json.dumps({"text": text, "tooltip": tooltip, "class": classes}))


if __name__ == "__main__":
    main()
