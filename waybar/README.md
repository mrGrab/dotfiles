# Waybar

Waybar configuration for Hyprland: a single top bar on `DP-1` with workspaces, window title, a Google Calendar clock, weather, and system controls.

## Layout

```text
waybar/.config/waybar/
├── config.jsonc              # bar settings, module order, includes
├── style.css                 # styling (imports colors.css)
├── colors.css                # shared desktop palette
├── modules/                  # one JSON file per module
│   ├── clock.json            # built-in clock (kept, currently disabled)
│   ├── clock/calendar.json   # built-in clock calendar settings
│   ├── workspaces.json, window.json, language.json,
│   ├── wireplumber.json, bluetooth.json, tray.json
│   └── custom/
│       ├── clock.json        # Google Calendar clock
│       ├── weather.json      # Google Weather
│       ├── notification.json # swaync
│       ├── power.json        # power menu (+ power_menu.xml)
└── scripts/
    ├── custom-clock.py       # Google Calendar clock + reminders
    ├── calendar-app.sh       # focus-or-launch the Calendar app window
    └── custom-weather.py     # weather
```

## Modules

| Position | Module                | Notes                                           |
| -------- | --------------------- | ----------------------------------------------- |
| left     | `hyprland/workspaces` | Scroll to switch workspaces                     |
| left     | `hyprland/window`     | Active window title                             |
| center   | `custom/clock`        | [Google Calendar clock](#google-calendar-clock) |
| center   | `custom/weather`      | Needs `GOOGLE_API_KEY` ([Weather](#weather))    |
| right    | `tray`                |                                                 |
| right    | `hyprland/language`   | Click to switch layout                          |
| right    | `wireplumber`         | Right-click: pavucontrol, middle-click: mute    |
| right    | `custom/notification` | swaync; click: panel, right-click: DND          |
| right    | `custom/power`        | Suspend / hibernate / reboot / shutdown menu    |

## Install

```bash
sudo pacman -S waybar swaync pavucontrol python
stow -t ~ waybar
```

Icons need a Nerd Font (the style falls back to `NotoSans NFP Med`).
`config.jsonc` changes need a waybar restart; `style.css` reloads automatically.

## Weather

`custom/weather` uses the Google Weather API with an API key (weather data isn't tied to a user, so no OAuth is needed).

1. In a Google Cloud project, enable **Weather API** and create an **API key** (restrict it to the Weather API).
2. Export `GOOGLE_API_KEY` in your session environment, outside this repo.
3. Set your coordinates in `modules/custom/weather.json`.

The module is hidden when the key is missing. The script uses only the Python standard library.

---

## Google Calendar clock

`custom/clock` replaces the built-in clock. It shows the time in the bar and, on hover, the month grid with today's and tomorrow's Google Calendar events.
It also sends desktop notifications for event reminders.

### Features

- **Tooltip**: month grid (weekends dimmed, today in red) + agenda for today and tomorrow
  - past events dimmed, current event bold, 📹 for events with a video link
  - `· in 25m` on the next event when it starts within an hour
  - at most 6 events per day, then `+N more`
  - events you declined are hidden
- **Bar**: the clock turns accent blue when an event starts within 10 minutes
- **Notifications**: each event's Google "popup" reminders, sent via swaync with **Open** and **Join** (video link) buttons. Reminders missed during suspend fire once if the event hasn't ended. Nothing fires twice across restarts. Swaync Do Not Disturb silences them.
- **Offline / errors**: the time always shows; the tooltip shows stale events or a warning

| Mouse        | Action                                                        |
| ------------ | ------------------------------------------------------------- |
| Hover        | Month + events                                                |
| Left-click   | Year view (returns to month when the cursor leaves the clock) |
| Right-click  | Focus the Google Calendar app window, or open it              |
| Middle-click | Refresh events now                                            |

```text
   September 2026      Today
Mo Tu We Th Fr Sa Su   09:30–10:00  Standup
    1  2  3  4  5  6   14:00–15:00  📹 1:1 with Olena
 7  8  9 10 11 12 13   15:30–16:00  📹 Design review · in 25m
14 15 16 17 18 19 20   Tomorrow
21 22 23 24 25 26 27   all-day      Team offsite
28 29 30               10:00–11:00  Planning
```

### How it works

- `scripts/custom-clock.py` is a long-running script (Python standard library only). It prints one JSON line per minute and on changes.
- Events come from [`gws`](https://github.com/googleworkspace/cli) (Google Workspace CLI) every 5 minutes: `gws calendar events list` on the primary calendar. `gws` handles OAuth and stores tokens encrypted.
- Mouse actions run `custom-clock.py toggle` (year view) and `custom-clock.py refresh`, which signal the running instance (`SIGUSR1` / `SIGUSR2`) via its pid file `$XDG_RUNTIME_DIR/waybar-custom-clock.pid`. A stale pid file is ignored.
- Sent reminders are tracked in `~/.cache/waybar-custom-clock/notified.json`.
- The cursor is polled (`hyprctl cursorpos`) only while the year view is open, because waybar has no hover-out event.

### First-time setup

#### 1. Install `gws`

```bash
sudo pacman -S googleworkspace-cli
```

#### 2. Google Cloud project

Open [Google Cloud Console](https://console.cloud.google.com/) and select or create a project. The weather project can be reused.

#### 3. Enable the Calendar API

**APIs & Services → Library → Google Calendar API → Enable**.

#### 4. Configure Google Auth Platform (OAuth consent screen)

The console shows _"Google Auth Platform not configured yet"_. Click **Get started**:

- **App name**: e.g. `waybar-calendar` (shown on the sign-in page)
- **User support email**: your Gmail
- **Audience**: **External** (the only option for personal Gmail accounts; _Internal_ is for Workspace organisations)
- **Contact email**: your Gmail
- Accept the policy → **Create**

On the **Branding** page fill in **only** the required fields. Do **not** upload a logo: it sends the app into brand verification.

#### 5. Publishing status: Testing vs production

| Status            | What you need                                      | Login lasts                |
| ----------------- | -------------------------------------------------- | -------------------------- |
| **Testing**       | **Audience → Test users → Add users** → your Gmail | ~7 days, then log in again |
| **In production** | **Audience → Publish app**                         | until revoked              |

Publishing may be blocked with _"complete your configuration on the Branding page"_, which in practice means Google wants an app home page, a privacy policy and an **authorized domain** (a domain you own and have verified).
If you don't have one, stay in **Testing**: everything works, and the tooltip tells you when to log in again. Removing all scopes from the **Data access** page _may_ also unblock publishing (untested); the scope is requested at login anyway.

#### 6. Create the Desktop OAuth client

**Google Auth Platform → Clients → Create client**:

- **Application type**: **Desktop app**
- **Name**: anything
- **Download JSON**, then:

```bash
mkdir -p ~/.config/gws
mv ~/Downloads/client_secret_*.json ~/.config/gws/client_secret.json
chmod 600 ~/.config/gws/client_secret.json
```

An API key can't be used instead: API keys only read **public** calendars.

#### 7. Log in (read-only)

```bash
gws auth login --scopes https://www.googleapis.com/auth/calendar.readonly
```

- Use the **full scope URL**. `-s calendar` means `--services` (it filters the scope picker) and fails with _"OAuth2 scope name is invalid"_.
- The browser warns _"Google hasn't verified this app"_: it's your own app, so choose **Advanced → Go to waybar-calendar (unsafe)**.

Check that it works:

```bash
gws calendar events list --params '{"calendarId":"primary","maxResults":3}'
```

#### 8. Install Google Calendar as an app (for right-click)

1. Open <https://calendar.google.com> in Chromium.
2. **⋮ → Cast, save and share → Install page as app**.
3. Find the app id:

   ```bash
   ls ~/.local/share/applications/chrome-*-Default.desktop
   # chrome-<APP_ID>-Default.desktop
   ```

4. If the id differs from `kjbdgfilnfhdoflbpgamdcdgpehopbep`, update it in:
   - `waybar/.config/waybar/scripts/calendar-app.sh` (`APP_ID`)
   - `hypr/.config/hypr/rules.lua` (float/center/size rule for the Calendar window)
   - `hypr/.config/hypr/bindings.lua` (`floatSizes`, used by SUPER+V)

The window opens floating, centered, 1440×900. Only one window exists at a time: right-click focuses it if it's already open.

#### 9. Enable the module and restart waybar

`config.jsonc` already includes `modules/custom/clock.json` and uses `custom/clock` in `modules-center`. Restart waybar:

```bash
pkill waybar; waybar & disown
systemctl --user restart waybar.service
```

### Settings

Constants at the top of `scripts/custom-clock.py`:

| Constant                     | Default     | Meaning                                                                   |
| ---------------------------- | ----------- | ------------------------------------------------------------------------- |
| `FETCH_INTERVAL`             | `900`       | Seconds between fetches                                                   |
| `FETCH_DAYS`                 | `8`         | Look-ahead for reminders (tooltip shows 2 days)                           |
| `TOOLTIP_WIDTH`              | `66`        | Max line width in chars. GTK wraps tooltips at ~70, which breaks the grid |
| `YEAR_COLUMNS`               | `3`         | Months per row in the year view (4 would wrap)                            |
| `MAX_DAY_EVENTS`             | `6`         | Events per day before `+N more`                                           |
| `SOON_MINUTES`               | `10`        | When the bar turns blue (`#custom-clock.soon` in `style.css`)             |
| `COUNTDOWN_MINUTES`          | `60`        | When the next event shows `· in Nm`                                       |
| `BAR_BOTTOM`, `MODULE_REACH` | `40`, `80`  | Pixels: when the year view closes (assumes a **top** bar)                 |
| `TODAY_COLOR`                | `FireBrick` | Today in the grid                                                         |

### Troubleshooting

| Tooltip / symptom                 | Cause                                            | Fix                                                             |
| --------------------------------- | ------------------------------------------------ | --------------------------------------------------------------- |
| `⚠ gws login expired`             | Token expired (Testing mode: ~7 days) or revoked | Run the login from step 7                                       |
| `⚠ gws not installed`             | `gws` not in `PATH`                              | Step 1                                                          |
| `(stale, HH:MM)`                  | Last fetch failed, showing cached events         | Check network; see waybar log                                   |
| `⚠ gws exit …` / `bad event data` | API error or unexpected response                 | Full message in waybar's stderr (`custom-clock:` prefix)        |
| Stuck on `loading…`               | First fetch still running or hanging             | Middle-click; run the `gws` check from step 7                   |
| Tooltip lines wrap                | Line wider than GTK's limit                      | Lower `TOOLTIP_WIDTH`                                           |
| No notifications                  | swaync DND on, or event has no popup reminder    | Check DND; reminders on all-day events must be set on the event |
| Right-click opens nothing         | Wrong app id                                     | Step 8                                                          |

Test the script on its own (prints JSON lines, Ctrl+C to stop):

```bash
~/.config/waybar/scripts/custom-clock.py
```

### Security

- `~/.config/gws/` (client secret + encrypted tokens) must never be committed. `.gitignore` has `**/.config/gws/` as a guard, and it isn't part of any stow package.
- The login is read-only (`calendar.readonly`); the script can't change your calendar.

### Limitations

- Primary calendar only. No Google Tasks.
- All-day events that use the calendar's _default_ reminders don't notify (the API doesn't expose all-day defaults). Reminders set on the event itself work.
- The year view auto-close and `calendar-app.sh` rely on Hyprland (`hyprctl`). Elsewhere, the year view closes after 60 s instead.
- If waybar runs on several monitors, each bar runs its own script, and notifications are duplicated.
