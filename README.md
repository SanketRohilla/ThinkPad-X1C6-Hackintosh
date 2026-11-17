# ThinkPad X1 Carbon 6th Gen (20KG / 20KH) — macOS EFI

OpenCore 1.0.2 EFI and post-install configuration for the Lenovo ThinkPad X1 Carbon 6th Generation.

Tested on **macOS Ventura (13.x)**, **Sonoma (14.x)**, **Sequoia (15.x)**, and **Tahoe (macOS 26)**.

---

## Hardware Specs

- **Model:** Lenovo ThinkPad X1 Carbon 6th Gen (`20KG` / `20KH`)
- **CPU:** Intel Core i5-8350U / i7-8550U / i7-8650U (Kaby Lake-R)
- **GPU:** Intel UHD Graphics 620
- **RAM:** 8GB / 16GB LPDDR3 2133MHz
- **Display:** 14" FHD (1920x1080) / WQHD (2560x1440)
- **Audio:** Realtek ALC285 (layout-id: `11`, `28`, or `32`)
- **Ethernet:** Intel I219-LM Gigabit
- **Wi-Fi / BT:** Intel Dual Band Wireless-AC 8265 (or AX210)
- **Storage:** Toshiba XG5 NVMe SSD (PCIe M.2)
- **Trackpad:** Synaptics ClickPad + TrackPoint via SMBus (`VoodooSMBus` + `VoodooRMI`)
- **Bootloader:** OpenCore 1.0.2
- **SMBIOS:** `MacBookPro15,2`

---

## macOS Version Support

- **macOS Ventura (13.x):** Native graphics and audio support without extra root patches.
- **macOS Sonoma (14.x) & Sequoia (15.x):** Apple dropped native Kaby Lake graphics drivers. Requires OpenCore Legacy Patcher (OCLP) root patch + `AMFIPass.kext` for full QE/CI Metal acceleration.
- **macOS Tahoe (macOS 26):** Supported. In Tahoe, Apple deprecated legacy `AppleHDA`. Audio and graphics drivers both require OCLP root patching to restore functionality. Use `config-for-Sequoia-install.plist` (`revpatch=sbvmm`) for installer updates.

---

## What Works

- [x] Intel UHD 620 Graphics (QE/CI, Metal, hardware video decode)
- [x] CPU Power Management (`CPUFriend` / SpeedShift)
- [x] Sleep / Wake (S3 sleep with BIOS set to Linux)
- [x] Audio (internal speakers, 3.5mm combo jack, internal dual mics)
- [x] Intel Wi-Fi (`itlwm.kext` + HeliPort)
- [x] Intel Bluetooth (`IntelBluetoothFirmware` + `BlueToolFixup`)
- [x] Trackpad with native macOS gestures (`VoodooSMBus` + `VoodooRMI`)
- [x] TrackPoint with physical buttons and middle-button scroll
- [x] 720p HD Webcam
- [x] Battery status & dual-battery management (`SSDT-BATX`)
- [x] HDMI video and audio out
- [x] USB-A 3.0 and USB-C / Thunderbolt 3 ports
- [x] MicroSD Card Reader (`RealtekCardReader.kext`)
- [x] Fn Keys:
  - F1-F3: Volume control (mute / down / up)
  - F4: Microphone mute (with LED toggle via YogaSMC)
  - F5-F6: Smooth backlight brightness
  - F7: Display mirror / extend toggle
  - Fn + Space: Keyboard backlight toggle (hardware EC level)
  - Fn + Esc: FnLock toggle (hardware EC level)

---

## What Doesn't Work / Limitations

- [ ] **Fingerprint Reader (Synaptics `06cb:009a`):** Will never work. macOS Touch ID requires an Apple T2 chip or Apple Silicon Secure Enclave.
- [ ] **Cellular WWAN (Fibocom L850-GL):** Intel XMM 7360 PCIe modem has no macOS drivers.
- [ ] **Hardware DRM in Safari (FairPlay 2.x/3.x):** 4K Netflix / Apple TV+ in Safari does not work without Apple T2 or AMD dGPU. 1080p streaming works in Chrome, Firefox, or Brave.
- [ ] **Samsung PM981 / PM981a SSDs:** Causes kernel panics on macOS. Replace with WD SN750/SN770, SK Hynix P31, or Samsung 970 EVO Plus if your unit came with a PM981.

---

## Continuity & Apple Ecosystem

