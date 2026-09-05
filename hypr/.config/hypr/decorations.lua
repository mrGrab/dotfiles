hl.config({
    general = {
        gaps_in = 5,
        border_size = 1,
        col = {
            active_border = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
            inactive_border = "rgba(595959aa)",
        },
        resize_on_border = true,
        allow_tearing = false,
        layout = "master",
    },
    decoration = {
        rounding = 9,
        rounding_power = 2,

        active_opacity = 1,
        inactive_opacity = 0.95,

        dim_inactive = true,
        dim_strength = 0.01,
        shadow = {
            enabled = true,
            range = 4,
            render_power = 3,
            color = 0xee1a1a1a,
        },
        blur = {
            enabled = false,
            size = 3,
            passes = 1,
            vibrancy = 0.1696,
            special = false
        },
    },
    dwindle = { preserve_split = true },
    master = {
        new_status = "master",
        orientation = "right",
        mfact = 0.60,
        new_on_top = false,
        focus_master_on_close = true
    },
    misc = {
        force_default_wallpaper = 0,
        animate_manual_resizes = true,
        disable_hyprland_logo = true,
        middle_click_paste = true,
        disable_autoreload = false
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
    cursor = {
        invisible = false,
        inactive_timeout = 10
    },
    ecosystem = {
        no_update_news = true,
        no_donation_nag = true
    }
})
