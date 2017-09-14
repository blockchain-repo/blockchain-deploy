#!/bin/sh

function echo_green
{
    local content=$@
    echo -e "\033[1;32m${content}\033[0m"
    return 0
}

function usage
{
    echo_green "
Usage:
    $0 [\$1]
Options:
    -h    usage help
    -b    grep with block id
    -t    grep with transaction id
    -g    get logs from remote nodes
    -c    clean tmp/remote_log/
    "
    return 0
}

function clean_logs
{
    rm -rf /tmp/remote_log/*
}

function get_logs
{
    fab get_logs
    echo "
    Log synchronization complete
    "
    return 0
}


function grep_block
{
    cd /tmp/remote_log
    if test -z $1
    then
        grep -r --color '' *
    else
        grep -r --color $1 *
    fi
    return 0
}

function grep_transaction
{
    cd /tmp/remote_log
    if test -z $1
    then
        grep -r --color '' *
    else
        grep -r --color $1 *
    fi
    return 0
}

case $1 in
    -h)
        usage
    ;;
    -b)
        grep_block $2
    ;;
    -t)
        grep_transaction $2
    ;;
    -g)
        get_logs
    ;;
    -c)
        clean_logs
    ;;
    *)
        usage
    ;;
esac

