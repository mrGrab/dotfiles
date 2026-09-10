local function rule(config)
    hl.window_rule(config)
end

rule({
    name = "windowrule-1",
    suppress_event = "maximize",
    match = { class = ".*" },
})

rule({
    name = "windowrule-2",
    no_focus = true,
    match = {
        class = "^$",
        title = "^$",
        xwayland = true,
        float = true,
        fullscreen = false,
        pin = false,
    },
})

rule({ name = "windowrule-3", animation = "popin", match = { class = "kitty" } })

hl.layer_rule({ name = "layerrule-1", blur = true, animation = "slide right", ignore_alpha = 0, match = { namespace = "swaync-control-center" } })
hl.layer_rule({ name = "layerrule-2", ignore_alpha = 0, match = { namespace = "swaync-notification-window" } })

rule({ name = "windowrule-4", opacity = "0.95 0.85", match = { class = "^(org.gnome.Nautilus)$" } })
rule({ name = "windowrule-5", float = true, center = true, size = { 875, 600 }, match = { tag = "floating-window" } })
rule({ name = "windowrule-6", tag = "+floating-window", match = { class = "(blueman-manager|xdg-desktop-portal-gtk|About|TUI.float)" } })
rule({
    name = "windowrule-7",
    tag = "+floating-window",
    match = {
        class = "(xdg-desktop-portal-gtk|sublime_text|DesktopEditors|org.gnome.Nautilus|dev\\.zed\\.Zed)",
        title =
        "^(Open.*Files?|Open [Ff]older.*|Save.*Files?|Save.*As|Save|All Files|.*wants to (open|save).*|[Cc]hoose.*|.* — [Ss]ettings)",
    },
})
rule({ name = "windowrule-8", float = true, center = true, match = { class = "org.gnome.Calculator" } })
rule({ name = "windowrule-10", opacity = "1 1", match = { class = "^(zoom|vlc|mpv|imv|org.gnome.NautilusPreviewer)$" } })
rule({ name = "windowrule-11", rounding = 8, match = { tag = "pop" } })
rule({ name = "windowrule-12", tag = "+terminal", match = { class = "(Alacritty|kitty|com.mitchellh.ghostty)" } })
rule({ name = "windowrule-13", no_initial_focus = true, match = { class = "(Zoom Workplace)", initial_title = "(menu window)" } })
rule({ name = "windowrule-14", move = { "cursor_x-(window_w*0.5)", "cursor_y-(window_h*0.5)" }, match = { class = "(Zoom Workplace)", initial_title = "(sub menu window)" } })
rule({ name = "windowrule-15", float = true, size = { 1600, 900 }, center = true, match = { class = "^(blender)$" } })
rule({ name = "windowrule-16", float = true, center = true, match = { class = "^(org\\.pulseaudio\\.pavucontrol|pavucontrol)$" } })
rule({
    name = "windowrule-18",
    float = true,
    center = true,
    size = { 1100, 800 },
    match = {
        class = "^(md\\.obsidian\\.Obsidian)$",
        initial_title = "^(Settings - .* - Obsidian .*)$",
    },
})
rule({
    name = "windowrule-17",
    float = true,
    center = true,
    size = { 1440, 918 },
    suppress_event = "maximize fullscreen",
    match = {
        class = "^(org\\.telegram\\.desktop)$",
        initial_title = "^(Media viewer)$",
    },
})
