# TaskSense Release Builder - Anleitung

## Schnellstart (30 Sekunden)

```bash
# Baue hochladbare MSIX-Datei
python release.py

# Fertig! Ausgabe: dist/TaskSense.msix
```

Das ist alles. Ein Befehl, alles erledigt.

## Was wird gemacht?

Der `release.py` Befehl führt ALLES automatisch aus:

1. ✓ Prüft Voraussetzungen (MakeAppx, PyInstaller)
2. ✓ Baut .exe mit PyInstaller
3. ✓ Erstellt MSIX-Verzeichnisstruktur
4. ✓ Kopiert/erstellt Asset-Dateien
5. ✓ Paketiert mit MakeAppx
6. ✓ Optional: Signiert die MSIX
7. ✓ Gibt hochladbare Datei aus

## Verwendung

### Basis-Build
```bash
python release.py
```
Erstellt: `dist/TaskSense.msix`

### Mit Versionsnummer
```bash
python release.py --version 1.0.1
```

### Mit Signatur
```bash
python release.py --sign --cert certs/TaskSense_TestCert.pfx
```

### Schneller Build (nutze existierende .exe)
```bash
python release.py --skip-exe
```

### Mit detaillierter Ausgabe
```bash
python release.py --verbose
```

### Kombinationen
```bash
python release.py --version 1.1.0 --sign --cert certs/cert.pfx --verbose
```

## Ausgabe

Nach erfolgreichen Build:

```
╔════════════════════════════════════════════════════════════╗
║    TaskSense MSIX Release Builder erfolgreich!             ║
╚════════════════════════════════════════════════════════════╝

✓ .exe erstellt (180.5 MB)
✓ MSIX erstellt (185.2 MB)
✓ Bereit für Upload

📦 MSIX-Datei ist bereit für Microsoft Store Upload!

Datei: dist/TaskSense.msix

Nächste Schritte:
  1. Partner Center: https://partner.microsoft.com/
  2. Lade MSIX-Datei hoch
  3. Durchlaufe Zertifizierung
```

## Voraussetzungen einmalig installieren

```bash
# PyInstaller
pip install pyinstaller

# Pillow (für Asset-Generierung, optional)
pip install pillow

# Windows SDK (mit MakeAppx)
# Download: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
```

## Tipps

### Problem: "MakeAppx nicht gefunden"
- Installiere Windows SDK
- MakeAppx wird automatisch gefunden

### Problem: ".exe zu groß"
```bash
# Baue mit UPX-Kompression
python release.py
```

### Problem: "Signatur fehlgeschlagen"
```bash
# Baue ohne Signatur (funktioniert auch so)
python release.py

# Oder erstelle neues Zertifikat
python cert_manager.py create-ps

# Dann mit Signatur
python release.py --sign --cert certs/TaskSense_TestCert.pfx
```

## Workflow für Microsoft Store

```bash
# 1. Entwicklung abgeschlossen
git commit -m "Feature: ..."
git push

# 2. Release-Build
python release.py --version 1.0.1

# 3. Upload zu Partner Center
# Öffne: https://partner.microsoft.com/
# Lade: dist/TaskSense.msix

# 4. Fertig! Zertifizierung läuft automatisch
```

## Automatisierung (Optional)

Mit GitHub Actions kannst du automatisch MSIX bauen:

```yaml
name: Release Build

on:
  release:
    types: [created]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install pyinstaller pillow
      - run: python release.py --version ${{ github.event.release.tag_name }}
      - uses: actions/upload-artifact@v2
        with:
          name: TaskSense-MSIX
          path: dist/TaskSense.msix
```

## Dokumentation

- [STORE_UPLOAD_CHECKLIST.md](STORE_UPLOAD_CHECKLIST.md) - Upload-Checkliste
- [MSIX_BUILD_GUIDE.md](MSIX_BUILD_GUIDE.md) - Detaillierte Anleitung
- [MSIX_QUICK_REFERENCE.md](MSIX_QUICK_REFERENCE.md) - Schnellreferenz

---

**Das ist alles was du brauchst!** 🚀

Ein Befehl, fertig.
