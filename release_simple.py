#!/usr/bin/env python3
"""
TaskSense MSIX Release Builder - Simplified Version.

Verwendung:
  python release_simple.py --edition lite
  python release_simple.py --edition pro --version 1.0.4
"""

import argparse
import subprocess
import sys
from pathlib import Path

from build_common import get_msix_filename, get_product, read_version_from_manifest


def run_release(edition: str, version: str = None, sign: bool = False, cert_path: str = None):
    """Führt den kompletten Release aus."""
    project_root = Path(__file__).parent
    product = get_product(edition)

    if not version:
        version = read_version_from_manifest(project_root)
        print(f"📖 Version aus AppxManifest.xml gelesen: {version}\n")

    print("\n" + "=" * 70)
    print(f"🚀 {product.display_name} MSIX Release Builder".center(70))
    print("=" * 70 + "\n")

    print("📦 Schritt 1: Baue .exe mit PyInstaller...")
    print("-" * 70)
    try:
        result = subprocess.run(
            [sys.executable, str(project_root / "build.py"), "--edition", product.edition],
            check=False,
        )
        if result.returncode != 0:
            print("❌ .exe Build fehlgeschlagen")
            return False
    except Exception as error:
        print(f"❌ Fehler: {error}")
        return False

    print("\n📦 Schritt 2: Baue MSIX-Paket mit MakeAppx...")
    print("-" * 70)

    cmd = [
        sys.executable,
        str(project_root / "build_msix.py"),
        "--edition",
        product.edition,
        "--version",
        version,
    ]

    if sign and cert_path:
        cmd.extend(["--sign", "--cert", cert_path])

    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print("❌ MSIX Build fehlgeschlagen")
            return False
    except Exception as error:
        print(f"❌ Fehler: {error}")
        return False

    print("\n" + "=" * 70)
    print("✅ MSIX Release erfolgreich!".center(70))
    print("=" * 70 + "\n")

    msix_path = project_root / "dist" / version / get_msix_filename(product, version)
    if msix_path.exists():
        size = msix_path.stat().st_size / (1024 * 1024)
        print(f"📁 Ausgabe: {msix_path}")
        print(f"   Größe: {size:.1f} MB")
        print(f"   Version: {version}")
        print(f"   Edition: {product.display_name}\n")

    return True


def main():
    """Haupteinstiegspunkt."""
    parser = argparse.ArgumentParser(
        description="TaskSense MSIX Release Builder",
        epilog="Beispiel: python release_simple.py --edition lite --version 1.0.4",
    )
    parser.add_argument("--edition", choices=("lite", "pro"), default="pro")
    parser.add_argument(
        "--version",
        default=None,
        help="Versionsnummer (wenn nicht angegeben: aus AppxManifest.xml)",
    )
    parser.add_argument("--sign", action="store_true", help="Mit Zertifikat signieren")
    parser.add_argument("--cert", type=str, help="Zertifikat-Pfad (.pfx)")

    args = parser.parse_args()

    success = run_release(
        edition=args.edition,
        version=args.version,
        sign=args.sign,
        cert_path=args.cert,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
