# ThinkPad X1 Carbon 6th Gen (20KG / 20KH) — macOS EFI

OpenCore EFI and post-install suite for the Lenovo ThinkPad X1 Carbon 6th Generation.

| Folder | Target macOS Versions | OpenCore | SMBIOS | Status |
| :--- | :--- | :---: | :---: | :--- |
| [`EFI/`](./EFI) | **Ventura (13.x)**, **Sonoma (14.x)**, **Sequoia (15.x)** | 1.0.2 | `MacBookPro15,2` | Stable (`v1.0.5`) |
| [`EFI-Tahoe/`](./EFI-Tahoe) | **macOS Tahoe (26.x)** + Dual-Boot Sonoma / Sequoia | 1.0.8 | `MacBookPro16,3` | **Beta (`v1.0.8`)** |

> **Recommendation:**
> - Use **`EFI/`** if you only run **Ventura, Sonoma, or Sequoia** (keeps full Thunderbolt 3 support and `MacBookPro15,2` SMBIOS).
> - Use **`EFI-Tahoe/`** if you are running or dual-booting **macOS 26 Tahoe** (kernel-gated with `MinKernel`/`MaxKernel` so Sonoma and Sequoia also boot from the same OpenCore picker).

---

## Hardware Specs

- **Model:** Lenovo ThinkPad X1 Carbon 6th Gen (`20KG` / `20KH`)
- **CPU:** Intel Core i5-8350U / i7-8550U / i7-8650U (Kaby Lake-R)
- **GPU:** Intel UHD Graphics 620 (`0x59160000`)
- **RAM:** 8GB / 16GB LPDDR3 2133MHz
- **Display:** 14" FHD (1920x1080) / WQHD (2560x1440)
- **Audio:** Realtek ALC285 (`layout-id: 21`, or `11` / `28` / `32`)
- **Ethernet:** Intel I219-LM Gigabit (`IntelMausi.kext`)
- **Wi-Fi / BT:** Intel Dual Band Wireless-AC 8265 (or AX210)
- **Storage:** Toshiba XG5 NVMe SSD (PCIe M.2)
- **Trackpad:** Synaptics ClickPad + TrackPoint via SMBus (`VoodooSMBus` + `VoodooRMI`)

---

## macOS Version Notes

### macOS Ventura (13.x)
- Native graphics and audio support via [`EFI/`](./EFI).

### macOS Sonoma (14.x) & Sequoia (15.x)
- Apple dropped native Kaby Lake graphics drivers in Sonoma/Sequoia — requires OpenCore Legacy Patcher (OCLP) root patch + `AMFIPass.kext` for full QE/CI Metal acceleration.
- **Wi-Fi Setup (Important!):** Both `EFI/` and `EFI-Tahoe/` use `itlwm.kext`, which creates an Ethernet-like interface (`en1`) and **does not show in System Settings -> Wi-Fi**. After installing Sonoma/Sequoia, install and launch **`Post-Install/Apps/HeliPort_v1.5.0.dmg`** (`/Applications/HeliPort.app`) to connect to Wi-Fi networks.

