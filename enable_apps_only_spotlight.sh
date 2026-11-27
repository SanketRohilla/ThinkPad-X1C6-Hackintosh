#!/bin/bash
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo: sudo bash $0"
    exit 1
fi

echo "[*] Keeping extra/Windows volumes excluded from Spotlight..."
for vol in "/Volumes/Untitled" "/Volumes/Macintosh HD" "/Volumes/Macintosh HD - Data"; do
    if [ -d "$vol" ]; then
        mdutil -i off "$vol" >/dev/null 2>&1 || true
    fi
done

echo "[*] Enabling Spotlight indexing on / and /System/Volumes/Data..."
mdutil -i on / /System/Volumes/Data

VOL_CFG="/System/Volumes/Data/.Spotlight-V100/VolumeConfiguration.plist"
for _ in $(seq 1 10); do
    if [ -f "$VOL_CFG" ]; then
        break
    fi
    sleep 1
done

if [ -f "$VOL_CFG" ]; then
    echo "[*] Restricting Spotlight to /Applications and /System/Applications (excluding user/system data)..."
    python3 - "$VOL_CFG" <<'PY'
import plistlib
import sys
from pathlib import Path

cfg_path = Path(sys.argv[1])
with cfg_path.open("rb") as f:
    data = plistlib.load(f)

exclusions = list(data.get("Exclusions", []))
targets = [
    "/Users",
    "/Library",
    "/private",
    "/usr",
    "/opt",
    "/cores",
    "/System/Volumes/Data/Users",
    "/System/Volumes/Data/Library",
    "/System/Volumes/Data/private",
    "/System/Volumes/Data/Previous Content",
    "/System/Volumes/Data/MobileSoftwareUpdate",
    "/System/Volumes/Data/usr",
    "/System/Volumes/Data/opt",
    "/System/Volumes/Data/cores",
    "/System/Volumes/Data/sw",
    "/System/Volumes/Data/pkg",
    "/System/Volumes/Data/Volumes",
]
for item in targets:
    if item not in exclusions:
        exclusions.append(item)

data["Exclusions"] = exclusions
with cfg_path.open("wb") as f:
    plistlib.dump(data, f)
print(f"[OK] Saved {len(exclusions)} Spotlight exclusions to {cfg_path}")
PY
else
    echo "[!] Warning: $VOL_CFG not found yet. Re-run after indexing initializes."
fi

echo "[*] Reloading Spotlight daemons and importing Applications..."
killall mds mds_stores 2>/dev/null || true
sleep 2
mdimport /Applications /System/Applications 2>/dev/null || true
mdutil -s / /System/Volumes/Data

echo "[OK] Spotlight enabled for Apps only."
