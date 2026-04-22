# Microsoft Store Upload Checkliste für TaskSense

## Phase 1: Vorbereitung (vor Upload)

### Developer Account
- [ ] Microsoft Partner Center Account erstellt
- [ ] Entwickler-Gebühr bezahlt ($19 oder lokal äquivalent)
- [ ] Email verrifiziert
- [ ] Profile komplett ausgefüllt

### Technische Vorbereitung
- [ ] MSIX-Paket gebaut mit `python build_msix.py`
- [ ] MSIX erfolgreich signiert
- [ ] MSIX-Größe: unter 2 GB
- [ ] Windows 10 19041+ erforderlich
- [ ] Windows 11 kompatibel getestet

### Assets vorbereitet
- [ ] Square44x44Logo.png (44×44) ✓
- [ ] Square150x150Logo.png (150×150) ✓
- [ ] StoreLogo.png (50×50) ✓
- [ ] SplashScreen.png (620×300) ✓
- [ ] Screenshots (mind. 1, max. 10)
  - [ ] 1920×1080 oder 1280×720
  - [ ] PNG oder JPG
  - [ ] App-Funktionalität zeigen
- [ ] Trailer (optional, aber empfohlen)
  - [ ] MP4 Format
  - [ ] Mindestens 720p
  - [ ] Unter 100 MB

### Beschreibungen
- [ ] App-Name: TaskSense (eindeutig im Store)
- [ ] Kurzbeschreibung (unter 100 Zeichen)
  - "Intelligentes Windows Reminder- und Fokus-Tool"
- [ ] Detaillierte Beschreibung
  - Features
  - Systemanforderungen
  - Berechtigungen erklärt
  - Screenshots-Beschreibungen
- [ ] "Notwenige Hinweise": Datenschutz, Berechtigungen
- [ ] Schlüsselwörter/Tags (bis 7)

### Datenschutz & Rechtliches
- [ ] Datenschutzerklärung verfasst
  - [ ] Welche Daten gesammelt werden
  - [ ] Lokal? Cloud? Beide?
  - [ ] Löschrichtlinien
  - [ ] DSGVO konform (falls EU-Nutzer)
- [ ] Impressum bereitgestellt
- [ ] Lizenzterme geklärt
- [ ] IARC Altersfreigabe durchführen
  - [ ] Fragebogen ausfüllen
  - [ ] Rating erhalten (z.B. USK, PEGI)

### Systemanforderungen
- [ ] Minimale OS-Version: Windows 10 19041
- [ ] RAM: 256 MB Minimum
- [ ] Disk: 500 MB freier Speicher
- [ ] Architektur: x64, ARM64, x86

## Phase 2: Partner Center Eintrag erstellen

### App-Registrierung
- [ ] App-Namen in Partner Center reserviert
- [ ] Eindeutiger Name im Store
- [ ] Kategorie gewählt (Produktivität)
- [ ] Unterkategorie gewählt (Utilities)

### Store-Einträge
- [ ] Beschreibung hinzugefügt
- [ ] Screenshots hochgeladen (mind. 1)
- [ ] Release-Notizen verfasst
- [ ] Preis gesetzt (kostenlos = keine Gebühren)
- [ ] Verfügbarkeitsländer gewählt
  - [ ] Mindestens Deutschland
  - [ ] Oder weltweit?

### Berechtigungen deklariert
- [ ] "RunFullTrust" Capability begründet
  - "Zum Tracking von Fenstern und Prozessen erforderlich"
- [ ] Berechtigungen in Datenschutzerklärung erklärt
- [ ] Nutzer können Berechtigungen kontrollieren

## Phase 3: MSIX hochladen

### Paket-Upload
- [ ] Gehe zu "Pakete" → "Neue Paketversion"
- [ ] MSIX-Datei ausgewählt
- [ ] Datei hochgeladen
- [ ] Validierung abgewartet
- [ ] Keine Validierungsfehler ✓

