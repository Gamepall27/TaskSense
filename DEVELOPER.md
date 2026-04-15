# SmartCue Entwickler-Dokumentation

## Überblick

SmartCue ist ein intelligentes Windows-Reminder-Tool, das on Basis von Fenster-Tracking und Nutzungsdauer Smart-Rules auslöst.

## Architektur

### Komponenten

```
┌─────────────────────────────────────────────┐
│           User Interface (PyQt6)             │
│     Dashboard / Rules / Statistics / Prefs   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────┴───────────────────────────┐
│          Main Window Controller              │
│      (main_window.py - Threading)            │
└────┬────────────────────────────────────────┘
     │
     ├─► Core Logic ◄─────────────────────────┐
     │   ├─ WindowTracker (Windows API)       │
     │   ├─ UsageTracker (Session/Daily)      │
     │   └─ RuleEngine (Evaluation)           │
     │                                         │
     ├─► Services                             │
     │   └─ NotificationService (Toast)       │
     │                                         │
     ├─► Storage                              │
     │   └─ StorageManager (JSON)             │
     │                                         │
     └─► Models                               │
         ├─ Rule, RuleCondition, RuleAction   │
         ├─ AppUsageEntry, DailyUsageStats    │
         ├─ Settings                          │
         └─ ReminderLog                       │
```

### Datenfluss

1. **Tracking Loop** (alle 2 Sekunden):
   - `WindowTracker.get_active_window()` → Aktive App
   - `UsageTracker.update_active_app()` → Update Nutzungszeit
   - Signal an Dashboard

2. **Rule Evaluation**:
   - `RuleEngine.evaluate_rules()` → Alle Regeln prüfen
   - `RuleEngine._evaluate_condition()` → Bedingungen evaluieren
   - Bei Match: `RuleAction` auslösen

3. **Notifications**:
   - `NotificationService.show_notification()` → Toast anzeigen
   - `StorageManager.log_reminder()` → In Historia speichern

4. **Storage**:
   - Alle Daten als JSON in `data/`
   - Rules: `data/rules.json`
   - Settings: `data/settings.json`
   - Reminders: `data/reminders.json`
   - Stats: `data/statistics/stats_YYYY-MM-DD.json`

## Klassen-Details

### window_tracker.py

```python
WindowTracker()
├─ get_active_window() -> (app_name, process_name, window_title)
├─ get_active_monitor_info() -> dict
└─ _extract_app_name(process_name) -> str
```

Nutzt Windows API über `ctypes` und `psutil`.

### rule_engine.py

```python
UsageTracker()
├─ update_active_app(app_name, process_name)
├─ get_app_usage_minutes(app_name, scope) -> float
├─ reset_session()
└─ get_daily_stats() -> dict

RuleEngine(usage_tracker)
├─ evaluate_rules(rules, app_name, ...) -> List[Rule]
└─ _evaluate_condition(condition, ...) -> bool
```

**Bedingungstypen**:
- `app_is`: App muss exakt sein
- `app_contains`: App enthält String
- `app_not`: App ist nicht
- `usage_time_greater`: Nutzungszeit > X Minuten
- `time_after`: Aktuelle Zeit > X
- `time_before`: Aktuelle Zeit < X
- `weekday`: Wochentag ist X

### storage_manager.py

```python
StorageManager(data_dir)
├─ Regeln:
│  ├─ load_rules() -> List[Rule]
│  ├─ save_rules(rules)
│  ├─ save_rule(rule)
│  └─ delete_rule(rule_id)
├─ Einstellungen:
│  ├─ load_settings() -> Settings
│  └─ save_settings(settings)
├─ Reminders:
│  ├─ log_reminder(reminder)
│  └─ get_reminders_today() -> List[ReminderLog]
└─ Statistiken:
   ├─ save_daily_stats(stats)
   └─ load_daily_stats(date_str) -> DailyUsageStats
```

## Extending SmartCue

