#!/bin/bash
# ThinkPad X1 Carbon 6th Gen - VoltageShift Undervolt & TDP Unlock
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VS="$SCRIPT_DIR/voltageshift"

if [ ! -x "$VS" ]; then
    echo "[-] voltageshift binary not found at $VS"
    exit 1
fi

"$VS" offset -80 0 -50 0 0
"$VS" power 16 26
"$VS" write 0x1A2 0x01640000
echo "[OK] VoltageShift undervolt (-80mV CPU / -50mV cache) and 16W/26W TDP applied."
