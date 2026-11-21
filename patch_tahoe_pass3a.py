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
backup = config_path.with_name(f"{config_path.name}.bak_pass3a_{ts}")
shutil.copy2(config_path, backup)
print(f"[BACKUP] {backup}")

with config_path.open("rb") as f:
    plist = plistlib.load(f)

# 1. Pass 3A changes: enable j152f SecureBootModel (supported in BOTH Tahoe & Sequoia Preboot)
plist["Misc"]["Security"]["SecureBootModel"] = "j152f"
plist["Misc"]["Security"]["DmgLoading"] = "Signed"

# 2. Enforce Pass 2 invariants so nothing regresses
plist["Kernel"]["Quirks"]["SetApfsTrimTimeout"] = -1
for kext in plist["Kernel"]["Add"]:
    if kext.get("BundlePath") in ("WhateverGreen.kext", "AMFIPass.kext"):
        kext["MaxKernel"] = "24.99.99"

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print("[DONE] Pass 3A applied: SecureBootModel=j152f, DmgLoading=Signed")
