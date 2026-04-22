"""
Build-Skript für TaskSense als standalone .exe mit PyInstaller.

Verwendung:
    python build.py --edition lite
    python build.py --edition pro
"""

import argparse
import sys

from build_common import get_product


def build_exe(edition: str):
    """Erstellt die .exe mit PyInstaller."""
    product = get_product(edition)

    print("=" * 60)
    print(f"{product.display_name} Build-Prozess")
    print("=" * 60)

    try:
        import PyInstaller.__main__
    except ImportError:
        print("\nFehler: PyInstaller ist nicht installiert!")
        print("Bitte installieren Sie PyInstaller:")
        print("    pip install pyinstaller")
        sys.exit(1)

    build_args = [
        "--onefile",
        "--windowed",
        f"--name={product.exe_name}",
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
        product.entry_script,
    ]

    print("\nStarte Build mit folgenden Optionen:")
    print("pyinstaller " + " ".join(build_args))
    print("\n" + "=" * 60 + "\n")

    try:
        import PyInstaller.__main__

        PyInstaller.__main__.run(build_args)

        print("\n" + "=" * 60)
        print("Build erfolgreich!")
        print(f"Datei: dist/{product.exe_name}.exe")
        print("=" * 60)
    except Exception as error:
        print("\n" + "=" * 60)
        print(f"Build fehlgeschlagen: {error}")
        print("=" * 60)
        sys.exit(1)


def main():
    """CLI-Einstiegspunkt."""
    parser = argparse.ArgumentParser(description="Baue TaskSense Lite oder Pro als .exe")
    parser.add_argument(
        "--edition",
        choices=("lite", "pro"),
        default="pro",
        help="Zu bauende Produktedition",
    )
    args = parser.parse_args()

    build_exe(args.edition)


if __name__ == "__main__":
    main()
