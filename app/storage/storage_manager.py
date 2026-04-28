"""JSON und SQLite-basierte Speicherung für TaskSense."""
import json
import os
import sqlite3
from typing import List, Optional
from app.models import Rule, Settings, ReminderLog, DailyUsageStats
from datetime import datetime


class StorageManager:
    """Verwaltet die Persistierung von Daten."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialisiert den StorageManager.
        
        Args:
            data_dir: Verzeichnis für Datenspeicherung
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.rules_file = os.path.join(data_dir, "rules.json")
        self.settings_file = os.path.join(data_dir, "settings.json")
        self.reminders_file = os.path.join(data_dir, "reminders.json")
        self.statistics_dir = os.path.join(data_dir, "statistics")
        self.db_path = os.path.join(data_dir, "tasksense.db")
        
        os.makedirs(self.statistics_dir, exist_ok=True)
        
        # Initialisiere Datenbank
        self._init_database()
    
    # ===== RULES =====
    
    def load_rules(self) -> List[Rule]:
        """Lädt alle Regeln aus dem Speicher."""
        if not os.path.exists(self.rules_file):
            print(f"DEBUG: rules.json existiert nicht: {self.rules_file}")
            return []
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            rules = [Rule.from_dict(rule_data) for rule_data in data.get('rules', [])]
            print(f"DEBUG: {len(rules)} Regel(n) geladen: {[r.name for r in rules]}")
            return rules
        except Exception as e:
            print(f"Fehler beim Laden der Regeln: {e}")
            return []
    
    def save_rules(self, rules: List[Rule]):
        """Speichert alle Regeln."""
        try:
            data = {
                'rules': [rule.to_dict() for rule in rules],
                'last_saved': datetime.now().isoformat(),
            }
            
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Regeln: {e}")
    
    def save_rule(self, rule: Rule):
        """Speichert eine einzelne Regel."""
        rules = self.load_rules()
        
        # Ersetze oder füge Regel hinzu
        rule_index = next((i for i, r in enumerate(rules) if r.rule_id == rule.rule_id), -1)
        if rule_index >= 0:
            rules[rule_index] = rule
        else:
            rules.append(rule)
        
        self.save_rules(rules)
    
    def delete_rule(self, rule_id: str):
        """Löscht eine Regel."""
        rules = self.load_rules()
        rules = [r for r in rules if r.rule_id != rule_id]
        self.save_rules(rules)
    
    # ===== SETTINGS =====
    
    def load_settings(self) -> Settings:
        """Lädt die Einstellungen."""
        if not os.path.exists(self.settings_file):
            return Settings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Settings.from_dict(data)
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
            return Settings()
    
    def save_settings(self, settings: Settings):
        """Speichert die Einstellungen."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
    
    # ===== REMINDERS =====
    
    def log_reminder(self, reminder: ReminderLog):
        """Loggt eine ausgelöste Erinnerung."""
        try:
            reminders = []
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    reminders = json.load(f).get('reminders', [])
            
            reminders.append(reminder.to_dict())
            
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump({'reminders': reminders}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Loggen der Erinnerung: {e}")
    
    def get_reminders_today(self) -> List[ReminderLog]:
        """Gibt alle heutigen Erinnerungen zurück."""
        if not os.path.exists(self.reminders_file):
            return []
        
        try:
            today = datetime.now().date().isoformat()
            
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            reminders = []
            for reminder_data in data.get('reminders', []):
                reminder = ReminderLog(
                    rule_id=reminder_data.get('rule_id', ''),
                    rule_name=reminder_data.get('rule_name', ''),
                    title=reminder_data.get('title', ''),
                    message=reminder_data.get('message', ''),
                    triggered_at=datetime.fromisoformat(reminder_data.get('triggered_at', datetime.now().isoformat())),
                    dismissed=reminder_data.get('dismissed', False),
                    snoozed_until=datetime.fromisoformat(reminder_data['snoozed_until']) if reminder_data.get('snoozed_until') else None,
                )
                
                if reminder.triggered_at.date().isoformat() == today:
                    reminders.append(reminder)
            
            return reminders
        except Exception as e:
            print(f"Fehler beim Laden der heutigen Erinnerungen: {e}")
            return []
    
    # ===== DATABASE (SQLite) =====
    
    def _init_database(self):
        """Initialisiert die SQLite-Datenbank mit erforderlichen Tabellen."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Erstelle all_time_usage Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS all_time_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT UNIQUE NOT NULL,
                    total_minutes REAL DEFAULT 0,
                    last_updated TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Fehler beim Initialisieren der Datenbank: {e}")
    
    def _get_db_connection(self):
        """Gibt eine neue Datenbankverbindung zurück."""
        return sqlite3.connect(self.db_path)
    
    def update_app_all_time_usage(self, app_name: str, minutes: float):
        """Aktualisiert die Gesamtnutzungszeit einer App in der Datenbank."""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Prüfe ob App bereits existiert
            cursor.execute('SELECT total_minutes FROM all_time_usage WHERE app_name = ?', (app_name,))
            result = cursor.fetchone()
            
            if result:
                # Update existierende App
                new_total = result[0] + minutes
                cursor.execute('''
                    UPDATE all_time_usage 
                    SET total_minutes = ?, last_updated = ?
                    WHERE app_name = ?
                ''', (new_total, datetime.now().isoformat(), app_name))
            else:
                # Insert neue App
                cursor.execute('''
                    INSERT INTO all_time_usage (app_name, total_minutes, last_updated)
                    VALUES (?, ?, ?)
                ''', (app_name, minutes, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Gesamtnutzungszeit: {e}")
    
    def get_all_time_stats_from_db(self) -> dict:
        """Gibt die Gesamtnutzungsstatistiken aus der Datenbank zurück."""
        stats = {}
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT app_name, total_minutes FROM all_time_usage ORDER BY total_minutes DESC')
            rows = cursor.fetchall()
            
            for app_name, total_minutes in rows:
                stats[app_name] = total_minutes
            
            conn.close()
        except Exception as e:
            print(f"Fehler beim Lesen der Gesamtstatistiken: {e}")
        
        return stats
    
    # ===== STATISTICS =====
    
    def save_daily_stats(self, stats: DailyUsageStats):
        """Speichert tägliche Statistiken und synchronisiert mit Datenbank."""
        try:
            stats_file = os.path.join(self.statistics_dir, f"stats_{stats.date}.json")
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Synchronisiere Daten mit Datenbank (füge zu Gesamtsummen hinzu)
            for app_name, minutes in stats.app_usage.items():
                self.update_app_all_time_usage(app_name, minutes)
        except Exception as e:
            print(f"Fehler beim Speichern der Statistiken: {e}")
    
    def load_daily_stats(self, date_str: str) -> Optional[DailyUsageStats]:
        """Läd tägliche Statistiken für ein Datum."""
        try:
            stats_file = os.path.join(self.statistics_dir, f"stats_{date_str}.json")
            
            if not os.path.exists(stats_file):
                return None
            
            with open(stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return DailyUsageStats(
                date=data.get('date', date_str),
                app_usage=data.get('app_usage', {}),
                reminders_triggered=data.get('reminders_triggered', 0),
                focus_time_minutes=data.get('focus_time_minutes', 0),
            )
        except Exception as e:
            print(f"Fehler beim Laden der Statistiken: {e}")
            return None
    
    def get_all_time_stats(self) -> dict:
        """Gibt die aggregierten Nutzungsstatistiken über alle Sessions hinweg."""
        # Verwende Datenbankdaten als primäre Quelle
        return self.get_all_time_stats_from_db()
    
    def reset_all_time_stats(self):
        """Setzt alle Gesamtstatistiken und täglichen Statistiken zurück."""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Lösche alle Einträge aus der all_time_usage Tabelle
            cursor.execute('DELETE FROM all_time_usage')
            
            conn.commit()
            conn.close()
            
            # Lösche auch alle täglichen Statistik-Dateien
            if os.path.exists(self.statistics_dir):
                for filename in os.listdir(self.statistics_dir):
                    if filename.startswith('stats_') and filename.endswith('.json'):
                        file_path = os.path.join(self.statistics_dir, filename)
                        try:
                            os.remove(file_path)
                            print(f"DEBUG: Gelöschte Tages-Statistik: {filename}")
                        except Exception as e:
                            print(f"Fehler beim Löschen von {filename}: {e}")
            
            print("DEBUG: Alle Gesamtstatistiken und täglichen Statistiken wurden zurückgesetzt")
        except Exception as e:
            print(f"Fehler beim Zurücksetzen der Statistiken: {e}")
