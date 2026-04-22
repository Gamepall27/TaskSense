"""
Build-Skript für TaskSense als standalone .exe mit PyInstaller.

Verwendung:
    python build.py

Dies erstellt eine standalone .exe Datei unter dist/TaskSense.exe
"""

import subprocess
import sys
import os


def build_exe():
    """Erstellt die .exe mit PyInstaller."""
    
    print("=" * 60)
    print("TaskSense Build-Prozess")
    print("=" * 60)
    
    # Prüfe, ob PyInstaller installiert ist
    try:
        import PyInstaller.__main__
    except ImportError:
        print("\nFehler: PyInstaller ist nicht installiert!")
        print("Bitte installieren Sie PyInstaller:")
        print("    pip install pyinstaller")
        sys.exit(1)
    
    # Build-Argumente
    build_args = [
        "--onefile",
        "--windowed",
        "--name=TaskSense",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.sip",
        "--hidden-import=psutil",
        "--hidden-import=win10toast",
        "--collect-all=PyQt6",
        "--collect-all=pyqt6",
        "--collect-all=win10toast",
        "main.py",
    ]
    
    print("\nStarte Build mit folgenden Optionen:")
    print("pyinstaller " + " ".join(build_args))
    print("\n" + "=" * 60 + "\n")
    
    # Führe PyInstaller direkt als Modul aus
    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(build_args)
        
        print("\n" + "=" * 60)
        print("Build erfolgreich!")
        print("Datei: dist/TaskSense.exe")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"Build fehlgeschlagen: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    build_exe()
