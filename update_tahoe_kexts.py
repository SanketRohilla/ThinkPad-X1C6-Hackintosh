#!/usr/bin/env python3
import io, json, shutil, urllib.request, zipfile
from pathlib import Path

kexts_dir = Path("EFI-Tahoe/OC/Kexts")
tmp_dir = Path("/tmp/tahoe_kext_bundle")
if tmp_dir.exists():
    shutil.rmtree(tmp_dir)
tmp_dir.mkdir(parents=True)

REPOS = [
    ("laobamac/SimpleHDA", ["SimpleHDA.kext"]),
    ("acidanthera/Lilu", ["Lilu.kext"]),
    ("acidanthera/VirtualSMC", ["VirtualSMC.kext", "SMCProcessor.kext", "SMCBatteryManager.kext", "SMCLightSensor.kext"]),
    ("acidanthera/WhateverGreen", ["WhateverGreen.kext"]),
    ("acidanthera/AppleALC", ["AppleALC.kext"]),
    ("acidanthera/RestrictEvents", ["RestrictEvents.kext"]),
    ("acidanthera/BrcmPatchRAM", ["BlueToolFixup.kext"]),
    ("OpenIntelWireless/IntelBluetoothFirmware", ["IntelBluetoothFirmware.kext"]),
]

for repo, targets in REPOS:
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(api_url, headers={"User-Agent": "OpenCore-Builder"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            release = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[WARN] Failed API lookup for {repo}: {e}")
        continue

    assets = release.get("assets", [])
    chosen = next((a for a in assets if "RELEASE" in a["name"].upper() and a["name"].endswith(".zip")), None)
    if not chosen:
        chosen = next((a for a in assets if a["name"].endswith(".zip") and "DEBUG" not in a["name"].upper()), None)
    if not chosen:
        print(f"[WARN] No release zip found for {repo}")
        continue

    print(f"[FETCH] {repo} -> {chosen['name']}")
    zip_bytes = urllib.request.urlopen(chosen["browser_download_url"], timeout=30).read()
    extract_dir = tmp_dir / repo.replace("/", "_")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(extract_dir)

    for target in targets:
        matches = [p for p in extract_dir.rglob(target) if p.is_dir() and "__MACOSX" not in str(p)]
        if matches:
            dest = kexts_dir / target
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(matches[0], dest)
            print(f"  [INSTALLED] {dest}")
