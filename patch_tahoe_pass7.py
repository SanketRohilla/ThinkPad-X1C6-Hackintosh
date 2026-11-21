#!/usr/bin/env python3
import plistlib, shutil, sys
from datetime import datetime
from pathlib import Path

config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("EFI/OC/config.plist")
if not config_path.is_file():
    sys.exit(f"ERROR: Not found: {config_path}")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = config_path.with_name(f"{config_path.name}.bak_pass7_{ts}")
shutil.copy2(config_path, backup)
print(f"[BACKUP] {backup}")

with config_path.open("rb") as f:
    plist = plistlib.load(f)

# 1. Enforce kernel quirks required for SimpleHDA & Toshiba NVMe
plist["Kernel"]["Quirks"]["DisableLinkeditJettison"] = True
plist["Kernel"]["Quirks"]["SetApfsTrimTimeout"] = -1
plist["Kernel"]["Quirks"]["ExtendBTFeatureFlags"] = True

# 2. Rebuild Kernel -> Add cleanly:
#    - Insert SimpleHDA.kext right after AppleALC.kext (MinKernel=25.0.0)
#    - Enable IntelBluetoothFirmware.kext, IntelBTPatcher.kext, and BlueToolFixup.kext on Tahoe
new_add = []
for kext in plist["Kernel"]["Add"]:
    bp = kext.get("BundlePath")
    if bp == "SimpleHDA.kext":
        continue
    if bp in ("IntelBluetoothFirmware.kext", "IntelBTPatcher.kext", "BlueToolFixup.kext"):
        kext["Enabled"] = True
        kext["MaxKernel"] = ""
    if bp == "AppleALC.kext":
        kext["Enabled"] = True
        kext["MaxKernel"] = ""
        new_add.append(kext)
        new_add.append({
            "Arch": "x86_64",
            "BundlePath": "SimpleHDA.kext",
            "Comment": "Restore native AppleHDA stack on macOS Tahoe 26+",
            "Enabled": True,
            "ExecutablePath": "Contents/MacOS/SimpleHDA",
            "MaxKernel": "",
            "MinKernel": "25.0.0",
            "PlistPath": "Contents/Info.plist",
        })
        continue
    new_add.append(kext)

plist["Kernel"]["Add"] = new_add

# 3. Strip debug logging bloat (msgbuf=1048576, debug=0x100, -v) that slows Tahoe & add shda-lang=en
guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
drop_args = {"msgbuf=1048576", "debug=0x100", "-v", "io=0x80", "-igfxvesa"}
clean_args = [a for a in plist["NVRAM"]["Add"][guid]["boot-args"].split() if a not in drop_args and not a.startswith("shda-lang=")]
clean_args.append("shda-lang=en")
plist["NVRAM"]["Add"][guid]["boot-args"] = " ".join(clean_args)

# 4. Disable heavy EFI disk debug logging (Target=67 writes every log line to disk)
plist["Misc"]["Debug"]["AppleDebug"] = False
plist["Misc"]["Debug"]["ApplePanic"] = False
plist["Misc"]["Debug"]["DisableWatchDog"] = False
plist["Misc"]["Debug"]["Target"] = 0

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print("[DONE] Pass 7 applied: SimpleHDA + Intel Bluetooth enabled, debug bloat removed")
