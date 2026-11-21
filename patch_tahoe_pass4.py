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
backup = config_path.with_name(f"{config_path.name}.bak_pass4_{ts}")
shutil.copy2(config_path, backup)
print(f"[BACKUP] {backup}")

with config_path.open("rb") as f:
    plist = plistlib.load(f)

# 1. Disable SecureBootModel during macOS installer personalization (standard OpenCore requirement)
plist["Misc"]["Security"]["SecureBootModel"] = "Disabled"
plist["Misc"]["Security"]["DmgLoading"] = "Any"

# 2. Enforce ALL Pass 2 + Pass 3B invariants
plist["Kernel"]["Quirks"]["SetApfsTrimTimeout"] = -1
for kext in plist["Kernel"]["Add"]:
    if kext.get("BundlePath") in ("WhateverGreen.kext", "AMFIPass.kext"):
        kext["MaxKernel"] = "24.99.99"

has_tb_block = any(
    b.get("Identifier") == "com.apple.driver.AppleThunderboltNHI" and b.get("Enabled")
    for b in plist["Kernel"]["Block"]
)
if not has_tb_block:
    sys.exit("ERROR: AppleThunderboltNHI block missing! Aborting.")

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print("[DONE] Pass 4 config ready: SecureBootModel=Disabled, DmgLoading=Any, Pass 2/3B invariants verified")
