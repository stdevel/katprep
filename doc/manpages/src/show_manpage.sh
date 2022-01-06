#!/bin/sh
if [ -z "$1" ]; then
    echo "Use manpage source as parameter"
else
    pandoc "$1" -s -t man | man -l -
fi
