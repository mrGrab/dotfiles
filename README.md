# Dotfiles

Personal configuration files managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Overview

This repository uses a standard GNU Stow structure where each directory corresponds to a package (e.g., `kitty`, `ghostty`, `zed`). \
Symlinks are created directly into the target directory (defaulting to `~`).

```text
~/dotfiles/
├── kitty/
│   └── .config/
│       └── kitty/
│           └── kitty.conf
├── ghostty/
│   └── .config/
│       └── ghostty/
│           └── config
└── zed/
    └── .config/
        └── zed/
            └── settings.json
```

## Usage

### Deploy Configurations

Use `stow` with the `-t ~ flag` to target your home directory:

```bash
# Deploy individual configurations
stow -t ~ kitty
stow -t ~ ghostty
stow -t ~ zed

# Restow (useful to update symlinks after changing repository structure)
stow -R -t ~ kitty

# Remove symlinks (un-stow)
stow -D -t ~ kitty
```

> [!NOTE]
>If an existing non-symlinked file already exists in `~/.config/<package>`, stow will refuse to overwrite it to prevent data loss. Move or back up the target file first.

### How to Import an Existing Config

```bash
mkdir -p ~/dotfiles/hypr/.config
mv ~/.config/hypr ~/dotfiles/hypr/.config/
cd ~/dotfiles
stow -t ~ hypr

# Confirm it is now a symlink pointing to ~/dotfiles
ls -la ~/.config/hypr
```