### Paket-Details überprüft
- [ ] Version korrekt
- [ ] Architektur erkannt (x64, ARM64)
- [ ] Größe akzeptabel
- [ ] Abhängigkeiten aufgelöst

## Phase 4: Zertifizierung vorbereiten

### Zertifizierungs-Seite
- [ ] Zertifizierungshinweise ausgefüllt
- [ ] Testgeräte-Info (falls nötig)
- [ ] Testkonten bereitgestellt (falls nötig)
- [ ] Bekannte Limitationen dokumentiert

### Konforme Funktionalität
- [ ] Keine Crashes oder Freeze
- [ ] UI responsive
- [ ] Alle Funktionen funktionieren
- [ ] Kein unangemessener Inhalt
- [ ] Datenschutz-Richtlinie akzessibel
- [ ] Kontakt-Information erreichbar

### Store-Richtlinien überprüft
- [ ] Keine Malware (Windows Defender scan)
- [ ] Keine unangemessenen Inhalte
- [ ] Keine Betrugsmechanismen
- [ ] Funktionalität wie beschrieben
- [ ] Keine Verletzung von Markenrechten
- [ ] Datenschutz eingehalten
- [ ] Keine Verlinkung zu externen Stores

## Phase 5: Zur Zertifizierung einreichen

### Final Check
- [ ] Alle erforderlichen Felder ausgefüllt
- [ ] Alle Screenshots aktuell
- [ ] Store-Beschreibung professionell
- [ ] Datenschutz-Link funktioniert
- [ ] Email-Kontakt korrekt
- [ ] Keine Typos oder Grammatikfehler

### Einreichung
- [ ] Klick auf "Zur Zertifizierung einreichen"
- [ ] Bestätigung erhalten
- [ ] Zertifizierungs-Status überwachen

### Zertifizierungs-Zeitraum
- [ ] Erwartete Dauer: 2-5 Arbeitstage
- [ ] Email-Benachrichtigungen aktiviert
- [ ] Support kontaktieren falls Fragen

## Phase 6: Nach Veröffentlichung

### Überwachung
- [ ] App im Store sichtbar
- [ ] Store-Listing korrekt angezeigt
- [ ] Installation funktioniert
- [ ] Update-Mechanismus funktioniert
- [ ] Kundenbewertungen anschauen
- [ ] Support-Anfragen bearbeiten

### Feedback & Iterationen
- [ ] Reviews lesen und antworten
- [ ] Bugs beheben und Updates einreichen
- [ ] Features basierend auf Feedback hinzufügen
- [ ] Mit neueren Windows-Versionen kompatibel halten

## Häufige Zertifizierungs-Ablehnungsgründe

- ❌ Crash oder Freeze beim Start
- ❌ Datenschutzerklärung fehlt oder nicht erreichbar
- ❌ Berechtigungen nicht begründet
- ❌ Falsche Screenshots oder Beschreibung
- ❌ Funktionalität nicht wie beschrieben
- ❌ Ungültige MSIX-Signatur
- ❌ Zu große Datei
- ❌ Unangemessener Inhalt
- ❌ Mehrfache Stores referenziert
- ❌ Outdated Abhängigkeiten

## Nützliche Links

- Partner Center: https://partner.microsoft.com/
- App Policies: https://docs.microsoft.com/store/policies
- MSIX Academy: https://learn.microsoft.com/training/modules/package-windows-apps-with-msix/
- Zertifizierungsleitfaden: https://docs.microsoft.com/windows/msix/store-developer-program

## Kontakt & Support

Bei Problemen während Zertifizierung:
1. Lese Zertifizierungs-Bericht in Partner Center
2. Bearbeite App und reiche erneut ein
3. Kontaktiere Microsoft Store Support
4. Konsultiere Developer Community Forum

## Notizen

```
Projekt: TaskSense
Version: 1.0.0
Eingereicht: __________
Status: __________
Notizen: __________
```

---

**Checkliste-Version**: 1.0  
**Letzte Aktualisierung**: April 2026  
**Nächste Überprüfung**: Bei neuem Release
