#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VS="$SCRIPT_DIR/voltageshift"

for _ in {1..60}; do
    "$VS" write 0x1A2 0x01640000
    sleep 1
done
