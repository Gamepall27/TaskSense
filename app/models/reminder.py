"""Reminder-Logging Modelle."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReminderLog:
    """Protokoll einer ausgelösten Erinnerung."""
    
    rule_id: str
    rule_name: str
    title: str
    message: str
    triggered_at: datetime = field(default_factory=datetime.now)
    dismissed: bool = False
    snoozed_until: datetime = None
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'title': self.title,
            'message': self.message,
            'triggered_at': self.triggered_at.isoformat(),
            'dismissed': self.dismissed,
            'snoozed_until': self.snoozed_until.isoformat() if self.snoozed_until else None,
        }
