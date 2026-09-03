#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias ll='ls -lFhtr'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias pacman='pacman --color always'
alias sudo='sudo '


PATH="${PATH}:${HOME}/.local/bin"
if [ -d "${HOME}/ProgramFiles/azure-functions-cli" ] ; then
    PATH="${PATH}:${HOME}/ProgramFiles/azure-functions-cli"
fi
if [ -d "${HOME}/bin" ] ; then
    PATH="${PATH}:${HOME}/bin"
fi

#PS1='[\u@\h \W]\$ '
PS1="[\[$(tput sgr0)\]\[$(tput bold)\]\[\033[38;5;2m\]\u\[$(tput sgr0)\]: \[$(tput sgr0)\]\[\033[38;5;6m\]\w\[$(tput sgr0)\]]\\$ \[$(tput sgr0)\]"

