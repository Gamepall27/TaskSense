# TaskSense MSIX - Schnellreferenz

## Schnellstart (5 Minuten)

```bash
# 1. Voraussetzungen installieren
pip install pyinstaller pillow

# 2. MSIX bauen (automatisch .exe + Assets)
python build_msix.py

# 3. Ausgabe
dist/TaskSense.msix
```

## Kommandos

### MSIX bauen

```bash
# Einfacher Build (Test/Entwicklung)
python build_msix.py

# Mit Signatur (für Store)
python build_msix.py --sign --cert path/to/cert.pfx

# PowerShell (Windows)
.\build_msix.ps1
.\build_msix.ps1 -Sign -CertPath certs/TaskSense_TestCert.pfx
```

### Zertifikat erstellen

```bash
# Neue Test-Signatur (MakeCert)
python cert_manager.py create

# Mit PowerShell
python cert_manager.py create-ps

# Vorhandene Zertifikate auflisten
python cert_manager.py list
```

### Build validieren

```bash
# Teste MSIX lokal
MakeAppx validate /d build/msix /lar DiagnosticReport.xml

# Installiere zu Test
Add-AppxPackage -Register "build/msix/AppxManifest.xml" -ForceUpdateFromAnyVersion
```

## Dateistruktur

```
TaskSense/
├── build_msix.py              # Hauptbuild-Skript
├── build_msix.ps1             # PowerShell Variante
├── cert_manager.py            # Zertifikat-Manager
├── AppxManifest.xml           # MSIX-Manifest
├── MSIX_BUILD_GUIDE.md        # Ausführliche Anleitung
├── STORE_UPLOAD_CHECKLIST.md  # Upload-Checkliste
├── Assets/                    # Icons & Logos
│   ├── StoreLogo.png
│   ├── Square44x44Logo.png
│   ├── Square150x150Logo.png
│   └── SplashScreen.png
├── build/
│   └── msix/                  # Build-Verzeichnis
│       ├── AppxManifest.xml
│       ├── TaskSense.exe
│       └── Assets/
└── dist/
    └── TaskSense.msix         # Fertige MSIX
```

## Workflow

### Entwicklung
```
1. Programmieren
   python main.py              # Teste lokal
   
2. Build zu .exe
   python build.py
   dist/TaskSense.exe
   
3. Test
   dist/TaskSense.exe
```

### Für Microsoft Store
```
1. MSIX bauen
   python build_msix.py
   dist/TaskSense.msix
   
2. Zertifikat erstellen (wenn neu)
   python cert_manager.py create-ps
   
3. MSIX signieren
   python build_msix.py --sign --cert certs/TaskSense_TestCert.pfx
   
4. In Partner Center hochladen
   https://partner.microsoft.com/
   
5. Zertifizierung abwarten (2-5 Tage)
   
6. Im Store veröffentlicht 🎉
```

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| MakeAppx nicht gefunden | Windows SDK installieren |
| PyInstaller Fehler | `pip install --upgrade pyinstaller` |
| Zertifikat Fehler | `python cert_manager.py create-ps` |
| MSIX zu groß | Unnötige Dateien aus build/ entfernen |
| Manifest ungültig | Manifest.xml Syntax prüfen |

## Partner Center URLs

- Dashboard: https://partner.microsoft.com/dashboard
- App-Verwaltung: https://partner.microsoft.com/dashboard/windows/apps
- Richtlinien: https://docs.microsoft.com/store/policies
- Dev-Support: https://support.microsoft.com/

## Wichtige Informationen

- **App Name**: TaskSense
- **Publisher**: CN=Gamepall27
- **Version**: 1.0.0.0 (Update in `app/__init__.py`)
- **Erforderlich**: Windows 10 19041+ oder Windows 11
- **Zielgruppe**: Windows Desktop-Nutzer
- **Kategorie**: Produktivität / Utilities

## Partner Center Setup

1. Konto erstellen: https://partner.microsoft.com/
2. Entwickler-Gebühr zahlen ($19)
3. Email verifizieren
4. Profil ausfüllen
5. App registrieren und Name reservieren
6. Store-Listing vorbereiten
7. MSIX hochladen
8. Zur Zertifizierung einreichen

## Version Update vor Release

```bash
# 1. Versionsnummer erhöhen
# Bearbeite: app/__init__.py
__version__ = "1.0.1"

# 2. Bearbeite: AppxManifest.xml
Version="1.0.1.0"

# 3. Neuen Build erstellen
python build_msix.py --sign --cert certs/cert.pfx

# 4. Upload zu Partner Center
```

## Weitere Ressourcen

- Ausführlicher Guide: [MSIX_BUILD_GUIDE.md](MSIX_BUILD_GUIDE.md)
- Upload-Checkliste: [STORE_UPLOAD_CHECKLIST.md](STORE_UPLOAD_CHECKLIST.md)
- Zertifikat-Verwaltung: `python cert_manager.py --help`
- Main Dokumentation: [README.md](README.md)

---

**Letzte Aktualisierung**: April 2026  
**MSIX-Version**: 1.0  
**Windows-Kompatibilität**: 10.0.19041+
