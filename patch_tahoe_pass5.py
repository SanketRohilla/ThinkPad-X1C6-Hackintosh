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
backup = config_path.with_name(f"{config_path.name}.bak_pass5_{ts}")
shutil.copy2(config_path, backup)
print(f"[BACKUP] {backup}")

with config_path.open("rb") as f:
    plist = plistlib.load(f)

# 1. Re-enable WhateverGreen.kext on Darwin 25+ (Tahoe)
for kext in plist["Kernel"]["Add"]:
    if kext.get("BundlePath") == "WhateverGreen.kext":
        kext["MaxKernel"] = ""
        print("[Kernel->Add] Set WhateverGreen.kext MaxKernel = ''")
    elif kext.get("BundlePath") == "AMFIPass.kext":
        kext["MaxKernel"] = "24.99.99"

# 2. Remove -igfxvesa and io=0x80 from boot-args so Intel UHD 620 / WindowServer initializes
guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
args = plist["NVRAM"]["Add"][guid]["boot-args"].split()
cleaned_args = [a for a in args if a not in ("-igfxvesa", "io=0x80")]
plist["NVRAM"]["Add"][guid]["boot-args"] = " ".join(cleaned_args)
print(f"[NVRAM->Add] Updated boot-args:\n  {plist['NVRAM']['Add'][guid]['boot-args']}")

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print("[DONE] Pass 5 applied: WhateverGreen enabled for Tahoe, -igfxvesa removed")
