"""Kern-Engine für das Tracking und Triggen von Regeln."""
from datetime import datetime, timedelta
from typing import List, Optional, Callable
from app.models import Rule, RuleCondition, AppUsageEntry, DailyUsageStats
import threading
import time


class UsageTracker:
    """Trackt die Nutzungszeiten von Anwendungen."""
    
    def __init__(self):
        """Initialisiert den UsageTracker."""
        self.current_app: Optional[str] = None
        self.current_process: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self.session_usage: dict = {}  # app_name -> timedelta
        self.today_usage: dict = {}  # app_name -> timedelta
        self.current_date: Optional[str] = None
        self._lock = threading.Lock()
    
    def update_active_app(self, app_name: Optional[str], process_name: Optional[str]):
        """
        Aktualisiert die aktuelle App und trackt die Nutzungszeit.
        
        Args:
            app_name: Name der aktuellen App
            process_name: Prozessname
        """
        with self._lock:
            if app_name is None:
                return
            
            # App-Wechsel erkannt
            if self.current_app is not None and self.current_app != app_name:
                self._finalize_app_usage()
                # Starte Grace Period
                self.app_change_time = datetime.now()
                self.last_app_before_change = self.current_app
            
            # Setze neue App
            if self.current_app != app_name:
                self.current_app = app_name
                self.current_process = process_name
                self.session_start_time = datetime.now()
    
    def _finalize_app_usage(self):
        """Speichert die Nutzungszeit der aktuellen App."""
        if self.current_app and self.session_start_time:
            duration = datetime.now() - self.session_start_time
            
            # Zu Session-Nutzung hinzufügen
            if self.current_app not in self.session_usage:
                self.session_usage[self.current_app] = timedelta()
            self.session_usage[self.current_app] += duration
            
            # Zu Tagesnutzung hinzufügen
            if self.current_app not in self.today_usage:
                self.today_usage[self.current_app] = timedelta()
            self.today_usage[self.current_app] += duration
    
    def get_app_usage_minutes(self, app_name: str, scope: str = "session") -> float:
        """
        Gibt die Nutzungsdauer einer App in Minuten zurück.
        
        Args:
            app_name: Name der App
            scope: 'session' oder 'today'
            
        Returns:
            Nutzungsdauer in Minuten
        """
        with self._lock:
            if scope == "session":
                usage_dict = self.session_usage
            elif scope == "today":
                usage_dict = self.today_usage
            else:
                return 0.0
            
            if app_name in usage_dict:
                duration = usage_dict[app_name]
                
                # Falls aktuelle App, addiere noch die aktuelle Session
                if app_name == self.current_app and self.session_start_time:
                    current_session_duration = datetime.now() - self.session_start_time
                    duration += current_session_duration
                
                return duration.total_seconds() / 60
            
            return 0.0
    
    def reset_session(self):
        """Setzt die Session zurück."""
        with self._lock:
            self.session_usage.clear()
            self.session_start_time = None
            self.current_app = None
            self.current_process = None
    
    def reset_today(self):
        """Setzt die heutigen Statistiken zurück."""
        with self._lock:
            self.today_usage.clear()
    
    def get_daily_stats(self) -> dict:
        """Gibt die heutigen Statistiken zurück."""
        with self._lock:
            stats = self.today_usage.copy()
            
            # Addiere aktuelle Session, falls vorhanden
            if self.current_app and self.session_start_time:
                current_duration = datetime.now() - self.session_start_time
                if self.current_app not in stats:
                    stats[self.current_app] = timedelta()
                stats[self.current_app] += current_duration
            
            # Konvertiere zu Minuten
            return {app: duration.total_seconds() / 60 for app, duration in stats.items()}


