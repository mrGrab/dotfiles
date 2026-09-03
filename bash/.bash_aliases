#!/usr/bin/env bash

# My Kubernetes Utility Wrapper
function k8s {
    case "$1" in
    "cluster")
        if [ "$2" == "list" ]; then
            kubectl config get-clusters
        elif [ "$2" == "set" ] && [ -n "$3" ]; then
            kubectl config use-context "$3"
        else
            echo "Usage: k8s cluster {list|set <context>}"
        fi
        ;;
    "pod")
        if [ "$2" == "ssh" ] && [ -n "$3" ]; then
            local container_flag=""
            [ -n "$4" ] && container_flag="-c $4"
            kubectl exec --stdin --tty "$3" ${container_flag} -- sh -c "(bash || sh)"
        else
            echo "Usage: k8s pod ssh <pod-name> [container-name]"
        fi
        ;;
    "namespace")
        if [ "$2" == "set" ] && [ -n "$3" ]; then
            kubectl config set-context --current --namespace="$3"
        else
            echo "Usage: k8s namespace set <namespace>"
        fi
        ;;
    *)
        echo "Usage: k8s {cluster|pod|namespace}"
        ;;
    esac
}

function _k8s_completions {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD - 1]}"
    opts="cluster pod namespace"

    case "${prev}" in
    "k8s")
        COMPREPLY=($(compgen -W "${opts}" -- "${cur}"))
        return 0
        ;;
    "cluster")
        COMPREPLY=($(compgen -W "list set" -- "${cur}"))
        return 0
        ;;
    "pod")
        COMPREPLY=($(compgen -W "ssh" -- "${cur}"))
        return 0
        ;;
    "namespace")
        COMPREPLY=($(compgen -W "set" -- "${cur}"))
        return 0
        ;;
    *)
        # Optional dynamic completions for values following set/ssh
        local subcmd="${COMP_WORDS[COMP_CWORD - 2]}"
        if [ "${subcmd}" == "cluster" ] && [ "${prev}" == "set" ]; then
            local contexts
            contexts=$(kubectl config get-contexts -o name 2>/dev/null)
            COMPREPLY=($(compgen -W "${contexts}" -- "${cur}"))
            return 0
        elif [ "${subcmd}" == "namespace" ] && [ "${prev}" == "set" ]; then
            local namespaces
            namespaces=$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
            COMPREPLY=($(compgen -W "${namespaces}" -- "${cur}"))
            return 0
        fi
        return 0
        ;;
    esac
}

complete -F _k8s_completions k8s
