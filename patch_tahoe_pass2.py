#!/usr/bin/env python3
import plistlib
import sys
from pathlib import Path

config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("EFI/OC/config.plist")

with config_path.open("rb") as f:
    plist = plistlib.load(f)

# 1. Add io=0x80 for full IOKit driver visibility
guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
boot_args = plist["NVRAM"]["Add"][guid]["boot-args"]
if "io=0x80" not in boot_args.split():
    # Insert io=0x80 after debug=0x100 if present, else append
    args_list = boot_args.split()
    if "debug=0x100" in args_list:
        idx = args_list.index("debug=0x100") + 1
        args_list.insert(idx, "io=0x80")
        plist["NVRAM"]["Add"][guid]["boot-args"] = " ".join(args_list)
    else:
        plist["NVRAM"]["Add"][guid]["boot-args"] = f"{boot_args} io=0x80"

# 2. Disable OpenCore APFS TRIM binary patch completely
plist["Kernel"]["Quirks"]["SetApfsTrimTimeout"] = -1

# 3. Temporarily cap WhateverGreen.kext to Darwin <= 24 (Sequoia) to isolate WEG/iGPU lockup
for kext in plist["Kernel"]["Add"]:
    if kext.get("BundlePath") == "WhateverGreen.kext":
        kext["MaxKernel"] = "24.99.99"
        break

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print("[DONE] Applied Pass 2 (io=0x80, SetApfsTrimTimeout=-1, WhateverGreen MaxKernel=24.99.99)")
