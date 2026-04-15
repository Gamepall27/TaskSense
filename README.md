# SmartCue - Intelligentes Reminder- und Fokus-Tool fur Windows

## Ubersicht

**SmartCue** ist eine Windows-Desktop-Anwendung, die dich intelligente Erinnerungen gibt. Im Gegensatz zu klassischen Reminder-Tools erkennt SmartCue not nur feste Uhrzeiten, sondern auch:

- Welche Programme du gerade nutzt
- Wie lange du an einem Programm arbeitet
- Spezifische Muster in deinem Verhalten
- Tageszeiten und Wochentage

Basierend auf diesen Daten zeigt die App dir smart platzierte Erinnerungen. Zum Beispiel:
- "Du hast Chrome bereits 120 Minuten genutzt - Zeit fur eine Pause?"
- "Es ist 22 Uhr - Solltest du nicht Feierabend machen?"
- "VS Code ist geöffnet - Git Commit nicht vergessen!"

## Features

### MVP v1.0

- [x] **Fenster-Tracking**: Erkennt automatisch das aktive Fenster und Programm
- [x] **Nutzungs-Tracking**: Misst, wie lange jede App aktiv ist
- [x] **Flexible Regel-Engine**: Definiere deine eigenen Smart-Rules
- [x] **Windows-Benachrichtigungen**: Moderne Desktop-Notifications
- [x] **Regel-Verwaltung**: Erstelle, bearbeite, losche Regeln in der GUI
- [x] **Statistiken**: Sehe deine App-Nutzung und Erinnerungs-Historie
- [x] **Einstellungen**: Passe Tracking-Intervall, Benachrichtigungen an
- [x] **Persistierung**: Alle Daten werden lokal in JSON gespeichert
- [x] **Hintergrundbetrieb**: System-Tray verfügbar
- [x] **Beispiel-Regeln**: App startet mit vordefinierten Beispielregeln

### Zeige Regel-Typen

1. **App-basiert**
   - `app_is`: Wenn bestimmte App lauft
   - `app_contains`: Wenn App-Name enthält
   - `app_not`: Wenn bestimmte App NICHT lauft

2. **Zeit-basiert**
   - `usage_time_greater`: Wenn Nutzungsdauer > X Minuten
   - `time_after`: Wenn aktuelle Zeit > Uhrzeit
   - `time_before`: Wenn aktuelle Zeit < Uhrzeit
   - `weekday`: Wenn bestimmter Wochentag

3. **Bedingung-Gruppen**
   - Mehrere Bedingungen mit AND verbunden

4. **Cooldown & Drosselung**
   - Regeln konnen nur einmal pro N Minuten auslosen (Cooldown)

## Installation

### Voraussetzungen

- Windows 10 oder neuer
- Python 3.8+
- pip

### Setup

1. **Repository klonen oder Dateien herunterladen**

```bash
cd smartcue
```

2. **Virtuelle Umgebung erstellen (empfohlen)**

```bash
python -m venv venv
venv\Scripts\activate
```

3. **Abhangigkeiten installieren**

```bash
pip install -r requirements.txt
```

## Starten der Anwendung

### Direkt mit Python

```bash
python main.py
```

Das ist es! Die Anwendung startet und zeigt das Hauptfenster mit dem Dashboard.

## Bedienung

### Dashboard-Tab

- Sehe die aktuell laufende App
- Checke deine Nutzungsdauer
- Uberblick uber die meistgenutzten Apps heute
- Letzte ausgelöste Erinnerung

### Regeln-Tab

- **Neue Regel**: Klicke "Neue Regel" um eine neue Regel zu erstellen
- **Name**: Gib einen aussagekraftigen Namen ein (z.B. "Chrome Pause")
- **Bedingung**: Wahle den Regeltyp
  - `app_is`: "Chrome" → Losung aus, wenn Chrome lauft
  - `usage_time_greater`: "120" → Losung aus, wenn App 120+ Minuten lauft
  - `time_after`: "22:00" → Losung aus, wenn es nach 22 Uhr ist
- **Notification-Titel & Text**: Schreib die Meldung
- **Cooldown**: Mindestabstand zwischen Auslosungen (z.B. 15 Minuten)
- **Enabled**: Regel kann an/aus geschaltet werden

### Statistiken-Tab

- Alle Apps die heute genutzt wurden
- Gesamtnutzungsdauer je App
- Historie der ausgelöstenErinnerungen

### Einstellungs-Tab

- **Tracking-Intervall**: Wie oft wird das aktive Fenster gecheckt (2sec empfohlen)
- **Benachrichtigungen**: Können hier deaktiviert werden
- **Theme**: Light/Dark (Vorbereitung)
- **Mit Windows minimiert starten**: App versteckt im Tray beim Start

## Beispiel-Regeln

Die App wird mit diesen Regeln gestartet:

### 1. Chrome Pause-Reminder

```
Bedingung: usage_time_greater (Chrome > 120 Minuten)
Nachricht: "Du hast Chrome bereits 120 Minuten genutzt. Zeit fur eine Pause?"
Cooldown: 15 Minuten
```

### 2. Spat-Worker Alert

```
Bedingung: time_after (22:00 Uhr)
Nachricht: "Es ist 22 Uhr. Solltest du nicht langsam Feierabend machen?"
Cooldown: 60 Minuten
```

### 3. VS Code Git-Reminder

```
Bedingung: app_is (VS Code)
Nachricht: "Denke daran, deine Anderungen zu committen!"
Cooldown: 30 Minuten
```

## Projektstruktur

