#!/usr/bin/env python3
"""
TaskSense MSIX Release Builder - Simplified Version

Nutzt existierende build.py und build_msix.py - ohne Umwege!

Verwendung:
  python release_simple.py                    # Nutzt Version aus AppxManifest.xml
  python release_simple.py --version 1.0.4   # Custom-Version
  python release_simple.py --version 1.0.4 --sign --cert certs/cert.pfx

Ergebnis: dist/VERSION/TaskSense.msix (z.B. dist/1.0.4/TaskSense.msix)
"""

import subprocess
import sys
import re
from pathlib import Path


def read_version_from_manifest(project_root: Path) -> str:
    """Liest die Version aus dem AppxManifest.xml."""
    manifest_path = project_root / "AppxManifest.xml"
    
    if not manifest_path.exists():
        return "1.0.0"  # Default
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrahiere Version mit Regex
        match = re.search(r'Version="([^"]+)"', content)
        if match:
            version = match.group(1)
            # Konvertiere von 4-stellig (1.0.0.0) zu 3-stellig (1.0.0) wenn möglich
            if version.endswith('.0') and version.count('.') == 3:
                version = version[:-2]
            return version
    except Exception:
        pass
    
    return "1.0.0"  # Default


def run_release(version: str = None, sign: bool = False, cert_path: str = None):
    """Führt den kompletten Release aus."""
    
    project_root = Path(__file__).parent
    
    # Wenn keine Version gegeben, aus Manifest auslesen
    if not version:
        version = read_version_from_manifest(project_root)
        print(f"📖 Version aus AppxManifest.xml gelesen: {version}\n")
    
    print("\n" + "=" * 70)
    print("🚀 TaskSense MSIX Release Builder".center(70))
    print("=" * 70 + "\n")
    
    # Schritt 1: Baue .exe
    print("📦 Schritt 1: Baue .exe mit PyInstaller...")
    print("-" * 70)
    
    try:
        result = subprocess.run([sys.executable, str(project_root / "build.py")], check=False)
        if result.returncode != 0:
            print("❌ .exe Build fehlgeschlagen")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False
    
    # Schritt 2: Baue MSIX
    print("\n📦 Schritt 2: Baue MSIX-Paket mit MakeAppx...")
    print("-" * 70)
    
    cmd = [sys.executable, str(project_root / "build_msix.py"), "--version", version]
    
    if sign and cert_path:
        cmd.extend(["--sign", "--cert", cert_path])
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print("❌ MSIX Build fehlgeschlagen")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False
    
    # Erfolg!
    print("\n" + "=" * 70)
    print("✅ MSIX Release erfolgreich!".center(70))
    print("=" * 70 + "\n")
    
    # Ausgabepfad: dist/VERSION/TaskSense.msix
    msix_path = project_root / "dist" / version / "TaskSense.msix"
    if msix_path.exists():
        size = msix_path.stat().st_size / (1024 * 1024)
        print(f"📁 Ausgabe: {msix_path}")
        print(f"   Größe: {size:.1f} MB")
        print(f"   Version: {version}\n")
    
    print("🚀 Bereit für Microsoft Store Upload!")
    print("   1. Partner Center: https://partner.microsoft.com/")
    print("   2. Lade MSIX-Datei hoch")
    print("   3. Durchlaufe Zertifizierung\n")
    
    return True


def main():
    """Haupteinstiegspunkt."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TaskSense MSIX Release Builder",
        epilog="Beispiel: python release_simple.py --version 1.0.4 --sign --cert certs/cert.pfx"
    )
    parser.add_argument("--version", default=None, help="Versionsnummer (wenn nicht angegeben: aus AppxManifest.xml)")
    parser.add_argument("--sign", action="store_true", help="Mit Zertifikat signieren")
    parser.add_argument("--cert", type=str, help="Zertifikat-Pfad (.pfx)")
    
    args = parser.parse_args()
    
    success = run_release(version=args.version, sign=args.sign, cert_path=args.cert)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
