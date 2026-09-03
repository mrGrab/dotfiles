#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# --- History Configuration ---
shopt -s histappend # allow multiple terminals to write to the history file
HISTCONTROL=ignoredups:erasedups
HISTSIZE=10000
HISTFILESIZE=20000

# --- Aliases ---
alias ls='ls --color=auto'
alias ll='ls -lFhtr'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias pacman='pacman --color always'
alias sudo='sudo '

if [ -f ~/.bash_aliases ]; then
    source ~/.bash_aliases
fi

# Add some colour to LESS/MAN pages
export LESS_TERMCAP_mb=$'\E[01;31m'
export LESS_TERMCAP_md=$'\E[01;33m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;42;30m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[01;36m'

# --- PATH Management ---
# Helper function to prepend/append paths cleanly without duplicates
path_append() {
    [[ -d "$1" ]] && [[ ":$PATH:" != *":$1:"* ]] && PATH="${PATH}:${1}"
}

path_append "${HOME}/.local/bin"
path_append "${HOME}/ProgramFiles/azure-functions-cli"
path_append "${HOME}/bin"

# --- Prompt (PS1) ---
PS1="[\[$(tput sgr0)\]\[$(tput bold)\]\[\033[38;5;2m\]\u\[$(tput sgr0)\]: \[$(tput sgr0)\]\[\033[38;5;6m\]\w\[$(tput sgr0)\]]\\$ \[$(tput sgr0)\]"

# --- OS & Homebrew Configuration (Cross-Platform) ---
ARCH="$(uname -m)"
brew_path=""

if [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ "$ARCH" == "arm64" ]]; then
        brew_path="/opt/homebrew"
    else
        brew_path="/usr/local"
    fi
elif [[ -d "/home/linuxbrew/.linuxbrew" ]]; then
    brew_path="/home/linuxbrew/.linuxbrew"
fi

# Apply macOS/Homebrew-specific paths and flags if brew_path is valid
if [[ -n "$brew_path" ]] && [[ -x "${brew_path}/bin/brew" ]]; then
    eval "$("${brew_path}/bin/brew" shellenv)"

    if [[ "$ARCH" == "arm64" ]] && command -v terraform &>/dev/null; then
        complete -C "${brew_path}/bin/terraform" terraform
    fi

    path_append "${brew_path}/opt/libpq/bin"
    path_append "${brew_path}/opt/python@3/libexec/bin"
    path_append "/usr/local/go/bin"
    path_append "${brew_path}/opt/mysql-client@8.4/bin"
    path_append "${brew_path}/opt/grep/libexec/gnubin"
    path_append "${brew_path}/opt/gnu-sed/libexec/gnubin"

    export LDFLAGS="-L${brew_path}/opt/libpq/lib"
    export CPPFLAGS="-I${brew_path}/opt/libpq/include"

    # Completion
    export BASH_COMPLETION_COMPAT_DIR="${brew_path}/etc/bash_completion.d"
    if [[ -r "${brew_path}/etc/profile.d/bash_completion.sh" ]]; then
        source "${brew_path}/etc/profile.d/bash_completion.sh"
    fi

    if [[ -d "${brew_path}/etc/bash_completion.d" ]]; then
        for i in "${brew_path}/etc/bash_completion.d/"*; do
            [[ -r "$i" ]] && source "$i"
        done
    fi
fi
