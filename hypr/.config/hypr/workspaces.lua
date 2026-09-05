local workspaces = {
    { workspace = "1",  monitor = "DP-1", default = true, persistent = true, gaps_out = 2 },
    { workspace = "3",  monitor = "DP-1", gaps_out = 2 },
    { workspace = "5",  monitor = "DP-1", gaps_out = 2 },
    { workspace = "7",  monitor = "DP-1", gaps_out = 2 },
    { workspace = "9",  monitor = "DP-1", gaps_out = 2 },
    { workspace = "2",  monitor = "DP-3", default = true, persistent = true, gaps_out = 2 },
    { workspace = "4",  monitor = "DP-3", gaps_out = 2 },
    { workspace = "6",  monitor = "DP-3", gaps_out = 2 },
    { workspace = "8",  monitor = "DP-3", gaps_out = 2 },
    { workspace = "10", monitor = "DP-3", gaps_out = 2 },
}

for _, workspace in ipairs(workspaces) do
    hl.workspace_rule(workspace)
end
