# TaskSense - Microsoft Store MSIX Paketierung

## Übersicht

Dieses Projekt kann als MSIX-Paket für den Microsoft Store gebaut werden. MSIX ist das moderne Paketierungsformat für Windows-Apps mit automatischen Updates, Versionsverwaltung und Store-Integration.

## Voraussetzungen

### 1. Windows SDK installieren
```powershell
# Via Microsoft Store (empfohlen)
# Suche nach "Windows App SDK" oder "Windows SDK"
```

Oder über Visual Studio:
- Öffne Visual Studio Installer
- Wähle "Windows App SDK" unter Optionale Komponenten

### 2. MakeAppx Tool
Das Tool wird mit dem Windows SDK installiert. Pfad:
```
C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\MakeAppx.exe
```

### 3. Python-Abhängigkeiten
```bash
pip install pyinstaller pillow
```

### 4. Zertifikat (für Store-Upload)
- Entwerfe das App-Paket selbst mit einem Testzertifikat
- Für Microsoft Store Upload: Partner Center generiert das Zertifikat

## MSIX Build durchführen

### Einfacher Build (ohne Signatur)
```bash
python build_msix.py
```

Dies erstellt `dist/TaskSense.msix`

### Build mit digitaler Signatur
```bash
python build_msix.py --sign --cert path/to/certificate.pfx
```

## Struktur des MSIX-Pakets

```
build/msix/
├── AppxManifest.xml          # App-Manifest (Metadaten)
├── TaskSense.exe             # Hauptprogramm
└── Assets/                   # App-Icons und Bilder
    ├── StoreLogo.png         (50×50)
    ├── Square44x44Logo.png   (44×44)
    ├── Square150x150Logo.png (150×150)
    └── SplashScreen.png      (620×300)
```

## Microsoft Store Upload

### 1. Partner Center Account erstellen
- Gehe zu: https://partner.microsoft.com/
- Registriere dich als App-Developer
- Zahle einmalig $19 (oder lokales Äquivalent)

### 2. App im Partner Center registrieren
1. Gehe zu "Dashboard" → "Neue Anwendung erstellen"
2. Gib App-Namen ein: "TaskSense"
3. Reserviere App-Namen
4. Fülle Produktinformationen aus:
   - Beschreibung
   - Screenshots
   - Kategorien
   - Altersfreigabe
   - Systemanforderungen (Windows 10+)

### 3. Paketinformationen hinzufügen
1. Gehe zu "Pakete"
2. Lade `dist/TaskSense.msix` hoch
3. Partner Center signiert das Paket automatisch
4. Überprüfe die Paketdetails

### 4. Store-Einträge ausfüllen
1. **Beschreibung**: Detaillierte Features, Screenshots, Videos
2. **Lizenzierungsvorgaben**: Kostenlos/Bezahlt
3. **Altersfreigabe**: IARC-Bewertung durchführen
4. **Datenschutz**: Datenschutzrichtlinie bereitstellen
5. **Hardwareanforderungen**: Mind. Windows 10, 64-bit

### 5. Zertifizierung
1. Reiche zur Zertifizierung ein
2. Microsoft prüft auf:
   - Funktionalität
   - Sicherheit
   - Datenschutz
   - Store-Richtlinien-Konformität
3. Gültig: 2-5 Arbeitstage

### 6. Veröffentlichung
Nach bestandener Zertifizierung:
- App wird im Store veröffentlicht
- Automatische Updates via Store aktiviert
- Benutzer können installieren/updaten

## AppxManifest.xml Anpassungen

Falls Anpassungen nötig sind, bearbeite `AppxManifest.xml`:

```xml
<Identity Name="Gamepall27.TaskSense"
          Publisher="CN=Gamepall27"
          Version="1.0.0.0" />
```

**Wichtig**: 
- `Name` muss reservierter App-Name sein
- `Publisher` muss zum Store-Account passen
- Version als Semantic Versioning: `MAJOR.MINOR.PATCH.BUILD`

## Automatische Updates

Nach Store-Veröffentlichung können Updates automatisch verteilt werden:

1. Erhöhe Version in `app/__init__.py`:
   ```python
   __version__ = "1.0.1"
   ```

2. Baue neues MSIX:
   ```bash
   python build_msix.py
   ```

3. Lade in Partner Center hoch

Benutzer erhalten automatische Updates via Store.

## Häufige Probleme

### Problem: "MakeAppx nicht gefunden"
**Lösung**: Installiere Windows SDK oder füge zu PATH hinzu:
```powershell
$env:Path += ";C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64"
```

### Problem: "Assets nicht gefunden"
**Lösung**: Erstelle `Assets/` Verzeichnis mit PNG-Dateien (mindestens 50×50)

### Problem: "Ungültige Manifest"
**Lösung**: Validiere mit:
```bash
MakeAppx validate /d build/msix /lar DiagnosticReport.xml
```

### Problem: "Signatur ungültig"
**Lösung**: Zertifikat muss:
- SHA256 sein
- Gültig und nicht abgelaufen
- Auf Code Signing ausgelegt sein

## Testinstallation lokal

```powershell
# Installiere Testsignatur
Add-AppxPackage -Register "build/msix/AppxManifest.xml" -ForceUpdateFromAnyVersion
```

## Store-Richtlinien Checklist

- ✓ Keine Malware
- ✓ Datenschutz einhalten
- ✓ Keine unangemessenen Inhalte
- ✓ Funktionalität wie beschrieben
- ✓ Store-Metadaten korrekt
- ✓ System-APIs korrekt verwendet

## Ressourcen

- Microsoft App Packaging: https://docs.microsoft.com/en-us/windows/msix/
- Partner Center: https://partner.microsoft.com/
- Windows App SDK: https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/
- MSIX Academy: https://learn.microsoft.com/en-us/training/modules/package-windows-apps-with-msix/

## Support

Bei Fragen oder Problemen:
1. Konsultiere Microsoft Docs
2. Kontaktiere Microsoft Developer Support
3. Schreibe ein Issue im Repository