### macOS Tahoe (26.x) — `v1.0.8 Tahoe Beta`
Verified on **macOS 26.7.3 (Build `25G342`, Darwin `25.6.0`)** with [`EFI-Tahoe/`](./EFI-Tahoe):
- **Graphics:** Native `AppleIntelKBLGraphics` / Metal 3 (2048 MB VRAM) works out of the box with `WhateverGreen.kext` 1.7.1.
- **Audio:** Restored via **`SimpleHDA.kext` v1.0.2** (`MinKernel = 25.0.0`, `DisableLinkeditJettison = True`) + `AppleALC.kext` 1.9.8 + `shda-lang=en`.
- **Wi-Fi:** `itlwm.kext` 2.3.0 + `HeliPort.app`.
- **Bluetooth:** `IntelBluetoothFirmware.kext` 2.4.0 + `IntelBTPatcher.kext` 2.4.0 + `BlueToolFixup.kext` 2.7.2 + `SSDT-XHC1.aml` (`XHC1` `_UPC`/`_PS0`/`_PS3` ACPI patches).
- **Trackpad / Keyboard / Hotkeys:** `VoodooPS2Controller.kext` + `VoodooSMBus.kext` + `VoodooRMI.kext` + `BrightnessKeys.kext` + uncapped `YogaSMC.kext`.
- **Undervolting / Power:** `VoltageShift.kext` injected in `EFI-Tahoe/OC/Kexts`.
- **Kernel Compatibility:**
  - `MacBookPro16,3` SMBIOS + `Skip Board ID check` booter patch + `-no_compat_check`.
  - `AppleThunderboltNHI` is excluded on Darwin `25.0.0+` (`MinKernel = 25.0.0`) to prevent PCIe/DMA hard-locks on Tahoe (Thunderbolt 3 remains active on Sonoma/Sequoia).
  - `AMFIPass.kext`, `NVMeFix.kext`, `HibernationFixup.kext`, and `Sinetek-rtsx.kext` are capped at `MaxKernel = 24.99.99` (active on Sonoma/Sequoia, skipped on Tahoe; X1C6 MicroSD reader works natively over USB `USB3.0-CRW`).

#### Tahoe Post-Install Scripts
1. **Sync `EFI-Tahoe` to ESP & Load `YogaSMC.kext`:**
   ```bash
   sudo bash sync_efi_and_enable_yogasmc.sh
   ```
   *(Uses `plutil` so `/Volumes/NO NAME` mounts safely. Reboot and select **Reset NVRAM** at the OpenCore picker afterward, then regenerate your own SMBIOS with `Utilities/macserial` before signing into Apple ID / iMessage.)*
2. **Fix Blank `Apps.app` Launcher (Spotlight Apps-Only Mode):**
   On macOS 26, `/System/Applications/Apps.app` appears blank if Spotlight is completely disabled. Run:
   ```bash
   sudo bash enable_apps_only_spotlight.sh
   ```
   This enables Spotlight indexing only for `/Applications` and `/System/Applications` while excluding `/Users`, `/Library`, `/private`, and secondary volumes so background CPU stays minimal.
3. **Note on System Debloating:** Do **not** bulk-disable Apple `launchd` agents (`photolibraryd`, `appplaceholdersyncd`, `ThumbnailsAgent`, etc.) on Tahoe — it breaks **Photos.app**, **Dock/Apps launcher**, and **QuickLook** while yielding virtually no performance gain.

---

## What Works

- [x] Intel UHD 620 Graphics (QE/CI, Metal, hardware video decode)
- [x] CPU Power Management (`CPUFriend` / SpeedShift)
- [x] Sleep / Wake (S3 sleep with BIOS set to Linux)
- [x] Audio (internal speakers, 3.5mm combo jack, internal dual mics)
- [x] Intel Wi-Fi (`itlwm.kext` + `HeliPort.app`)
- [x] Intel Bluetooth (`IntelBluetoothFirmware` + `IntelBTPatcher` + `BlueToolFixup`)
- [x] Trackpad with native macOS gestures (`VoodooSMBus` + `VoodooRMI`)
- [x] TrackPoint with physical buttons and middle-button scroll
- [x] 720p HD Webcam
- [x] Battery status & dual-battery management (`SSDT-BATX`)
- [x] HDMI video and audio out
- [x] USB-A 3.0 and USB-C ports (Thunderbolt 3 active on Ventura/Sonoma/Sequoia; disabled on Tahoe Beta)
- [x] MicroSD Card Reader (native USB3.0-CRW / `Sinetek-rtsx.kext` on <=Sequoia)
- [x] Fn Keys (`F1-F3` volume, `F4` mic mute via `YogaSMC`, `F5-F6` brightness, `F7` display toggle, `Fn+Space`, `Fn+Esc`)

