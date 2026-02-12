#!/bin/bash
# Sample script with some issues for review

echo "Starting deployment..."

# Dangerous: running as root without checking
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

# Dangerous: recursive delete variables
rm -rf $DIR/

# Hardcoded secret
API_KEY="12345-secret-key"

# Installing packages without update
apt-get install -y nginx

echo "Done."
