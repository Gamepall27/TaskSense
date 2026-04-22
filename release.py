#!/usr/bin/env python3
"""
TaskSense Release Builder - All-in-One MSIX Paketierung

Dieser Befehl erledigt ALLES:
  python release.py
  
Ergebnis: dist/TaskSense.msix (hochladbar für Microsoft Store)

Optionen:
  --version VERSION    Versionsnummer (z.B. 1.0.1) [default: 1.0.0]
  --sign               Mit Zertifikat signieren
  --cert PATH          Zertifikat-Pfad (.pfx Datei)
  --skip-exe           Nutze existierende .exe (skip PyInstaller)
  --verbose            Detaillierte Ausgabe
"""

import subprocess
import sys
import os
import shutil
import json
from pathlib import Path
from typing import Optional, Tuple


class TaskSenseReleaseBuilder:
    """All-in-One MSIX Release Builder."""
    
    def __init__(self, version: str = "1.0.0", verbose: bool = False):
        self.project_root = Path(__file__).parent
        self.version = version
        self.verbose = verbose
        self.log_indent = 0
        
        # Verzeichnisse
        self.build_dir = self.project_root / "build" / "msix"
        self.dist_dir = self.project_root / "dist"
        self.assets_dir = self.project_root / "Assets"
        
        # State
        self.steps_completed = []
        
    def log(self, msg: str, level: str = "info"):
        """Protokollierung mit Formatting."""
        indent = "  " * self.log_indent
        
        if level == "info":
            print(f"{indent}ℹ {msg}")
        elif level == "success":
            print(f"{indent}✓ {msg}")
        elif level == "warning":
            print(f"{indent}⚠ {msg}")
        elif level == "error":
            print(f"{indent}✗ {msg}")
        elif level == "step":
            print(f"\n{indent}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"{indent}📌 {msg}")
            print(f"{indent}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def run_command(self, cmd: list, description: str = "") -> bool:
        """Führt Befehl aus und prüft auf Fehler."""
        if self.verbose:
            self.log(f"Befehl: {' '.join(cmd)}", "info")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.log(f"Fehler: {result.stderr if result.stderr else 'Exit Code ' + str(result.returncode)}", "error")
                return False
            
            return True
        except Exception as e:
            self.log(f"Fehler beim Ausführen: {e}", "error")
            return False
    
    def check_requirements(self) -> bool:
        """Prüft alle Voraussetzungen."""
        self.log("Prüfe Voraussetzungen", "step")
        self.log_indent += 1
        
        # Python
        self.log("Python verfügbar")
        
        # PyInstaller
        try:
            import PyInstaller
            self.log("PyInstaller installiert", "success")
        except ImportError:
            self.log("PyInstaller nicht installiert!", "error")
            self.log("Installiere: pip install pyinstaller", "error")
            self.log_indent -= 1
            return False
        
        # MakeAppx
        makeappx_found = False
        possible_paths = [
            "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22621.0\\x64\\MakeAppx.exe",
            "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x64\\MakeAppx.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # Füge zu PATH hinzu
                if path not in os.environ['PATH']:
                    os.environ['PATH'] += f";{os.path.dirname(path)}"
                self.log("MakeAppx gefunden", "success")
                makeappx_found = True
                break
        
        if not makeappx_found:
            self.log("MakeAppx nicht gefunden!", "warning")
            self.log("Installiere Windows SDK von: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/", "warning")
            self.log_indent -= 1
            return False
        
        self.log_indent -= 1
        return True
    
    def build_executable(self, skip_exe: bool = False) -> bool:
        """Baut die .exe mit PyInstaller."""
        self.log("Baue ausführbare Datei", "step")
        self.log_indent += 1
        
        exe_path = self.dist_dir / "TaskSense.exe"
        
        if skip_exe and exe_path.exists():
            self.log("Nutze existierende .exe", "info")
            self.log_indent -= 1
            return True
        
        self.log("Starte PyInstaller...")
        
        # Build-Kommand
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "TaskSense",
            "--hidden-import=PyQt6.QtCore",
            "--hidden-import=PyQt6.QtGui",
            "--hidden-import=PyQt6.QtWidgets",
            "--hidden-import=psutil",
            "--hidden-import=win10toast",
            "--distpath", str(self.dist_dir),
            "--buildpath", str(self.project_root / "build" / "pyinstaller"),
            "--workpath", str(self.project_root / "build" / "pyinstaller"),
            str(self.project_root / "main.py")
        ]
        
        if not self.run_command(cmd):
            self.log("PyInstaller Build fehlgeschlagen", "error")
            self.log_indent -= 1
            return False
        
        if not exe_path.exists():
            self.log(f".exe nicht erstellt: {exe_path}", "error")
            self.log_indent -= 1
            return False
        
        exe_size = exe_path.stat().st_size / (1024 * 1024)
        self.log(f".exe erstellt ({exe_size:.1f} MB)", "success")
        
        self.log_indent -= 1
        return True
    
    def prepare_msix_structure(self) -> bool:
        """Bereitet die MSIX-Verzeichnisstruktur vor."""
        self.log("Bereite MSIX-Struktur vor", "step")
        self.log_indent += 1
        
        # Erstelle Verzeichnisse
        self.build_dir.mkdir(parents=True, exist_ok=True)
        (self.build_dir / "Assets").mkdir(exist_ok=True)
        
        self.log(f"Verzeichnis erstellt: {self.build_dir}")
        
        # Kopiere Manifest
        manifest_src = self.project_root / "AppxManifest.xml"
        manifest_dst = self.build_dir / "AppxManifest.xml"
        
        if not manifest_src.exists():
            self.log("AppxManifest.xml nicht gefunden!", "error")
            self.log_indent -= 1
            return False
        
        shutil.copy(manifest_src, manifest_dst)
        self.log("Manifest kopiert", "success")
        
        # Kopiere .exe
        exe_src = self.dist_dir / "TaskSense.exe"
        exe_dst = self.build_dir / "TaskSense.exe"
        
        if not exe_src.exists():
            self.log(f".exe nicht gefunden: {exe_src}", "error")
            self.log_indent -= 1
            return False
        
        shutil.copy(exe_src, exe_dst)
        self.log(".exe kopiert", "success")
        
        # Erstelle/kopiere Assets
        self._create_assets()
        
        self.log_indent -= 1
        return True
    
    def _create_assets(self):
        """Erstellt oder kopiert Asset-Dateien."""
        assets_needed = {
            "StoreLogo.png": (50, 50),
            "Square44x44Logo.png": (44, 44),
            "Square150x150Logo.png": (150, 150),
            "SplashScreen.png": (620, 300),
        }
        
        for asset_name, size in assets_needed.items():
            src_path = self.assets_dir / asset_name
            dst_path = self.build_dir / "Assets" / asset_name
            
            if src_path.exists():
                shutil.copy(src_path, dst_path)
                self.log(f"Asset kopiert: {asset_name}")
            else:
                # Erstelle Platzhalter
                self._create_placeholder_image(dst_path, asset_name, size)
    
    def _create_placeholder_image(self, path: Path, name: str, size: Tuple[int, int]):
        """Erstellt Platzhalter-PNG."""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', size, color=(100, 150, 200))
            draw = ImageDraw.Draw(img)
            
            text = name.replace('.png', '')
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255))
            
            img.save(path)
            self.log(f"Asset erstellt: {name}")
        except ImportError:
            self.log(f"PIL nicht installiert - überspringe Asset {name}", "warning")
    
    def create_msix_package(self) -> bool:
        """Erstellt das MSIX-Paket."""
        self.log("Erstelle MSIX-Paket", "step")
        self.log_indent += 1
        
        output_msix = self.dist_dir / "TaskSense.msix"
        
        # Stelle sicher dass dist existiert
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        
        # Entferne alte MSIX
        if output_msix.exists():
            output_msix.unlink()
            self.log("Alte MSIX gelöscht")
        
        # MakeAppx Befehl
        cmd = [
            "MakeAppx",
            "pack",
            "/d", str(self.build_dir),
            "/p", str(output_msix),
            "/o",  # Überschreibe
        ]
        
        self.log("Starte MakeAppx...")
        
        if not self.run_command(cmd):
            self.log("MakeAppx Fehler - MSIX konnte nicht erstellt werden", "error")
            self.log_indent -= 1
            return False
        
        if not output_msix.exists():
            self.log("MSIX nicht erstellt!", "error")
            self.log_indent -= 1
            return False
        
        msix_size = output_msix.stat().st_size / (1024 * 1024)
        self.log(f"MSIX erstellt ({msix_size:.1f} MB)", "success")
        
        self.log_indent -= 1
        return True
    
    def sign_msix(self, cert_path: Optional[str]) -> bool:
        """Signiert die MSIX (optional)."""
        if not cert_path:
            self.log("Signatur übersprungen (kein Zertifikat)", "info")
            return True
        
        self.log("Signiere MSIX", "step")
        self.log_indent += 1
        
        output_msix = self.dist_dir / "TaskSense.msix"
        cert_file = Path(cert_path)
        
        if not cert_file.exists():
            self.log(f"Zertifikat nicht gefunden: {cert_path}", "error")
            self.log_indent -= 1
            return False
        
        # SignTool Befehl
        cmd = [
            "SignTool",
            "sign",
            "/f", str(cert_file),
            "/fd", "SHA256",
            str(output_msix),
        ]
        
        self.log("Starte SignTool...")
        
        if not self.run_command(cmd):
            self.log("SignTool Fehler - MSIX konnte nicht signiert werden", "warning")
            self.log_indent -= 1
            return False
        
        self.log("MSIX signiert", "success")
        self.log_indent -= 1
        return True
    
    def show_summary(self) -> None:
        """Zeigt Zusammenfassung."""
        self.log("🎉 Release Build erfolgreich!", "step")
        self.log_indent += 1
        
        output_msix = self.dist_dir / "TaskSense.msix"
        msix_size = output_msix.stat().st_size / (1024 * 1024)
        
        self.log(f"Ausgabe: {output_msix}", "success")
        self.log(f"Größe: {msix_size:.1f} MB", "success")
        self.log(f"Version: {self.version}", "info")
        
        self.log_indent -= 1
        
        print("\n" + "═" * 60)
        print("📦 MSIX-Datei ist bereit für Microsoft Store Upload!")
        print("═" * 60)
        print(f"\nDatei: {output_msix}")
        print(f"\nNächste Schritte:")
        print("  1. Partner Center: https://partner.microsoft.com/")
        print("  2. Lade die MSIX-Datei hoch")
        print("  3. Durchlaufe Zertifizierungsprozess")
        print("\nDokumentation:")
        print("  - STORE_UPLOAD_CHECKLIST.md")
        print("  - MSIX_BUILD_GUIDE.md")
        print("  - MSIX_QUICK_REFERENCE.md")
        print("\n" + "═" * 60)
    
    def build(self, skip_exe: bool = False, sign: bool = False, cert_path: Optional[str] = None) -> bool:
        """Führt kompletten Build-Prozess aus."""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " TaskSense MSIX Release Builder".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
        
        # Schritt 1: Prüfe Requirements
        if not self.check_requirements():
            self.log("Build abgebrochen", "error")
            return False
        
        # Schritt 2: Baue .exe
        if not self.build_executable(skip_exe):
            self.log("Build abgebrochen", "error")
            return False
        
        # Schritt 3: Bereite Struktur vor
        if not self.prepare_msix_structure():
            self.log("Build abgebrochen", "error")
            return False
        
        # Schritt 4: Erstelle MSIX
        if not self.create_msix_package():
            self.log("Build abgebrochen", "error")
            return False
        
        # Schritt 5: Signiere (optional)
        if sign:
            if not self.sign_msix(cert_path):
                self.log("Signatur fehlgeschlagen - MSIX ist trotzdem verwendbar", "warning")
        
        # Abschluss
        self.show_summary()
        
        return True


def main():
    """Haupteinstiegspunkt."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TaskSense Release Builder - All-in-One MSIX Paketierung",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python release.py
  python release.py --version 1.0.1
  python release.py --sign --cert certs/cert.pfx
  python release.py --skip-exe --verbose
        """
    )
    
    parser.add_argument("--version", default="1.0.0", help="Versionsnummer (default: 1.0.0)")
    parser.add_argument("--sign", action="store_true", help="Mit Zertifikat signieren")
    parser.add_argument("--cert", type=str, help="Zertifikat-Pfad (.pfx)")
    parser.add_argument("--skip-exe", action="store_true", help="Nutze existierende .exe")
    parser.add_argument("--verbose", action="store_true", help="Detaillierte Ausgabe")
    
    args = parser.parse_args()
    
    builder = TaskSenseReleaseBuilder(version=args.version, verbose=args.verbose)
    success = builder.build(
        skip_exe=args.skip_exe,
        sign=args.sign,
        cert_path=args.cert
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
