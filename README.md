# Lenovo ThinkPad X1 Carbon 6th Gen (2018) — OpenCore 1.0.2 EFI

A complete, battle-tested OpenCore EFI configuration and post-installation optimization suite for the **Lenovo ThinkPad X1 Carbon 6th Generation (`20KG` / `20KH`)** running macOS Ventura, Sonoma, Sequoia, and beyond.

---

## 💻 Hardware Specifications

| Component | Target Hardware | Status | Driver / Kext |
| :--- | :--- | :--- | :--- |
| **Processor** | Intel Core i5-8350U / i7-8550U / i7-8650U (Kaby Lake-R) | **Working** | Native XNU Power Management + `CPUFriend` |
| **Graphics** | Intel UHD Graphics 620 (`8086:5917` / `5916`) | **Working** | `WhateverGreen.kext` (Metal, QE/CI, QuickSync) |
| **Memory** | 8GB / 16GB LPDDR3 2133MHz | **Working** | Native |
| **Audio** | Realtek ALC285 / Intel Sunrise Point-LP (`8086:9d71`) | **Working** | `AppleALC.kext` (Layout-ID `11`, `28`, or `32`) |
| **Ethernet** | Intel Ethernet Connection I219-LM (`8086:15d7`) | **Working** | `IntelMausi.kext` |
| **Wi-Fi** | Intel Dual Band Wireless-AC 8265 (`8086:24fd`) / AX210 | **Working** | `itlwm.kext` + HeliPort (or `AirportItlwm.kext`) |
| **Bluetooth**| Intel Wireless Bluetooth | **Working** | `IntelBluetoothFirmware.kext` + `BlueToolFixup.kext` |
| **Storage** | NVMe SSD (Toshiba XG5, WD SN750/770, SK Hynix P31) | **Working** | `NVMeFix.kext` *(Note: Avoid Samsung PM981)* |
| **Trackpad** | Synaptics ClickPad + TrackPoint + 3 Physical Buttons | **Working** | `VoodooSMBus.kext` + `VoodooRMI.kext` (Native multi-touch gestures) |
| **Keyboard** | ThinkPad Backlit Keyboard & Fn Shortcuts | **Working** | `VoodooPS2Controller.kext` + `BrightnessKeys.kext` + `YogaSMC` |
| **Display** | 14" FHD (1920x1080) / WQHD (2560x1440) | **Working** | Smooth backlight control via `SSDT-PNLF.aml` |
| **Ports** | 2x USB-A 3.0, 2x Thunderbolt 3 / USB-C, 1x HDMI | **Working** | ACPI TB3 hotplug tree + Custom USB mapping |
| **Camera** | 720p HD Webcam | **Working** | Native UVC USB video |
| **Card Reader**| Realtek RTS525A PCIe MicroSD Card Reader | **Working** | `RealtekCardReader.kext` |
| **Fingerprint**| Synaptics USB Fingerprint Sensor | **Unsupported**| macOS does not support third-party biometric sensors |
| **WWAN (LTE)**| Fibocom L850-GL 4G LTE Module | **Unsupported**| Intel XMM 7360 PCIe modem has no macOS driver |

---

## ⌨️ ThinkPad Function (Fn) Keys

All essential function keys and Lenovo shortcuts are properly mapped:

| Key Combination | Function | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Fn + Esc** | FnLock Toggle | **Working** | Handled natively by Lenovo Embedded Controller (EC) |
| **F1** | Audio Mute | **Working** | Native macOS volume mute |
| **F2** | Volume Down | **Working** | Native macOS volume down |
| **F3** | Volume Up | **Working** | Native macOS volume up |
| **F4** | Microphone Mute | **Working** | Mutes input; orange LED toggle via `YogaSMC` |
| **F5** | Brightness Down | **Working** | 16-step smooth display dimming via `BrightnessKeys` |
| **F6** | Brightness Up | **Working** | 16-step smooth display brightness via `BrightnessKeys` |
| **F7** | Projector / Multi-Display | **Working** | Native macOS display mirror/extend toggle |
| **F8** | Wi-Fi Toggle | **N/A** | macOS handles networking via Menu Bar / HeliPort |
| **F9** | Settings / Notification Center | **Working** | Opens macOS Notification Center |
| **F10** | Bluetooth Toggle | **N/A** | Managed via macOS Control Center |
| **F11** | Keyboard Backlight / Custom | **Working** | Can be mapped via macOS Shortcuts or `YogaSMC` |
| **F12** | User-Defined Star Key | **Working** | Configurable via macOS Keyboard Shortcuts |
| **Fn + Space** | Keyboard Backlight (Off/Low/High) | **Working** | Handled by EC in hardware (100% OS independent) |
| **TrackPoint** | Red TrackPoint + Left/Middle/Right Click | **Working** | Smooth cursor movement + middle-click scroll |

