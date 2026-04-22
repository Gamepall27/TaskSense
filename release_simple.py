#!/usr/bin/env python3
"""
TaskSense MSIX Release Builder - Simplified Version

Nutzt existierende build.py und build_msix.py - ohne Umwege!

Verwendung:
  python release_simple.py
  python release_simple.py --version 1.0.4
  python release_simple.py --version 1.0.4 --sign --cert certs/cert.pfx

Ergebnis: dist/VERSION/TaskSense.msix (z.B. dist/1.0.4.0/TaskSense.msix)
"""

import subprocess
import sys
from pathlib import Path


def run_release(version: str = "1.0.0", sign: bool = False, cert_path: str = None):
    """Führt den kompletten Release aus."""
    
    print("\n" + "=" * 70)
    print("🚀 TaskSense MSIX Release Builder".center(70))
    print("=" * 70 + "\n")
    
    project_root = Path(__file__).parent
    
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
        epilog="Beispiel: python release_simple.py --version 1.0.1 --sign --cert certs/cert.pfx"
    )
    parser.add_argument("--version", default="1.0.0", help="Versionsnummer")
    parser.add_argument("--sign", action="store_true", help="Mit Zertifikat signieren")
    parser.add_argument("--cert", type=str, help="Zertifikat-Pfad (.pfx)")
    
    args = parser.parse_args()
    
    success = run_release(version=args.version, sign=args.sign, cert_path=args.cert)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
