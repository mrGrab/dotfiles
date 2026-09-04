require("autostart")
require("bindings")
require("workspaces")
require("rules")

hl.monitor({ output = "DP-1", mode = "1920x1080@270", position = "0x0", scale = 1 })
hl.monitor({ output = "DP-3", mode = "1920x1080@270", position = "1920x0", scale = 1 })
hl.env("HYPRCURSOR_SIZE", "24")

hl.config({
    general = {
        gaps_in = 2,
        gaps_out = 0,
        border_size = 1,
        col = {
            active_border = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
            inactive_border = "rgba(595959aa)",
        },
        resize_on_border = true,
        allow_tearing = false,
        layout = "dwindle",
    },
    decoration = {
        rounding = 10,
        rounding_power = 2,
        active_opacity = 1.0,
        inactive_opacity = 0.95,
        shadow = {
            enabled = true,
            range = 4,
            render_power = 3,
            color = 0xee1a1a1a,
        },
        blur = {
            enabled = true,
            size = 3,
            passes = 1,
            vibrancy = 0.1696,
        },
    },
    dwindle = { preserve_split = true },
    master = { new_status = "master" },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo = true,
        middle_click_paste = true,
    },
    input = {
        kb_layout = "us,ua",
        kb_variant = "",
        kb_model = "",
        kb_options = "grp:alt_space_toggle",
        kb_rules = "",
        numlock_by_default = true,
        follow_mouse = 2,
        sensitivity = 0,
        touchpad = { natural_scroll = false },
    },
})

local curves = {
    { "easeOutQuint",   { 0.23, 1 },    { 0.32, 1 } },
    { "easeInOutCubic", { 0.65, 0.05 }, { 0.36, 1 } },
    { "linear",         { 0, 0 },       { 1, 1 } },
    { "almostLinear",   { 0.5, 0.5 },   { 0.75, 1 } },
    { "quick",          { 0.15, 0 },    { 0.1, 1 } },
}
for _, curve in ipairs(curves) do
    hl.curve(curve[1], { type = "bezier", points = { curve[2], curve[3] } })
end

local animations = {
    { "global",              10,   "default",      nil },
    { "border",              5.39, "easeOutQuint", nil },
    { "windows",             4.79, "easeOutQuint", nil },
    { "windowsIn",           4.1,  "easeOutQuint", "popin 87%" },
    { "windowsOut",          1.49, "linear",       "popin 87%" },
    { "fadeIn",              1.73, "almostLinear", nil },
    { "fadeOut",             1.46, "almostLinear", nil },
    { "fade",                3.03, "quick",        nil },
    { "layers",              3.81, "easeOutQuint", nil },
    { "layersIn",            4,    "easeOutQuint", "fade" },
    { "layersOut",           1.5,  "linear",       "fade" },
    { "fadeLayersIn",        1.79, "almostLinear", nil },
    { "fadeLayersOut",       1.39, "almostLinear", nil },
    { "workspaces",          1.94, "almostLinear", "slide 75%" },
    { "workspacesIn",        1.21, "almostLinear", "slide 75%" },
    { "workspacesOut",       1.94, "almostLinear", "slide 75%" },
    { "specialWorkspace",    1.94, "almostLinear", "fade" },
    { "specialWorkspaceIn",  1.21, "almostLinear", "fade" },
    { "specialWorkspaceOut", 1.94, "almostLinear", "fade" },
    { "zoomFactor",          7,    "quick",        nil },
}
for _, animation in ipairs(animations) do
    local config = { leaf = animation[1], enabled = true, speed = animation[2], bezier = animation[3] }
    if animation[4] then config.style = animation[4] end
    hl.animation(config)
end

hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
hl.config({ cursor = { no_hardware_cursors = true } })
