#!/usr/bin/env python3
"""
TaskSense Release Builder - All-in-One MSIX Paketierung.

Verwendung:
  python release.py --edition lite
  python release.py --edition pro --version 1.0.4 --sign --cert certs/cert.pfx
"""

import argparse
import subprocess
import sys
from pathlib import Path

from build_common import get_msix_filename, get_product, read_version_from_manifest


class TaskSenseReleaseBuilder:
    """All-in-One MSIX Release Builder."""

    def __init__(self, edition: str, version: str, verbose: bool = False):
        self.project_root = Path(__file__).parent
        self.product = get_product(edition)
        self.version = version
        self.verbose = verbose

    def run_command(self, cmd: list) -> bool:
        """Führt einen Befehl aus und prüft den Exit Code."""
        if self.verbose:
            print(f"ℹ Befehl: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=False)
            return result.returncode == 0
        except Exception as error:
            print(f"✗ Fehler beim Ausführen: {error}")
            return False

    def build(self, skip_exe: bool = False, sign: bool = False, cert_path: str = None) -> bool:
        """Führt den kompletten Release-Build aus."""
        print("\n" + "╔" + "═" * 58 + "╗")
        print(f"║{(' ' + self.product.display_name + ' MSIX Release Builder').center(58)}║")
        print("╚" + "═" * 58 + "╝")

        if not skip_exe:
            print("\n📦 Schritt 1: Baue .exe...")
            build_cmd = [
                sys.executable,
                str(self.project_root / "build.py"),
                "--edition",
                self.product.edition,
            ]
            if not self.run_command(build_cmd):
                print("✗ .exe Build fehlgeschlagen")
                return False
        else:
            print("\nℹ Überspringe .exe Build")

        print("\n📦 Schritt 2: Baue MSIX...")
        msix_cmd = [
            sys.executable,
            str(self.project_root / "build_msix.py"),
            "--edition",
            self.product.edition,
            "--version",
            self.version,
        ]

        if sign:
            msix_cmd.append("--sign")
            if cert_path:
                msix_cmd.extend(["--cert", cert_path])

        if not self.run_command(msix_cmd):
            print("✗ MSIX Build fehlgeschlagen")
            return False

        output_msix = self.project_root / "dist" / self.version / get_msix_filename(self.product, self.version)
        print("\n" + "═" * 60)
        print("📦 MSIX-Datei ist bereit für Microsoft Store Upload!")
        print("═" * 60)
        print(f"Datei: {output_msix}")
        print(f"Edition: {self.product.display_name}")
        print(f"Version: {self.version}")

        return True


def main():
    """Haupteinstiegspunkt."""
    parser = argparse.ArgumentParser(
        description="TaskSense Release Builder - All-in-One MSIX Paketierung",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python release.py --edition lite
  python release.py --edition pro --version 1.0.1
  python release.py --edition lite --sign --cert certs/cert.pfx
  python release.py --edition pro --skip-exe --verbose
        """,
    )

    parser.add_argument("--edition", choices=("lite", "pro"), default="pro")
    parser.add_argument(
        "--version",
        default=None,
        help="Versionsnummer (wenn nicht angegeben: aus AppxManifest.xml)",
    )
    parser.add_argument("--sign", action="store_true", help="Mit Zertifikat signieren")
    parser.add_argument("--cert", type=str, help="Zertifikat-Pfad (.pfx)")
    parser.add_argument("--skip-exe", action="store_true", help="Nutze existierende .exe")
    parser.add_argument("--verbose", action="store_true", help="Detaillierte Ausgabe")

    args = parser.parse_args()
    version = args.version or read_version_from_manifest(Path(__file__).parent)

    builder = TaskSenseReleaseBuilder(
        edition=args.edition,
        version=version,
        verbose=args.verbose,
    )
    success = builder.build(
        skip_exe=args.skip_exe,
        sign=args.sign,
        cert_path=args.cert,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