---

## 🍏 Apple Continuity & Ecosystem Features

| Feature | Stock Intel AC 8265 | With Broadcom Upgrade (`BCM94360NG`) | Notes |
| :--- | :---: | :---: | :--- |
| **iMessage & FaceTime** | ✅ **Working** | ✅ **Working** | Requires valid SMBIOS serials generated via GenSMBIOS |
| **iCloud & App Store** | ✅ **Working** | ✅ **Working** | Native authentication |
| **AirDrop** | ❌ **Unsupported** | ✅ **Working** | Requires Apple Wireless Direct Link (AWDL) proprietary protocol |
| **Universal Control** | ❌ **Unsupported** | ✅ **Working** | Requires native Apple Broadcom Wi-Fi & Bluetooth stack |
| **Handoff & Universal Clipboard**| ⚠️ **Unreliable / Broken** | ✅ **Working** | `itlwm` cannot reliably sustain Apple Continuity daemon sync |
| **Apple Watch Unlock** | ❌ **Unsupported** | ✅ **Working** | Requires native AWDL ranging and timing |
| **AirPlay to Mac** | ⚠️ **Partial** | ✅ **Working** | Works over local LAN; direct peer-to-peer requires Broadcom AWDL |
| **Sidecar (Wired USB)** | ✅ **Working** | ✅ **Working** | Plug iPad via USB cable |
| **Sidecar (Wireless)** | ❌ **Unsupported** | ✅ **Working** | Requires AWDL / Broadcom Wi-Fi |

---

## 🚫 Unsupported Hardware & System Limitations

1. **Fingerprint Sensor (Synaptics `06cb:009a`):**
   - **Status:** Unsupported.
   - **Reason:** Apple's Touch ID authentication is cryptographically tethered to Apple Silicon / T2 Secure Enclave processors. No third-party USB fingerprint reader can interface with macOS PAM / Keychain.
2. **WWAN 4G LTE Cellular Modem (Fibocom L850-GL):**
   - **Status:** Unsupported.
   - **Reason:** Built on the Intel XMM 7360 PCIe modem architecture, for which no macOS drivers or RIL daemons exist.
3. **Hardware DRM in Safari (FairPlay 2.x / 3.x):**
   - **Status:** Limited.
   - **Details:** 4K Netflix and Apple TV+ in Safari require an Apple T2 chip or discrete AMD GPU.
   - **Solution:** 1080p streaming works perfectly in Chrome, Firefox, Brave, and Edge using Widevine DRM.
4. **Incompatible NVMe SSDs:**
   - **Samsung PM981 / PM981a (OEM)** causes unrecoverable kernel panics in macOS.
   - *Supported alternatives:* Toshiba XG5 (stock), WD Black SN750 / SN770, SK Hynix Gold P31, Crucial P3/P5, Samsung 970 EVO Plus.

---

## 🔄 Recommended Hardware Upgrade: Broadcom BCM94360NG

If you need full native **AirDrop**, **Universal Control**, **Handoff**, and **Apple Watch Unlock**:
* Replace the internal M.2 Wi-Fi card (`Intel AC 8265`) with a **Broadcom BCM94360NG** (M.2 Key A/E).
* **Advantages:**
  * Direct drop-in replacement (no whitelist restrictions on X1 Carbon 6th Gen).
  * Recognized natively as an Apple AirPort card without `itlwm` or HeliPort.
  * *Note for macOS Sonoma & Sequoia:* Requires applying OpenCore Legacy Patcher (OCLP) Modern Wireless root patches, as Apple removed native Kexts for Broadcom cards starting in macOS 14.

---

## 🚀 Supported macOS Versions

* **macOS High Sierra (10.13) → macOS Ventura (13.7.x):**  
  *100% Native out-of-the-box.* Zero root patching required.
* **macOS Sonoma (14.x) → macOS Sequoia (15.x):**  
  Apple dropped native Kaby Lake drivers starting in Sonoma. Full Metal QE/CI graphics acceleration is restored using **OpenCore Legacy Patcher (OCLP)** post-install root patches alongside `AMFIPass.kext`.

---

## 🗂️ Repository Structure

