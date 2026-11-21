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

# 1. Core Quirks
plist["Kernel"]["Quirks"]["DisableLinkeditJettison"] = True
plist["Kernel"]["Quirks"]["SetApfsTrimTimeout"] = -1
plist["Kernel"]["Quirks"]["ExtendBTFeatureFlags"] = True

# 2. Kext rules
CAP_SEQUOIA_ONLY = {
    "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Mouse.kext",
    "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Trackpad.kext",
    "YogaSMC.kext",
    "AMFIPass.kext",
    "Sinetek-rtsx.kext",
}
ENABLE_ON_TAHOE = {
    "VoodooPS2Controller.kext",
    "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Keyboard.kext",
    "VoodooSMBus.kext",
    "VoodooRMI.kext",
    "VoodooRMI.kext/Contents/PlugIns/VoodooInput.kext",
    "VoodooRMI.kext/Contents/PlugIns/RMISMBus.kext",
    "IntelBluetoothFirmware.kext",
    "BlueToolFixup.kext",
    "AppleALC.kext",
}

new_add = []
for kext in plist["Kernel"]["Add"]:
    bp = kext.get("BundlePath")
    if bp == "SimpleHDA.kext":
        continue
    if bp == "IntelBTPatcher.kext":
        kext["Enabled"] = False
    elif bp in CAP_SEQUOIA_ONLY:
        kext["MaxKernel"] = "24.99.99"
    elif bp in ENABLE_ON_TAHOE:
        kext["Enabled"] = True
        kext["MaxKernel"] = ""

    new_add.append(kext)
    if bp == "AppleALC.kext":
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

plist["Kernel"]["Add"] = new_add

# 3. Clean debug bloat from boot-args & add shda-lang=en
guid = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
drop_args = {"msgbuf=1048576", "debug=0x100", "-v", "io=0x80", "-igfxvesa"}
clean_args = [a for a in plist["NVRAM"]["Add"][guid]["boot-args"].split() if a not in drop_args and not a.startswith("shda-lang=")]
clean_args.append("shda-lang=en")
plist["NVRAM"]["Add"][guid]["boot-args"] = " ".join(clean_args)

# 4. Disable heavy EFI disk debug logging
plist["Misc"]["Debug"]["AppleDebug"] = False
plist["Misc"]["Debug"]["ApplePanic"] = False
plist["Misc"]["Debug"]["DisableWatchDog"] = False
plist["Misc"]["Debug"]["Target"] = 0

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print("[DONE] Pass 7 applied: Keyboard fixed, SimpleHDA + Intel Bluetooth enabled, debug overhead removed")
