#!/usr/bin/env bash
set -euo pipefail

# App id comes from ~/.local/share/applications/chrome-<id>-Default.desktop

APP_ID="kjbdgfilnfhdoflbpgamdcdgpehopbep"
CLASS_RE="^(chrome-${APP_ID}-Default|crx_${APP_ID})$"

addr=$(hyprctl clients -j | jq -r --arg re "$CLASS_RE" \
    'first(.[] | select(.class | test($re)) | .address) // empty')

if [[ -n "$addr" ]]; then
    hyprctl dispatch "hl.dsp.focus({ window = \"address:${addr}\" })" >/dev/null
else
    setsid -f chromium --profile-directory=Default --app-id="$APP_ID" >/dev/null 2>&1
fi
