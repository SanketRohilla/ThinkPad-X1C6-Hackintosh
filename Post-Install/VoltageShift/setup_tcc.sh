#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VS="$SCRIPT_DIR/voltageshift"

while true; do
    "$VS" write 0x1A2 0x01640000
    sleep 5
done