class RuleEngine:
    """Engine für die Evaluation und das Auslösen von Regeln."""
    
    def __init__(self, usage_tracker: UsageTracker):
        """
        Initialisiert die RuleEngine.
        
        Args:
            usage_tracker: Instanz von UsageTracker
        """
        self.usage_tracker = usage_tracker
        self.triggered_callbacks: List[Callable] = []
    
    def register_trigger_callback(self, callback: Callable):
        """
        Registriert einen Callback, der aufgerufen wird, wenn eine Regel ausgelöst wird.
        
        Args:
            callback: Callable(rule, context)
        """
        self.triggered_callbacks.append(callback)
    
    def evaluate_rules(self, rules: List[Rule], current_app: Optional[str],
                      current_process: Optional[str], window_title: str = "") -> List[Rule]:
        """
        Evaluiert alle Regeln und gibt die auszulösenden Regeln zurück.
        
        Args:
            rules: Liste von Regeln
            current_app: Aktuell aktive App
            current_process: Aktuell aktiver Prozess
            window_title: Fenstertitel
            
        Returns:
            Liste der auszulösenden Regeln
        """
        triggered_rules = []
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            # Prüfe, ob Bedingungen erfüllt sind
            if not self._evaluate_rule(rule, current_app, current_process, window_title):
                continue
            
            # Prüfe Cooldown nur wenn die Bedingung erfüllt ist
            if not rule.is_cooldown_expired():
                continue
            
            # Regel triggert!
            triggered_rules.append(rule)
            rule.mark_triggered()
        
        return triggered_rules
    
    def _evaluate_rule(self, rule: Rule, current_app: Optional[str],
                      current_process: Optional[str], window_title: str = "") -> bool:
        """
        Evaluiert eine einzelne Regel.
        
        Args:
            rule: Zu evaluierende Regel
            current_app: Aktuell aktive App
            current_process: Aktuell aktiver Prozess
            window_title: Fenstertitel
            
        Returns:
            True wenn Regel ausgelöst werden soll
        """
        if not rule.conditions:
            return False
        
        # Alle Bedingungen müssen erfüllt sein (AND-Logik)
        for condition in rule.conditions:
            result = self._evaluate_condition(condition, current_app, current_process, window_title)
            if not result:
                # Debug: Bedingung nicht erfüllt
                print(f"DEBUG: Regel '{rule.name}' - Bedingung '{condition.condition_type}={condition.value}' nicht erfüllt (current_app={current_app})")
                return False
        
        return True
    
    def _evaluate_condition(self, condition: RuleCondition, current_app: Optional[str],
                           current_process: Optional[str], window_title: str = "") -> bool:
        """
        Evaluiert eine einzelne Bedingung.
        
        Args:
            condition: Zu evaluierende Bedingung
            current_app: Aktuell aktive App
            current_process: Aktuell aktiver Prozess
            window_title: Fenstertitel
            
        Returns:
            True wenn Bedingung erfüllt ist
        """
        condition_type = condition.condition_type
        
        if condition_type == "app_is":
            # App muss genau sein
            return current_app == condition.value
        
        elif condition_type == "app_contains":
            # App muss enthalten sein (case-insensitive)
            return current_app and condition.value.lower() in current_app.lower()
        
        elif condition_type == "app_not":
            # App darf nicht sein
            return current_app != condition.value
        
        elif condition_type == "usage_time_greater":
            # Nutzungszeit mussmehr sein
            try:
                threshold_minutes = float(condition.value)
                usage_minutes = self.usage_tracker.get_app_usage_minutes(
                    current_app, scope="session"
                )
                return usage_minutes > threshold_minutes
            except (ValueError, TypeError):
                return False
        
        elif condition_type == "time_after":
            # Aktuell Zeit muss nach Wertsein
            try:
                target_hour = int(condition.value.split(':')[0])
                target_min = int(condition.value.split(':')[1]) if ':' in condition.value else 0
                now = datetime.now()
                target_time = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
                return now >= target_time
            except (ValueError, IndexError):
                return False
        
        elif condition_type == "time_before":
            # Aktuelle Zeit mussor Wert liegen
            try:
                target_hour = int(condition.value.split(':')[0])
                target_min = int(condition.value.split(':')[1]) if ':' in condition.value else 0
                now = datetime.now()
                target_time = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
                return now <= target_time
            except (ValueError, IndexError):
                return False
        
        elif condition_type == "weekday":
            # Wochentag muss matchen
            weekdays = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                       4: "Friday", 5: "Saturday", 6: "Sunday"}
            current_weekday = weekdays[datetime.now().weekday()]
            return current_weekday == condition.value
        
        return False
