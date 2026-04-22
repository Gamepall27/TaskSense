#!/usr/bin/env python3
"""
TaskSense MSIX Release Builder - Simplified Version

Nutzt existierende build.py und build_msix.py - ohne Umwege!

Verwendung:
  python release_simple.py
  python release_simple.py --version 1.0.1
  python release_simple.py --sign --cert certs/cert.pfx

Ergebnis: dist/TaskSense.msix
"""

import subprocess
import sys
import time
from pathlib import Path


def print_progress(step: int, total: int, title: str):
    """Zeigt einen hübschen Progress Bar."""
    percent = (step / total) * 100
    filled = int(50 * step / total)
    bar = "█" * filled + "░" * (50 - filled)
    print(f"\r{title} │{bar}│ {percent:>6.1f}%", end="", flush=True)


def run_release(version: str = "1.0.0", sign: bool = False, cert_path: str = None):
    """Führt den kompletten Release aus."""
    
    print("\n" + "=" * 70)
    print("🚀 TaskSense MSIX Release Builder".center(70))
    print("=" * 70 + "\n")
    
    project_root = Path(__file__).parent
    total_steps = 2
    
    # Schritt 1: Baue .exe
    print("\n📦 Schritt 1: Baue .exe mit PyInstaller...")
    print("-" * 70)
    
    try:
        print_progress(0, total_steps, "Gesamt")
        result = subprocess.run([sys.executable, str(project_root / "build.py")], check=False)
        print()  # Neue Zeile nach .exe Build
        if result.returncode != 0:
            print("❌ .exe Build fehlgeschlagen")
            return False
        print_progress(1, total_steps, "Gesamt")
        print()  # Neue Zeile
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        return False
    
    # Schritt 2: Baue MSIX
    print("\n📦 Schritt 2: Baue MSIX-Paket mit MakeAppx...")
    print("-" * 70)
    
    cmd = [sys.executable, str(project_root / "build_msix.py")]
    
    if sign and cert_path:
        cmd.extend(["--sign", "--cert", cert_path])
    
    try:
        result = subprocess.run(cmd, check=False)
        print()  # Neue Zeile nach MSIX Build
        if result.returncode != 0:
            print("❌ MSIX Build fehlgeschlagen")
            return False
        print_progress(total_steps, total_steps, "Gesamt")
        print()  # Neue Zeile
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        return False
    
    # Erfolg!
    print("\n" + "=" * 70)
    print("✅ MSIX Release erfolgreich!".center(70))
    print("=" * 70)
    
    msix_path = project_root / "dist" / "TaskSense.msix"
    if msix_path.exists():
        size = msix_path.stat().st_size / (1024 * 1024)
        print(f"\n📁 Ausgabe: {msix_path}")
        print(f"   Größe: {size:.1f} MB")
        print(f"   Version: {version}")
    
    print("\n🚀 Bereit für Microsoft Store Upload!")
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
