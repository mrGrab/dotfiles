local terminal = "kitty"
local fileManager = "nautilus --new-window"
local menu = "pkill -x wofi || wofi --show drun"
local mainMod = "SUPER"

hl.bind(mainMod .. " + grave", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + C", hl.dsp.window.close())
hl.bind(mainMod .. " + M", hl.dsp.exit())
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + V", function()
    local window = hl.get_active_window()
    if window == nil then
        return
    end

    if window.floating then
        hl.dispatch(hl.dsp.window.float({ action = "unset", window = window }))
        return
    end

    local monitor = hl.get_active_monitor()
    hl.dispatch(hl.dsp.window.float({ action = "set", window = window }))

    if monitor ~= nil then
        hl.dispatch(hl.dsp.window.resize({
            x = math.floor(monitor.width * 0.97),
            y = math.floor(monitor.height * 0.97),
            window = window,
        }))
        hl.dispatch(hl.dsp.window.center({ window = window }))
    end
end)
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + SHIFT + V",
    hl.dsp.exec_cmd("cliphist list | wofi --conf $HOME/.config/wofi/clipboard | cliphist decode | wl-copy"))
hl.bind(mainMod .. " + SHIFT + DELETE",
    hl.dsp.exec_cmd("cliphist list | wofi --conf $HOME/.config/wofi/clipboard | cliphist delete"))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu))
-- hl.bind(mainMod .. " + SPACE", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))

for key, direction in pairs({ left = "left", right = "right", up = "up", down = "down" }) do
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ direction = direction }))
end

for workspace = 1, 10 do
    local key = workspace % 10
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = workspace }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = workspace }))
end

hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))
hl.bind(mainMod .. " + SHIFT + left", hl.dsp.workspace.move({ monitor = "l" }))
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.workspace.move({ monitor = "r" }))
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

local volumeBinds = {
    { "XF86AudioRaiseVolume",  "wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+" },
    { "XF86AudioLowerVolume",  "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-" },
    { "XF86AudioMute",         "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle" },
    { "XF86AudioMicMute",      "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle" },
    { "XF86MonBrightnessUp",   "brightnessctl -e4 -n2 set 5%+" },
    { "XF86MonBrightnessDown", "brightnessctl -e4 -n2 set 5%-" },
}
for _, bind in ipairs(volumeBinds) do
    hl.bind(bind[1], hl.dsp.exec_cmd(bind[2]), { locked = true, repeating = true })
end

for _, bind in ipairs({
    { "XF86AudioNext",  "playerctl next" },
    { "XF86AudioPause", "playerctl play-pause" },
    { "XF86AudioPlay",  "playerctl play-pause" },
    { "XF86AudioPrev",  "playerctl previous" },
}) do
    hl.bind(bind[1], hl.dsp.exec_cmd(bind[2]), { locked = true })
end

local snapshot =
'hyprshot --output-folder $HOME/Pictures/Snapshots --filename Snapshot_$(date +"%Y-%m-%d_%H-%M-%S").png --mode '
hl.bind("ALT + SHIFT + 3", hl.dsp.exec_cmd(snapshot .. "region"))
hl.bind("ALT + SHIFT + 4", hl.dsp.exec_cmd(snapshot .. "window"))
hl.bind("ALT + SHIFT + 5", hl.dsp.exec_cmd(snapshot .. "output"))
hl.bind(mainMod .. " + i", hl.dsp.exec_cmd("swaync-client -t -sw"))
hl.bind(mainMod .. " + t", hl.dsp.exec_cmd("$HOME/bin/translate.sh"))
hl.bind("ALT + TAB", hl.dsp.window.swap({ next = true }))