```text
├── EFI/
│   ├── BOOT/
│   │   └── BOOTx64.efi
│   └── OC/
│       ├── ACPI/           # Custom patched AML tables (Battery dual-register, TB3 tree, PNLF, etc.)
│       ├── Drivers/        # OpenRuntime, HFSPlus, OpenCanopy, AudioDxe, ResetNvramEntry
│       ├── Kexts/          # Lilu, VirtualSMC, WhateverGreen, AppleALC, itlwm, VoodooSMBus, etc.
│       ├── Resources/      # OpenCanopy graphical icons, fonts, and boot chime audio files
│       ├── Tools/          # UEFI diagnostic and shell tools
│       ├── config.plist    # Primary OpenCore 1.0.2 configuration (MacBookPro15,2)
│       └── config-for-Sequoia-install.plist # Installation config with revpatch=sbvmm for macOS 15
├── Post-Install/
│   ├── Apps/
│   │   ├── HeliPort_v1.5.0.dmg      # Intel Wi-Fi status bar manager
│   │   └── YogaSMC-App-Release.dmg  # Fan speed controller & battery charge threshold utility
│   ├── VoltageShift/                # CPU undervolting (-80mV core, -50mV GPU, unlocked 25W/35W TDP)
│   └── LaunchDaemons/               # Startup daemons to re-apply undervolt & power limits on boot/wake
├── .gitignore
└── README.md
```

---

## ⚙️ Recommended BIOS Settings

Reboot your ThinkPad and press **Enter** / **F1** to enter BIOS Setup:

* **Config:**
  * Network → Wake On LAN: **Disabled**
  * Power → Sleep State: **Linux**
  * Thunderbolt 3 → BIOS Assist: **Disabled**
  * Thunderbolt 3 → Security Level: **User Authorization** (or **No Security**)
* **Security:**
  * Security Chip: **Disabled** (optional)
  * Password → Fingerprint Predesktop: **Disabled**
  * Secure Boot → Secure Boot: **Disabled**
* **Startup:**
  * UEFI/Legacy Boot: **UEFI Only**
  * CSM Support: **No**

---

## 🛠️ Installation Guide

### 1. Preparing the USB Drive
1. Format a USB 3.0 flash drive (16GB+) as **FAT32** with **MBR** or **GPT** partition scheme.
2. Copy the entire `EFI` folder from this repository directly to the root of your USB drive so that `/EFI/BOOT/BOOTx64.efi` and `/EFI/OC/OpenCore.efi` exist at the top level.

### 2. Generating Unique SMBIOS (Recommended for iServices)
For FaceTime, iMessage, and Apple ID, generate your own unique serials using [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS) or `macserial`:
* Target Model: `MacBookPro15,2`
* Update `PlatformInfo` -> `Generic`:
  * `SystemSerialNumber`
  * `MLB` (Board Serial)
  * `SystemUUID`

### 3. Post-Installation Optimizations

#### A. Wi-Fi (HeliPort)
Install [HeliPort](Post-Install/Apps/HeliPort_v1.5.0.dmg) to connect to Wi-Fi networks using `itlwm.kext`.

#### B. Fan & Thermal Management (YogaSMC)
Install [YogaSMC](Post-Install/Apps/YogaSMC-App-Release.dmg) to monitor real-time fan RPM, set custom fan curves, and configure battery charge protection (e.g. stop charging at 80%).

#### C. CPU Undervolting & Power Limit Unlocking (VoltageShift)
The X1C6 thermal throttles down to ~15W under continuous load. To unlock sustained 25W–35W turbo boosts and run 10–15°C cooler:
```bash
cd Post-Install/VoltageShift
chmod +x voltageshift setup.sh
sudo cp ../LaunchDaemons/*.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/setup.startup*.plist
sudo bash setup.sh
```

---

## 🤝 Credits
* [Acidanthera](https://github.com/acidanthera) for OpenCorePkg, Lilu, VirtualSMC, WhateverGreen, AppleALC, and OpenCore drivers.
* [tylernguyen/x1c6-hackintosh](https://github.com/tylernguyen/x1c6-hackintosh) for the foundational X1C6 ACPI patches and reference documentation.
* [Rybo713/X1C6-macOS](https://github.com/Rybo713/X1C6-macOS) for OpenCore 1.0.2 maintenance and Sequoia adaptations.
* [XE-i23333/ThinkPad-X1C6-Hackintosh](https://github.com/XE-i23333/ThinkPad-X1C6-Hackintosh) for the VoltageShift thermal daemon and YogaSMC profiles.
* [OpenIntelWireless](https://github.com/OpenIntelWireless) for itlwm and HeliPort.
