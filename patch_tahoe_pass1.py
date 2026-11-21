#!/usr/bin/env python3
"""
Pass 1 deterministic patch for ThinkPad X1C6 (macOS Sequoia + macOS Tahoe).
Applies isolated, dual-boot-safe fixes without altering ACPI, SMBIOS, or Sequoia kexts.
"""

import plistlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

TARGET_BOOT_ARGS = (
    "keepsyms=1 debug=0x100 -v msgbuf=1048576 -lilubetaall -no_compat_check "
    "revpatch=sbvmm -btlfxallowanyaddr -amfipassbeta -revbeta -wegbeta "
    "-ibtcompatbeta ipc_control_port_options=0 -vsmcbeta -igfxvesa"
)

IGPU_PATH = "PciRoot(0x0)/Pci(0x2,0x0)"
NVRAM_APPLE_GUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
IGPU_KEYS_TO_REMOVE = ("AAPL,GfxYTile", "disable-external-gpu", "enable-hdmi20")


def patch_config(config_path: Path) -> None:
    if not config_path.is_file():
        sys.exit(f"ERROR: File not found: {config_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = config_path.with_name(f"{config_path.name}.bak_{timestamp}")
    shutil.copy2(config_path, backup_path)
    print(f"[BACKUP] Saved original config to: {backup_path}")

    with config_path.open("rb") as f:
        plist = plistlib.load(f)

    # 1. Revert unverified T480 IGPU properties back to working Sequoia baseline
    igpu_props = plist["DeviceProperties"]["Add"].get(IGPU_PATH, {})
    for key in IGPU_KEYS_TO_REMOVE:
        if key in igpu_props:
            del igpu_props[key]
            print(f"[DeviceProperties] Removed {IGPU_PATH} -> {key}")

    # 2. Cap AMFIPass.kext to Darwin <= 24 (Sequoia) so unpatched Tahoe installer runs clean AMFI
    amfi_found = False
    for kext in plist["Kernel"]["Add"]:
        if kext.get("BundlePath") == "AMFIPass.kext":
            kext["MaxKernel"] = "24.99.99"
            amfi_found = True
            print("[Kernel->Add] Set AMFIPass.kext MaxKernel = '24.99.99'")
            break
    if not amfi_found:
        print("[WARN] AMFIPass.kext not found in Kernel->Add")

    # 3. Disable APFS TRIM stall on Toshiba XG5 mount
    plist["Kernel"]["Quirks"]["SetApfsTrimTimeout"] = 0
    print("[Kernel->Quirks] Set SetApfsTrimTimeout = 0")

    # 4. Clean boot-args (remove Linux panic=15, amfi_get_out_of_my_way=1, igfxonln=1; add debug=0x100, -igfxvesa)
    nvram_add = plist["NVRAM"]["Add"][NVRAM_APPLE_GUID]
    nvram_add["boot-args"] = TARGET_BOOT_ARGS
    print(f"[NVRAM->Add] Updated boot-args:\n  {TARGET_BOOT_ARGS}")

    # 5. Keep watchdog disabled and panic dumps readable for diagnostic capture
    plist["Misc"]["Debug"]["DisableWatchDog"] = True
    plist["Kernel"]["Quirks"]["PanicNoKextDump"] = True

    with config_path.open("wb") as f:
        plistlib.dump(plist, f, sort_keys=True)

    print(f"[DONE] Successfully wrote patched config to: {config_path}")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("EFI/OC/config.plist")
    patch_config(target)
