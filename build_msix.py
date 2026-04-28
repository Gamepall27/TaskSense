"""
MSIX Build-Skript für TaskSense Lite und Pro.

Verwendung:
    python build_msix.py --edition lite
    python build_msix.py --edition pro --version 1.0.4
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from build_common import (
    customize_manifest_content,
    get_msix_filename,
    get_product,
    normalize_manifest_version,
    read_version_from_manifest,
)


class MSIXBuilder:
    """Builder für editionsspezifische MSIX-Pakete."""

    def __init__(self, edition: str, version: str):
        self.project_root = Path(__file__).parent
        self.product = get_product(edition)
        self.version_input = version
        self.version_manifest = normalize_manifest_version(version)

        self.build_dir = self.project_root / "build" / "msix" / self.product.edition
        self.dist_dir = self.project_root / "dist"
        self.output_dir = self.dist_dir / self.version_input
        self.assets_dir = self.project_root / "Assets"
        self.output_msix = self.output_dir / get_msix_filename(self.product, self.version_input)
        self.makeappx = None

    def check_requirements(self) -> bool:
        """Prüft, ob alle erforderlichen Tools verfügbar sind."""
        print("🔍 Prüfe erforderliche Tools...")

        makeappx_paths = [
            "MakeAppx",
            "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64\\MakeAppx.exe",
            "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x64\\MakeAppx.exe",
            "C:\\Program Files\\Windows Kits\\10\\bin\\10.0.22621.0\\x64\\MakeAppx.exe",
        ]

        for path in makeappx_paths:
            try:
                result = subprocess.run([path, "/?"], capture_output=True, timeout=5)
                stdout = result.stdout.decode(errors="ignore")
                stderr = result.stderr.decode(errors="ignore")
                if result.returncode == 0 or "Usage" in stdout or "Usage" in stderr:
                    self.makeappx = path
                    print(f"✓ MakeAppx gefunden: {path}")
                    return True
            except Exception:
                continue

        print("✗ MakeAppx nicht gefunden!")
        print("  Bitte installiere das Windows SDK:")
        print("  https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/")
        return False

    def create_app_structure(self) -> bool:
        """Erstellt die Verzeichnisstruktur für MSIX."""
        print("\n📁 Erstelle MSIX-Struktur...")
        self.build_dir.mkdir(parents=True, exist_ok=True)
        (self.build_dir / "Assets").mkdir(exist_ok=True)

        manifest_src = self.project_root / "AppxManifest.xml"
        manifest_dst = self.build_dir / "AppxManifest.xml"
        if not manifest_src.exists():
            print(f"✗ Manifest nicht gefunden: {manifest_src}")
            return False

        manifest_content = manifest_src.read_text(encoding="utf-8")
        manifest_content = customize_manifest_content(
            manifest_content,
            self.product,
            self.version_input,
        )
        manifest_dst.write_text(manifest_content, encoding="utf-8")

        print(f"✓ Manifest angepasst: {manifest_dst}")
        print(f"  Edition: {self.product.display_name}")
        print(f"  Version gesetzt auf: {self.version_manifest}")

        self._create_assets()
        return True

    def _create_assets(self):
        """Erstellt oder kopiert Asset-Dateien."""
        print("\n🎨 Erstelle Assets...")

        assets_needed = {
            "StoreLogo.png": (50, 50),
            "Square44x44Logo.png": (44, 44),
            "Square150x150Logo.png": (150, 150),
            "SplashScreen.png": (620, 300),
        }

        for asset_name, size in assets_needed.items():
            asset_path = self.build_dir / "Assets" / asset_name
            src_path = self.assets_dir / asset_name

            if src_path.exists():
                shutil.copy(src_path, asset_path)
                print(f"✓ Asset kopiert: {asset_name}")
            else:
                self._create_placeholder_image(asset_path, asset_name, size)

    def _create_placeholder_image(self, path: Path, name: str, size: tuple):
        """Erstellt ein Platzhalter-PNG-Bild."""
        print(f"⚠ Asset nicht gefunden: {name}")
        try:
            from PIL import Image, ImageDraw

            img = Image.new("RGB", size, color=(100, 150, 200))
            draw = ImageDraw.Draw(img)
            text = name.replace(".png", "")
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255))
            img.save(path)
            print(f"  → Platzhalter erstellt: {name}")
        except ImportError:
            print(f"⚠ PIL nicht installiert - überspringe {name}")

    def build_exe(self) -> bool:
        """Erstellt die editionsspezifische .exe mit PyInstaller."""
        print("\n🔨 Baue .exe mit PyInstaller...")

        exe_path = self.dist_dir / f"{self.product.exe_name}.exe"
        if exe_path.exists():
            print(f"✓ .exe bereits vorhanden: {exe_path}")
            return True

        try:
            result = subprocess.run(
                [sys.executable, "build.py", "--edition", self.product.edition],
                cwd=self.project_root,
                capture_output=False,
            )
            if result.returncode == 0:
                print("✓ .exe erfolgreich erstellt")
                return True

            print("✗ .exe Build fehlgeschlagen")
            return False
        except Exception as error:
            print(f"✗ Fehler beim Ausführen von build.py: {error}")
            return False

    def copy_executable(self) -> bool:
        """Kopiert die .exe in das MSIX-Verzeichnis."""
        print("\n📦 Kopiere Executable...")

        exe_src = self.dist_dir / f"{self.product.exe_name}.exe"
        exe_dst = self.build_dir / f"{self.product.exe_name}.exe"

        if not exe_src.exists():
            print(f"✗ .exe nicht gefunden: {exe_src}")
            return False

        shutil.copy(exe_src, exe_dst)
        print(f"✓ Executable kopiert: {exe_dst}")
        return True

    def create_msix_package(self) -> bool:
        """Erstellt das MSIX-Paket mit MakeAppx."""
        print("\n📦 Erstelle MSIX-Paket...")
        print(f"  Produkt: {self.product.display_name}")
        print(f"  Version: {self.version_manifest} (Ordner: {self.version_input})")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Output-Verzeichnis: {self.output_dir}")

        if self.output_msix.exists():
            self.output_msix.unlink()

        try:
            cmd = [
                self.makeappx,
                "pack",
                "/d", str(self.build_dir),
                "/p", str(self.output_msix),
                "/o",
            ]
            print(f"  Befehl: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✓ MSIX-Paket erstellt: {self.output_msix}")
                if self.output_msix.exists():
                    size = self.output_msix.stat().st_size / (1024 * 1024)
                    print(f"  Größe: {size:.1f} MB")
                return True

            print(f"✗ MakeAppx Fehler ({result.returncode})")
            if result.stdout:
                print(f"  stdout: {result.stdout}")
            if result.stderr:
                print(f"  stderr: {result.stderr}")
            return False
        except Exception as error:
            print(f"✗ Fehler beim Erstellen des MSIX-Pakets: {error}")
            return False

    def sign_msix(self, cert_path: str = None) -> bool:
        """Signiert das MSIX-Paket digital (optional)."""
        print("\n🔐 Signiere MSIX-Paket...")

        if not self.output_msix.exists():
            print("✗ MSIX-Paket nicht gefunden")
            return False

        if cert_path is None:
            print("⚠ Kein Zertifikat angegeben - Signierung übersprungen")
            return True

        try:
            cmd = [
                "SignTool",
                "sign",
                "/f", cert_path,
                "/fd", "SHA256",
                str(self.output_msix),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✓ MSIX signiert: {self.output_msix}")
                return True

            print(f"✗ SignTool Fehler: {result.stderr}")
            return False
        except FileNotFoundError:
            print("✗ SignTool nicht gefunden")
            return False
        except Exception as error:
            print(f"✗ Fehler beim Signieren: {error}")
            return False

    def build(self, sign: bool = False, cert_path: str = None) -> bool:
        """Führt den kompletten Build-Prozess aus."""
        print("=" * 60)
        print(f"{self.product.display_name} MSIX Build")
        print("=" * 60)

        print("\n📋 Schritt 1: Prüfe Requirements...")
        if not self.check_requirements():
            print("\n❌ Build abgebrochen - fehlende Tools")
            return False

        print("\n📋 Schritt 2: Erstelle Struktur...")
        if not self.create_app_structure():
            print("\n❌ Build abgebrochen - Struktur-Fehler")
            return False

        print("\n📋 Schritt 3: Baue .exe...")
        if not self.build_exe():
            print("\n❌ Build abgebrochen - .exe Fehler")
            return False

        print("\n📋 Schritt 4: Kopiere .exe...")
        if not self.copy_executable():
            print("\n❌ Build abgebrochen - Copy Fehler")
            return False

        print("\n📋 Schritt 5: Erstelle MSIX...")
        if not self.create_msix_package():
            print("\n❌ Build abgebrochen - MSIX Fehler")
            return False

        if sign:
            print("\n📋 Schritt 6: Signiere MSIX...")
            if not self.sign_msix(cert_path):
                print("⚠ Warnung: Signierung fehlgeschlagen")

        print("\n" + "=" * 60)
        print("✓ MSIX Build erfolgreich!")
        print("=" * 60)
        print(f"\nAusgabe: {self.output_msix}")
        return True


def main():
    """Haupteinstiegspunkt."""
    parser = argparse.ArgumentParser(description="Baue TaskSense Lite oder Pro als MSIX-Paket")
    parser.add_argument(
        "--edition",
        choices=("lite", "pro"),
        default="pro",
        help="Zu bauende Produktedition",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Versionsnummer (wenn nicht angegeben: aus AppxManifest.xml)",
    )
    parser.add_argument("--sign", action="store_true", help="Digitale Signatur hinzufügen")
    parser.add_argument("--cert", type=str, help="Pfad zum Zertifikat (.pfx)")

    args = parser.parse_args()

    version = args.version or read_version_from_manifest(Path(__file__).parent)
    if not args.version:
        print(f"📖 Version aus AppxManifest.xml gelesen: {version}\n")

    builder = MSIXBuilder(edition=args.edition, version=version)
    success = builder.build(sign=args.sign, cert_path=args.cert)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
