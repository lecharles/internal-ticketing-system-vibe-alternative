#!/bin/bash

# Exit on error
set -e

echo "Starting monitoring of test environment..."

# Monitor log files
tail -f logs/internal_jira.log /var/log/nginx/internal-jira.{access,error}.log | while read line; do
    # Highlight errors in red
    if echo "$line" | grep -i "error" > /dev/null; then
        echo -e "\e[91m$line\e[0m"
    # Highlight warnings in yellow
    elif echo "$line" | grep -i "warning" > /dev/null; then
        echo -e "\e[93m$line\e[0m"
    # Show other lines in normal color
    else
        echo "$line"
    fi
done 