---

## What Doesn't Work / Limitations

- [ ] **Fingerprint Reader (Synaptics `06cb:009a`):** Will never work (Touch ID requires Apple T2 / Apple Silicon).
- [ ] **Cellular WWAN (Fibocom L850-GL):** Intel XMM 7360 PCIe modem has no macOS drivers.
- [ ] **Thunderbolt 3 on macOS Tahoe 26:** Blocked (`AppleThunderboltNHI` excluded on Darwin 25+) to avoid PCIe/DMA lockups.
- [ ] **Hardware DRM in Safari (FairPlay 2.x/3.x):** 1080p streaming works in Chrome, Firefox, Brave, or Zen.
- [ ] **Samsung PM981 / PM981a SSDs:** Causes kernel panics on macOS.
- [ ] **AirDrop / Universal Control / Apple Watch Unlock:** Requires swapping the Intel AC 8265 with a Broadcom `BCM94360NG`.

---

## BIOS Settings

Reboot and hit `Enter` / `F1` to enter ThinkPad BIOS Setup:

- **Config -> Power -> Sleep State:** `Linux` (Crucial for S3 sleep)
- **Config -> Thunderbolt 3 -> BIOS Assist:** `Disabled`
- **Config -> Thunderbolt 3 -> Security Level:** `User Authorization` or `No Security`
- **Security -> Secure Boot:** `Disabled`
- **Security -> Fingerprint Predesktop:** `Disabled`
- **Startup -> UEFI/Legacy Boot:** `UEFI Only`, CSM `No`

---

## USB Installer & Recovery Setup

Run the appropriate command from the repository root:

* **macOS Ventura (13.7.x):**
  ```bash
  python3 Utilities/macrecovery/macrecovery.py -b Mac-B4831CEBD52A0C4C -m 0000000000000000 download
  ```
* **macOS Sonoma (14.7.x):**
  ```bash
  python3 Utilities/macrecovery/macrecovery.py -b Mac-827FAC58A8FDFA22 -m 0000000000000000 download
  ```
* **macOS Sequoia (15.x):**
  ```bash
  python3 Utilities/macrecovery/macrecovery.py -b Mac-7BA5B2D9E42DDD94 -m 0000000000000000 download
  ```

Copy either `EFI/` (for Ventura/Sonoma/Sequoia) or `EFI-Tahoe/` (renamed to `EFI/` on your USB/ESP for Tahoe or dual-boot) alongside `com.apple.recovery.boot/` onto a **FAT32 / MBR** USB drive.

---

## Post-Install: Undervolting & Thermal Setup

```bash
cd Post-Install/VoltageShift
chmod +x voltageshift setup.sh
sudo bash setup.sh
```

Install `Post-Install/Apps/YogaSMC-App-Release.dmg` for fan speed control and battery charge thresholds, and `Post-Install/Apps/HeliPort_v1.5.0.dmg` for Wi-Fi.

---

## Credits

- [Acidanthera](https://github.com/acidanthera) (OpenCore, Lilu, VirtualSMC, WhateverGreen, AppleALC)
- [laobamac](https://github.com/laobamac/SimpleHDA) (SimpleHDA for macOS Tahoe)
- [tylernguyen/x1c6-hackintosh](https://github.com/tylernguyen/x1c6-hackintosh) (Base ACPI patches and reference)
- [Rybo713/X1C6-macOS](https://github.com/Rybo713/X1C6-macOS) (OpenCore EFI structure)
- [XE-i23333/ThinkPad-X1C6-Hackintosh](https://github.com/XE-i23333/ThinkPad-X1C6-Hackintosh) (Thermal daemon scripts and references)
- [OpenIntelWireless](https://github.com/OpenIntelWireless) (itlwm, HeliPort, IntelBluetoothFirmware)
