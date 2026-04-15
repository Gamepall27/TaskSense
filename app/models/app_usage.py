"""App-Nutzungs-Datenmodelle."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass
class AppUsageEntry:
    """Ein Eintrag für App-Nutzung."""
    
    app_name: str
    process_name: str
    window_title: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = None
    duration_minutes: float = 0.0
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            'app_name': self.app_name,
            'process_name': self.process_name,
            'window_title': self.window_title,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
        }


@dataclass
class DailyUsageStats:
    """Tägliche Nutzungsstatistiken."""
    
    date: str  # YYYY-MM-DD
    app_usage: Dict[str, float] = field(default_factory=dict)  # app_name -> minutes
    reminders_triggered: int = 0
    focus_time_minutes: int = 0
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            'date': self.date,
            'app_usage': self.app_usage,
            'reminders_triggered': self.reminders_triggered,
            'focus_time_minutes': self.focus_time_minutes,
        }
    
    def add_app_usage(self, app_name: str, minutes: float):
        """Addiert Nutzungszeit zu einer App."""
        if app_name not in self.app_usage:
            self.app_usage[app_name] = 0.0
        self.app_usage[app_name] += minutes
    
    def get_top_apps(self, limit: int = 5) -> list:
        """Gibt die meistgenutzten Apps zurück."""
        sorted_apps = sorted(
            self.app_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_apps[:limit]
