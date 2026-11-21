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
backup = config_path.with_name(f"{config_path.name}.bak_pass6_{ts}")
shutil.copy2(config_path, backup)
print(f"[BACKUP] {backup}")

KEXTS_TO_ENABLE_ON_TAHOE = {
    # Trackpad & TrackPoint
    "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Mouse.kext",
    "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Trackpad.kext",
    "VoodooSMBus.kext",
    "VoodooRMI.kext",
    "VoodooRMI.kext/Contents/PlugIns/VoodooInput.kext",
    "VoodooRMI.kext/Contents/PlugIns/RMISMBus.kext",
    # Battery, Sensors, Brightness & Power Management
    "SMCProcessor.kext",
    "SMCBatteryManager.kext",
    "SMCLightSensor.kext",
    "CPUFriend.kext",
    "CPUFriendDataProvider.kext",
    "BrightnessKeys.kext",
    "YogaSMC.kext",
    # Audio & Networking (Wi-Fi + Ethernet)
    "AppleALC.kext",
    "IntelMausi.kext",
    "itlwm.kext",
}

with config_path.open("rb") as f:
    plist = plistlib.load(f)

uncapped = []
for kext in plist["Kernel"]["Add"]:
    bp = kext.get("BundlePath")
    if bp in KEXTS_TO_ENABLE_ON_TAHOE and kext.get("Enabled"):
        kext["MaxKernel"] = ""
        uncapped.append(bp)
    elif bp in ("AMFIPass.kext", "Sinetek-rtsx.kext", "IntelBluetoothFirmware.kext", "BlueToolFixup.kext"):
        kext["MaxKernel"] = "24.99.99"

with config_path.open("wb") as f:
    plistlib.dump(plist, f, sort_keys=True)

print(f"[DONE] Pass 6 uncapped {len(uncapped)} kexts for Tahoe:")
for k in uncapped:
    print("  -", k)
