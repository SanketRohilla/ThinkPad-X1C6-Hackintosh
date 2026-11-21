#!/usr/bin/env python3
import plistlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("EFI/OC/config.plist")
if not config_path.is_file():
    sys.exit(f"ERROR: Not found: {config_path}")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = config_path.with_name(f"{config_path.name}.bak_pass3b_{ts}")
shutil.copy2(config_path, backup)
print(f"[BACKUP] {backup}")

with config_path.open("rb") as f:
    plist = plistlib.load(f)

block_list = plist["Kernel"]["Block"]
target_id = "com.apple.driver.AppleThunderboltNHI"

# Remove any previous entry for this identifier to stay idempotent
block_list[:] = [b for b in block_list if b.get("Identifier") != target_id]

block_list.append({
    "Arch": "x86_64",
    "Comment": "Tahoe: block AppleThunderboltNHI to prevent 0xFFFFFFFF PCIe/DMA hard-lock",
    "Enabled": True,
    "Identifier": target_id,
    "MaxKernel": "",
    "MinKernel": "25.0.0",
    "Strategy": "Exclude",
})

# Enforce Pass 2 + Pass 3A invariants
plist["Misc"]["Security"]["SecureBootModel"] = "j152f"
plist["Misc"]["Security"]["DmgLoading"] = "Signed"
plist["Kernel"]["Quirks"]["SetApfsTrimTimeout"] = -1
for kext in plist["Kernel"]["Add"]:
    if kext.get("BundlePath") in ("WhateverGreen.kext", "AMFIPass.kext"):
        kext["MaxKernel"] = "24.99.99"

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print(f"[DONE] Pass 3B applied: Blocked {target_id} (MinKernel=25.0.0, Strategy=Exclude)")
