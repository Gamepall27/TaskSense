"""Einstellungsmodell für TaskSense."""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Settings:
    """Anwendungseinstellungen."""
    
    tracking_interval_seconds: int = 2
    notifications_enabled: bool = True
    start_minimized: bool = True
    theme: str = "light"  # light, dark
    check_for_updates: bool = True
    data_retention_days: int = 90
    enable_statistics: bool = True
    custom_settings: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            'tracking_interval_seconds': self.tracking_interval_seconds,
            'notifications_enabled': self.notifications_enabled,
            'start_minimized': self.start_minimized,
            'theme': self.theme,
            'check_for_updates': self.check_for_updates,
            'data_retention_days': self.data_retention_days,
            'enable_statistics': self.enable_statistics,
            'custom_settings': self.custom_settings,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        """Erstellt aus Dictionary."""
        return cls(
            tracking_interval_seconds=data.get('tracking_interval_seconds', 2),
            notifications_enabled=data.get('notifications_enabled', True),
            start_minimized=data.get('start_minimized', True),
            theme=data.get('theme', 'light'),
            check_for_updates=data.get('check_for_updates', True),
            data_retention_days=data.get('data_retention_days', 90),
            enable_statistics=data.get('enable_statistics', True),
            custom_settings=data.get('custom_settings', {}),
        )
