"""
MSIX Build-Skript für TaskSense.

Dieses Skript erstellt ein MSIX-Paket (Microsoft Store Format).

Voraussetzungen:
    - MakeAppx Tool (Teil von Windows SDK)
    - SignTool (Optional, für digitale Signatur)
    - PyInstaller (für .exe Erstellung)

Verwendung:
    python build_msix.py [--sign]
    
    --sign: Digitale Signatur hinzufügen (erfordert Zertifikat)
"""

import subprocess
import sys
import os
import shutil
import json
from pathlib import Path


class MSIXBuilder:
    """Builder für MSIX-Pakete."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build" / "msix"
        self.dist_dir = self.project_root / "dist"
        self.assets_dir = self.project_root / "Assets"
        self.output_dir = self.project_root / "dist"
        self.makeappx = None  # Wird in check_requirements gesetzt
        
    def check_requirements(self):
        """Prüft, ob alle erforderlichen Tools verfügbar sind."""
        print("🔍 Prüfe erforderliche Tools...")
        
        # Versuche MakeAppx zu finden
        makeappx_paths = [
            "MakeAppx",  # Im PATH
            "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64\\MakeAppx.exe",
            "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x64\\MakeAppx.exe",
            "C:\\Program Files\\Windows Kits\\10\\bin\\10.0.22621.0\\x64\\MakeAppx.exe",
        ]
        
        makeappx_found = None
        for path in makeappx_paths:
            try:
                result = subprocess.run([path, '/?'], capture_output=True, timeout=5)
                if result.returncode == 0 or "Usage" in result.stdout.decode() or "Usage" in result.stderr.decode():
                    makeappx_found = path
                    print(f"✓ MakeAppx gefunden: {path}")
                    self.makeappx = path
                    break
            except:
                continue
        
        if not makeappx_found:
            print("✗ MakeAppx nicht gefunden!")
            print("  Bitte installiere das Windows SDK:")
            print("  https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/")
            print("  Oder kopiere MakeAppx.exe in den PATH")
            return False
        
        return True
    
    def create_app_structure(self):
        """Erstellt die Verzeichnisstruktur für MSIX."""
        print("\n📁 Erstelle MSIX-Struktur...")
        
        # Stelle sicher, dass build dir existiert
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # Erstelle erforderliche Unterverzeichnisse
        (self.build_dir / "Assets").mkdir(exist_ok=True)
        
        # Kopiere AppxManifest.xml
        manifest_src = self.project_root / "AppxManifest.xml"
        manifest_dst = self.build_dir / "AppxManifest.xml"
        if manifest_src.exists():
            shutil.copy(manifest_src, manifest_dst)
            print(f"✓ Manifest kopiert: {manifest_dst}")
        else:
            print(f"✗ Manifest nicht gefunden: {manifest_src}")
            return False
        
        # Erstelle oder kopiere Assets
        self._create_assets()
        
        return True
    
    def _create_assets(self):
        """Erstellt oder kopiert Asset-Dateien."""
        print("\n🎨 Erstelle Assets...")
        
        assets_dir = self.build_dir / "Assets"
        
        # Definiere erforderliche Assets
        assets_needed = {
            "StoreLogo.png": (50, 50),
            "Square44x44Logo.png": (44, 44),
            "Square150x150Logo.png": (150, 150),
            "SplashScreen.png": (620, 300),
        }
        
        # Versuche Assets von bestehender Quelle zu kopieren oder erstelle Platzhalter
        for asset_name, size in assets_needed.items():
            asset_path = assets_dir / asset_name
            src_path = self.project_root / "Assets" / asset_name
            
            if src_path.exists():
                shutil.copy(src_path, asset_path)
                print(f"✓ Asset kopiert: {asset_name}")
            else:
                self._create_placeholder_image(asset_path, asset_name, size)
    
    def _create_placeholder_image(self, path: Path, name: str, size: tuple):
        """Erstellt ein Platzhalter-PNG-Bild."""
        try:
            from PIL import Image, ImageDraw
            
            # Erstelle Bild mit Farbverlauf
            img = Image.new('RGB', size, color=(100, 150, 200))
            draw = ImageDraw.Draw(img)
            
            # Schreibe Text
            text = name.replace('.png', '')
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255))
            
            img.save(path)
            print(f"✓ Platzhalter erstellt: {name}")
        except ImportError:
            print(f"⚠ PIL nicht installiert - überspringe {name}")
            print("  Bitte manuell Asset hinzufügen oder: pip install Pillow")
    
    def build_exe(self):
        """Erstellt die .exe mit PyInstaller."""
        print("\n🔨 Baue .exe mit PyInstaller...")
        
        exe_path = self.dist_dir / "TaskSense.exe"
        
        # Prüfe ob bereits vorhanden
        if exe_path.exists():
            print(f"✓ .exe bereits vorhanden: {exe_path}")
            return True
        
        # Baue mit PyInstaller
        try:
            result = subprocess.run(
                [sys.executable, "build.py"],
                cwd=self.project_root,
                capture_output=False
            )
            
            if result.returncode == 0:
                print("✓ .exe erfolgreich erstellt")
                return True
            else:
                print("✗ .exe Build fehlgeschlagen")
                return False
        except Exception as e:
            print(f"✗ Fehler beim Ausführen von build.py: {e}")
            return False
    
    def copy_executable(self):
        """Kopiert die .exe in das MSIX-Verzeichnis."""
        print("\n📦 Kopiere Executable...")
        
        exe_src = self.dist_dir / "TaskSense.exe"
        exe_dst = self.build_dir / "TaskSense.exe"
        
        if not exe_src.exists():
            print(f"✗ .exe nicht gefunden: {exe_src}")
            return False
        
        shutil.copy(exe_src, exe_dst)
        print(f"✓ Executable kopiert: {exe_dst}")
        
        return True
    
    def create_msix_package(self):
        """Erstellt das MSIX-Paket mit MakeAppx."""
        print("\n📦 Erstelle MSIX-Paket...")
        
        output_msix = self.output_dir / "TaskSense.msix"
        
        # Stelle sicher dass output_dir existiert
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Debug: Prüfe ob Build-Dateien existieren
        print(f"  Build-Verzeichnis: {self.build_dir}")
        if not self.build_dir.exists():
            print(f"  ✗ Build-Verzeichnis existiert nicht!")
            return False
        
        manifest = self.build_dir / "AppxManifest.xml"
        if not manifest.exists():
            print(f"  ✗ AppxManifest.xml nicht gefunden: {manifest}")
            return False
        
        assets = self.build_dir / "Assets"
        if not assets.exists():
            print(f"  ✗ Assets-Verzeichnis nicht gefunden: {assets}")
            return False
        
        print(f"  ✓ Verzeichnisstruktur OK")
        
        try:
            cmd = [
                self.makeappx,
                "pack",
                "/d", str(self.build_dir),
                "/p", str(output_msix),
                "/o",
            ]
            
            print(f"  Befehl: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ MSIX-Paket erstellt: {output_msix}")
                if output_msix.exists():
                    size = output_msix.stat().st_size / (1024*1024)
                    print(f"  Größe: {size:.1f} MB")
                return True
            else:
                print(f"✗ MakeAppx Fehler ({result.returncode})")
                if result.stdout:
                    print(f"  stdout: {result.stdout}")
                if result.stderr:
                    print(f"  stderr: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Fehler beim Erstellen des MSIX-Pakets: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def sign_msix(self, cert_path: str = None):
        """Signiert das MSIX-Paket digital (optional)."""
        print("\n🔐 Signiere MSIX-Paket...")
        
        output_msix = self.output_dir / "TaskSense.msix"
        
        if not output_msix.exists():
            print("✗ MSIX-Paket nicht gefunden")
            return False
        
        # Wenn kein Zertifikat, überspringe
        if cert_path is None:
            print("⚠ Kein Zertifikat angegeben - Signierung übersprungen")
            print("  Für Microsoft Store Upload ist eine gültige Signatur erforderlich")
            return True
        
        try:
            cmd = [
                "SignTool",
                "sign",
                "/f", cert_path,
                "/fd", "SHA256",
                str(output_msix),
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ MSIX signiert: {output_msix}")
                return True
            else:
                print(f"✗ SignTool Fehler: {result.stderr}")
                return False
        except FileNotFoundError:
            print("✗ SignTool nicht gefunden")
            print("  Installiere Windows SDK für SignTool")
            return False
        except Exception as e:
            print(f"✗ Fehler beim Signieren: {e}")
            return False
    
    def build(self, sign: bool = False, cert_path: str = None):
        """Führt den kompletten Build-Prozess aus."""
        print("=" * 60)
        print("TaskSense MSIX Build")
        print("=" * 60)
        
        # Schritt 1: Prüfe Requirements
        print("\n📋 Schritt 1: Prüfe Requirements...")
        if not self.check_requirements():
            print("\n❌ Build abgebrochen - fehlende Tools")
            return False
        
        # Schritt 2: Erstelle Struktur
        print("\n📋 Schritt 2: Erstelle Struktur...")
        if not self.create_app_structure():
            print("\n❌ Build abgebrochen - Struktur-Fehler")
            return False
        
        # Schritt 3: Baue .exe
        print("\n📋 Schritt 3: Baue .exe...")
        if not self.build_exe():
            print("\n❌ Build abgebrochen - .exe Fehler")
            return False
        
        # Schritt 4: Kopiere .exe
        print("\n📋 Schritt 4: Kopiere .exe...")
        if not self.copy_executable():
            print("\n❌ Build abgebrochen - Copy Fehler")
            return False
        
        # Schritt 5: Erstelle MSIX
        print("\n📋 Schritt 5: Erstelle MSIX...")
        if not self.create_msix_package():
            print("\n❌ Build abgebrochen - MSIX Fehler")
            return False
        
        # Schritt 6: Signiere (optional)
        if sign:
            print("\n📋 Schritt 6: Signiere MSIX...")
            if not self.sign_msix(cert_path):
                print("⚠ Warnung: Signierung fehlgeschlagen")
        
        print("\n" + "=" * 60)
        print("✓ MSIX Build erfolgreich!")
        print("=" * 60)
        print(f"\nAusgabe: {self.output_dir / 'TaskSense.msix'}")
        print("3. Lade MSIX hoch")
        print("4. Durchlaufe Zertifizierungsprozess")
        
        return True


def main():
    """Haupteinstiegspunkt."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Baue TaskSense als MSIX-Paket")
    parser.add_argument("--sign", action="store_true", help="Digitale Signatur hinzufügen")
    parser.add_argument("--cert", type=str, help="Pfad zum Zertifikat (.pfx)")
    
    args = parser.parse_args()
    
    builder = MSIXBuilder()
    success = builder.build(sign=args.sign, cert_path=args.cert)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