| Feature | Stock Intel AC 8265 | With Broadcom Card (`BCM94360NG`) |
| :--- | :---: | :---: |
| iMessage & FaceTime | Yes | Yes |
| iCloud & App Store | Yes | Yes |
| AirDrop | No | Yes |
| Universal Control | No | Yes |
| Apple Watch Unlock | No | Yes |
| Handoff / Clipboard Sync | Unreliable | Yes |
| Sidecar (Wired USB) | Yes | Yes |
| Sidecar (Wireless) | No | Yes |

*Note on AirDrop:* Apple Continuity features rely on Apple Wireless Direct Link (AWDL), which only works on Apple-native Broadcom cards. If you need AirDrop and Universal Control, swap the internal M.2 Wi-Fi card with a **Broadcom BCM94360NG** (direct drop-in, no BIOS whitelist).

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

Each macOS version requires its own recovery image and configuration.

### 1. Download Recovery by macOS Version

Run the appropriate command from the repository root:

* **macOS Ventura (13.7.x):**
  ```bash
  python3 Utilities/macrecovery/macrecovery.py -b Mac-B4831CEBD52A0C4C -m 00000000000000000 download
  ```
  *(Uses standard `config.plist` directly)*

* **macOS Sonoma (14.7.x):**
  ```bash
  python3 Utilities/macrecovery/macrecovery.py -b Mac-827FAC58A8FDFA22 -m 00000000000000000 download
  ```
  *(Uses default installer `config.plist`)*

* **macOS Sequoia (15.x):**
  ```bash
  python3 Utilities/macrecovery/macrecovery.py -b Mac-7BA5B2D9E42DDD94 -m 00000000000000000 -os latest download
  ```
  *(Uses default installer `config.plist`)*

* **macOS Tahoe (macOS 26):**
  ```bash
  python3 Utilities/macrecovery/macrecovery.py -b Mac-27AD2F918AE68F61 -m 00000000000000000 -os latest download
  ```
  *(Uses default installer `config.plist`)*

  *Note:* You can also upgrade directly from Sonoma or Sequoia via **System Settings -> General -> Software Update** thanks to `revpatch=sbvmm`. Post-install, run OCLP root patches to restore both UHD 620 graphics and audio.

---

### 2. Preparing the USB Drive

1. Format a USB flash drive (1GB+ for Recovery, 16GB+ for Full Installer) as **FAT32 / MBR**.
2. Copy `EFI` and `com.apple.recovery.boot` to the root of the USB drive:
   ```text
   USB_ROOT/
   ├── EFI/
   │   ├── BOOT/
   │   │   └── BOOTx64.efi
   │   └── OC/
   │       ├── config.plist
   │       └── ...
   └── com.apple.recovery.boot/
       ├── BaseSystem.chunklist
       └── BaseSystem.dmg
   ```
3. **Out-of-the-box Installer Config:** `EFI/OC/config.plist` is already pre-configured for installation on Sonoma, Sequoia, and macOS 26 Tahoe (with `revpatch=sbvmm` active and Bluetooth kexts temporarily disabled to avoid installer freezes).
4. Insert the USB, press `F12` on boot, select your USB drive, and choose **macOS Recovery (dmg)** from the OpenCore boot picker.
5. After macOS is installed and you reach the desktop, switch to `EFI/OC/config-postinstall.plist` (rename it to `config.plist`) on your SSD to re-enable native Bluetooth.

---

## Post-Install: Undervolting & Thermal Setup

The X1 Carbon 6th Gen aggressively throttles to 15W under sustained load. The `Post-Install/VoltageShift` tools unlock 25W–35W TDP and undervolt the CPU:

```bash
cd Post-Install/VoltageShift
chmod +x voltageshift setup.sh
sudo cp ../LaunchDaemons/*.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/setup.startup*.plist
sudo bash setup.sh
```

Install `Post-Install/Apps/YogaSMC-App-Release.dmg` for fan speed control and battery charge thresholds (e.g., stop charging at 80%).

---

## Credits

- [Acidanthera](https://github.com/acidanthera) (OpenCore, Lilu, VirtualSMC, WhateverGreen, AppleALC)
- [tylernguyen/x1c6-hackintosh](https://github.com/tylernguyen/x1c6-hackintosh) (Base ACPI patches and reference)
- [Rybo713/X1C6-macOS](https://github.com/Rybo713/X1C6-macOS) (OpenCore 1.0.2 EFI structure)
- [XE-i23333/ThinkPad-X1C6-Hackintosh](https://github.com/XE-i23333/ThinkPad-X1C6-Hackintosh) (Thermal daemon scripts and Tahoe fixes)
- [OpenIntelWireless](https://github.com/OpenIntelWireless) (itlwm, HeliPort)
