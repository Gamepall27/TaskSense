"""
Test-Skript für SmartCue.

Dieses Skript prüft, ob alle Abhängigkeiten und Module korrekt installiert sind.

Verwendung:
    python test_setup.py
"""

import sys
import os


def test_imports():
    """Testet, ob alle Python-Module importierbar sind."""
    
    print("=" * 60)
    print("SmartCue Dependency Test")
    print("=" * 60)
    print()
    
    tests = [
        ("PyQt6", "PyQt6.QtWidgets"),
        ("psutil", "psutil"),
        ("win10toast", "win10toast"),
    ]
    
    failed = []
    
    for package_name, import_name in tests:
        try:
            __import__(import_name)
            print(f"[OK] {package_name}")
        except ImportError as e:
            print(f"[FAIL] {package_name}: {e}")
            failed.append(package_name)
    
    print()
    print("=" * 60)
    
    if failed:
        print(f"\nFehlende Pakete: {', '.join(failed)}")
        print("\nInstallieren Sie diese mit:")
        print(f"    pip install {' '.join(failed)}")
        print("\nOder installieren Sie alle Abhängigkeiten mit:")
        print("    pip install -r requirements.txt")
        return False
    else:
        print("Alle Abhängigkeiten sind installiert!")
        return True


def test_structure():
    """Testet, ob die Projektstruktur korrekt ist."""
    
    print("\nProjektstruktur prüfen...")
    print("-" * 60)
    
    required_dirs = [
        "app",
        "app/gui",
        "app/core",
        "app/models",
        "app/storage",
        "app/services",
        "app/utils",
        "data",
    ]
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "app/__init__.py",
        "app/gui/__init__.py",
        "app/core/__init__.py",
        "app/models/__init__.py",
        "app/storage/__init__.py",
        "app/services/__init__.py",
        "app/utils/__init__.py",
    ]
    
    failed = []
    
    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            print(f"[FAIL] Directory: {dir_name}")
            failed.append(dir_name)
        else:
            print(f"[OK] Directory: {dir_name}")
    
    for file_name in required_files:
        if not os.path.isfile(file_name):
            print(f"[FAIL] File: {file_name}")
            failed.append(file_name)
        else:
            print(f"[OK] File: {file_name}")
    
    print()
    return len(failed) == 0


def main():
    """Führt alle Tests durch."""
    
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test structure
    print()
    structure_ok = test_structure()
    
    print()
    print("=" * 60)
    
    if imports_ok and structure_ok:
        print("\nAlle Tests bestanden!")
        print("Die Anwendung kann gestartet werden mit:")
        print("    python main.py")
        print()
        return True
    else:
        print("\nEinige Tests fehlgeschlagen!")
        print("Bitte beheben Sie die Fehler oben.")
        print()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