### Neue Bedingungstypen hinzufügen

In `rule_engine.py`, Methode `_evaluate_condition()`:

```python
elif condition_type == "my_new_condition":
    # Implementierung
    return True/False
```

### Neue Regel-Aktionen

In `models/rule.py`:

```python
# Addiere neue action_type
class RuleAction:
    action_type: str  # "notify", "log", "execute", etc.
```

Dann in `main_window.py`:

```python
def _trigger_notification(self, rule: Rule):
    for action in rule.actions:
        if action.action_type == "notify":
            # Handle Notification
        elif action.action_type == "execute":
            # Handle Custom Action
```

### Neuer Storage-Backend

Implementiere die Same Interface wie `StorageManager`:

```python
class DatabaseStorage:
    def load_rules() -> List[Rule]: ...
    def save_rules(rules): ...
    # etc.
```

### Neue GUI-Tabs

In `gui/main_window.py`:

```python
from .new_feature import NewFeatureWidget

self.tabs.addTab(NewFeatureWidget(self), "Feature")
```

## Performance-Tipps

1. **Tracking-Interval**: Standard ist 2 Sekunden. Bei niedriger System-Last kann auf 1s reduziert werden.

2. **Regel-Evaluation**: Mit vielen Regeln können Sie diese deaktivieren, wenn nicht nötig.

3. **Storage**: JSON ist fine für kleine Datenmengen. Für >10k Einträge: zu SQLite migrieren.

4. **Threading**: Tracking läuft in QTimer, nicht in separatem Thread. Das ist performant genug.

## Debugging

### Debug-Logging aktivieren

In `main.py`:

```python
from app.utils.logging_setup import setup_logging
logger = setup_logging(log_level="DEBUG")
```

### Daten überprüfen

JSON-Dateien sind human-readable:

```bash
cat data/rules.json
cat data/settings.json
```

### Regel-Engine testen

Manually in Python:

```python
from app.core import RuleEngine, UsageTracker
from app.models import Rule, RuleCondition

tracker = UsageTracker()
engine = RuleEngine(tracker)

tracker.update_active_app("Chrome", "chrome.exe")
# Set 120 minutes of usage
tracker.session_usage["Chrome"] = timedelta(minutes=120)

rule = Rule(
    conditions=[RuleCondition("usage_time_greater", "120")]
)

result = engine.evaluate_rules([rule], "Chrome", "chrome.exe")
print(result)  # Should be [rule]
```

## Bekannte Limitierungen

1. **Windows-spezifisch**: Nutzt Windows API. Linux/macOS nicht unterstützt.

2. **Admin-Rechte**: Zum Tracking von System-Prozessen sind manchmal Admin-Rechte nötig.

3. **Notifications**: Teilweise buggy auf älteren Windows 10 Versionen. Fallback auf Sound.

4. **CPU**: Bei sehr häufigen Rules kann CPU-Last steigen.

## Zukünftige Verbesserungen

- [ ] SQLite-Backend für besser Skalierbarkeit
- [ ] Machine Learning für Auto-Rule-Detection
- [ ] Hard-Mode: Blocken von Apps
- [ ] Cloud-Sync mit End-to-End Encryption
- [ ] Plugin-Architecture
- [ ] REST-API für externe Integration
- [ ] Mobile-App Integration

## Testing

Unit-Tests können so erstellt werden:

```python
# tests/test_rule_engine.py
import unittest
from app.core import RuleEngine, UsageTracker
from app.models import Rule, RuleCondition

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.tracker = UsageTracker()
        self.engine = RuleEngine(self.tracker)
    
    def test_app_is_condition(self):
        # Test implementation
        pass
```

## Build für Production

```bash
python build.py
```

Dies erstellt eine standalone .exe unter `dist/SmartCue.exe`.

## Support

Für Bugs oder Features: Schreiben Sie einen Issue mit Logs aus `data/smartcue_*.log`.
