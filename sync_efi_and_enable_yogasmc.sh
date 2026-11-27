#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo: sudo bash $0"
    exit 1
fi

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
EFI_FOLDER="${1:-EFI-Tahoe}"
if [ ! -d "$REPO_DIR/$EFI_FOLDER/OC" ] && [ -d "$REPO_DIR/EFI/OC" ]; then
    EFI_FOLDER="EFI"
fi
EFI_SOURCE="$REPO_DIR/$EFI_FOLDER"

if [ ! -d "$EFI_SOURCE/OC" ]; then
    echo "[-] Error: OpenCore folder not found at $EFI_SOURCE"
    exit 1
fi

echo "=========================================================="
echo " ThinkPad X1C6: $EFI_FOLDER Sync & YogaSMC Setup"
echo "=========================================================="

# 1. Determine which EFI partition contains OpenCore
get_mount_point() {
    diskutil info -plist "$1" 2>/dev/null | plutil -extract MountPoint raw -o - - 2>/dev/null || true
}

EFI_DEV=""
TARGET_MOUNT=""
for dev in /dev/disk0s5 /dev/disk0s1; do
    echo "[*] Checking partition $dev..."
    diskutil mount "$dev" >/dev/null 2>&1 || true
    MOUNT_POINT="$(get_mount_point "$dev")"

    if [ -n "$MOUNT_POINT" ] && [ -d "$MOUNT_POINT" ]; then
        if [ -d "$MOUNT_POINT/EFI/OC" ]; then
            echo "[+] Found OpenCore target at: $dev mounted at $MOUNT_POINT"
            EFI_DEV="$dev"
            TARGET_MOUNT="$MOUNT_POINT"
            break
        fi
        diskutil unmount "$MOUNT_POINT" >/dev/null 2>&1 || true
    fi
done

if [ -z "$EFI_DEV" ]; then
    echo "[-] Could not automatically find OpenCore EFI partition. Defaulting to /dev/disk0s5..."
    diskutil mount /dev/disk0s5 >/dev/null 2>&1 || true
    TARGET_MOUNT="$(get_mount_point /dev/disk0s5)"
fi

# 2. Sync updated EFI files
if [ -n "$TARGET_MOUNT" ] && [ -d "$TARGET_MOUNT" ]; then
    echo "[*] Syncing updated EFI to $TARGET_MOUNT/EFI..."
    mkdir -p "$TARGET_MOUNT/EFI"
    
    # Backup current active config on EFI
    if [ -f "$TARGET_MOUNT/EFI/OC/config.plist" ]; then
        cp "$TARGET_MOUNT/EFI/OC/config.plist" "$TARGET_MOUNT/EFI/OC/config.plist.bak_$(date +%Y%m%d_%H%M%S)"
    fi

    cp -R "$EFI_SOURCE/"* "$TARGET_MOUNT/EFI/"
    echo "[OK] EFI successfully synced to ESP ($TARGET_MOUNT/EFI)!"
    
    # Safely unmount
    diskutil unmount "$TARGET_MOUNT" >/dev/null 2>&1 || true
else
    echo "[!] Warning: EFI mount point not accessible. Please verify partition."
fi

# 3. Load YogaSMC into live kernel right now
echo "[*] Loading YogaSMC.kext into live macOS kernel..."
YOGAKEXT="$EFI_SOURCE/OC/Kexts/YogaSMC.kext"
chown -R root:wheel "$YOGAKEXT"
chmod -R 755 "$YOGAKEXT"
kextload "$YOGAKEXT" 2>/dev/null || true

# 4. Launch YogaSMCNC app for current user
echo "[*] Starting YogaSMC menu bar app..."
SUDO_USER_NAME="${SUDO_USER:-$(stat -f %Su /dev/console)}"
su "$SUDO_USER_NAME" -c "open /Applications/YogaSMCNC.app" 2>/dev/null || true

echo "=========================================================="
echo " [SUCCESS] All tasks completed!"
echo " 1. YogaSMC driver loaded & menu bar app started."
echo " 2. New SMBIOS & uncapped YogaSMC synced to your active EFI."
echo " 3. IMPORTANT: Restart your ThinkPad now, press Spacebar at"
echo "    the OpenCore menu, select 'Reset NVRAM', then boot in"
echo "    and sign in to Apple ID / iMessage / iCloud."
echo "=========================================================="