```
smartcue/
├── main.py                      # Einstiegspunkt
├── requirements.txt             # Python-Abhangigkeiten
├── README.md                    # Diese Datei
├── data/                        # Lokale Datenspeicherung
│   ├── rules.json              # Gespeicherte Regeln
│   ├── settings.json           # Einstellungen
│   ├── reminders.json          # Erinnerungs-Historie
│   └── statistics/             # Tägliche Statistiken
└── app/
    ├── __init__.py
    ├── gui/                     # Benutzeroberfläche (PyQt6)
    │   ├── __init__.py
    │   ├── main_window.py       # Hauptfenster + Tab-Verwaltung
    │   ├── dashboard.py         # Dashboard-Tab
    │   ├── rules_manager.py     # Regelverwaltungs-Tab
    │   ├── statistics.py        # Statistik-Tab
    │   └── settings.py          # Einstellungs-Tab
    ├── core/                    # Kernlogik
    │   ├── __init__.py
    │   ├── window_tracker.py    # Windows-Fenster-Tracking
    │   └── rule_engine.py       # Regel-Engine & Usage-Tracking
    ├── models/                  # Datenmodelle
    │   ├── __init__.py
    │   ├── rule.py             # Regel-Datenmodell
    │   ├── app_usage.py        # App-Nutzungs-Modelle
    │   ├── settings.py         # Einstellungs-Modell
    │   └── reminder.py         # Erinnerungs-Log-Modell
    ├── services/                # Services (Notifications, etc.)
    │   ├── __init__.py
    │   └── notification_service.py
    ├── storage/                 # Persistierung
    │   ├── __init__.py
    │   └── storage_manager.py  # JSON-basierte Speicherung
    └── utils/                   # Hilfsfunktionen
        ├── __init__.py
        └── helpers.py          # Format-Funktionen und Utilities
```

## Build als .exe mit PyInstaller

### 1. PyInstaller installieren

```bash
pip install pyinstaller
```

### 2. Build-Befehl

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name SmartCue main.py
```

**Parameter erklart:**
- `--onefile`: Erstellt eine einzelne .exe anstelle von Ordnern
- `--windowed`: Keine Konsole (GUI-only)
- `--icon=icon.ico`: (Optional) Icon for die .exe
- `--name SmartCue`: Name der ausgegeben .exe

### 3. Ergebnis

Nach dem Build findest du die .exe hier:
```
dist/SmartCue.exe
```

Diese .exe kann direkt auf Windows-Systemen ohne Python ausgefuhrt werden.

### Problem: Fehler beim Build?

Falls PyInstaller fehlende Module meldet:
```bash
pyinstaller --onefile --windowed --name SmartCue \
  --hidden-import=PyQt6.QtCore \
  --hidden-import=PyQt6.QtGui \
  --hidden-import=PyQt6.QtWidgets \
  --hidden-import=psutil \
  --hidden-import=win10toast \
  main.py
```

## Tipps & Tricks

### App im Hintergrund laufen lassen

- Mit der Minmimieren-Taste kannst du die App minimieren
- Sie lauft weiterhin im System-Tray und uberwacht deine Apps
- Doppelklick auf das Tray-Icon offnet die App wieder

### Custom-Regeln erstellen

Die Regel-Engine ist very flexibel. Beispiele:

```
Bedingung 1: Wenn Excel lauft
=> "Vergiss nicht zu speichern!"

Bedingung 2: Wenn Firefox > 90 Minuten lauft
=> "Zum Lesen: Tabs sortieren!"

Bedingung 3: Wenn nach 18 Uhr
=> "Feierabend naht!"
```

### Daten exportieren

Alle Daten liegen in `data/` als JSON. Du kannst sie direkt bearbeiten oder sichern.

## Datenschutz

SmartCue:
- Speichert alle Daten **lokal** auf deinem PC
- Keine Abhängigkeit zu Cloud oder externen Servern
- Keine Datenerfassung oder Analytics
- Datenspeicherort: `smartcue/data/`

## Architektur-Highlights

### Saubere Modular-Struktur

- **GUI**: PyQt6-basiert, deklarativ
- **Core**: Windows API-Zugriff + ßantz Logic
- **Storage**: Pluggable Storage-Interface (aktuell JSON, leicht zu SQLite aufrüsten)
- **Models**: Einfache Dataclasses, serialisierbar
- **Services**: Notification, Logging, etc.

### Erweiterbarkeit

Die Architektur ist für zukünftige Features vorbereitet:

- [ ] Snooze-Button auf Notifications
- [ ] App-Kategorien (Arbeit, Ablenkung, Lernen)
- [ ] Wochenstatistiken
- [ ] Export/Import von Regeln
- [ ] Hard-Mode (Fokus-Lock)
- [ ] Cloud-Sync (Struktur nicht verbaut)
- [ ] Webhook-Integration

### Performance

- Threading für Fenster-Tracking (UI bleibt responsive)
- Optimierte Regel-Evaluation
- Minimale CPU/RAM-Nutzung
- Configurable Tracking-Intervall

## Debugging

Für Entwicklung/Debugging:

```bash
# Mit Konsole starten
python main.py

# Debug-Ausgaben in console.log anschauen
```

## Lizenz

Dieses Projekt stellt ein MVP fur die Nutzung zur Verfügung.

## Support & Feedback

Probleme? Durchschaue die generierten Logs im `data/`-Verzeichnis.

---

**Version**: 1.0.0  
**Programmier-Sprache**: Python 3.8+  
**Framework**: PyQt6  
**Zielplattform**: Windows 10+  
**Lizenz**: MIT
