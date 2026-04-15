"""Regel-Datenmodelle für SmartCue."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import uuid


@dataclass
class RuleCondition:
    """Eine einzelne Bedingung einer Regel."""
    
    condition_type: str  # 'app_is', 'usage_time', 'time_after', 'weekday', etc.
    value: str  # Wert für die Bedingung
    operator: str = "equals"  # equals, not_equals, greater_than, less_than, etc.
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            'condition_type': self.condition_type,
            'value': self.value,
            'operator': self.operator,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RuleCondition':
        """Erstellt aus Dictionary."""
        return cls(
            condition_type=data.get('condition_type', ''),
            value=data.get('value', ''),
            operator=data.get('operator', 'equals'),
        )


@dataclass
class RuleAction:
    """Eine zu berechnende Aktion, wenn die Regel ausgelöst wird."""
    
    action_type: str = "notify"  # notify, log, execute, etc.
    title: str = ""
    message: str = ""
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            'action_type': self.action_type,
            'title': self.title,
            'message': self.message,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RuleAction':
        """Erstellt aus Dictionary."""
        return cls(
            action_type=data.get('action_type', 'notify'),
            title=data.get('title', ''),
            message=data.get('message', ''),
        )


@dataclass
class Rule:
    """Eine Regel für SmartCue."""
    
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    enabled: bool = True
    conditions: List[RuleCondition] = field(default_factory=list)
    actions: List[RuleAction] = field(default_factory=list)
    cooldown_minutes: int = 15
    last_triggered: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    priority: int = 0
    recurring_pattern: str = "daily"  # once, daily, weekly, weekly_specific (default: daily)
    recurring_weekdays: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday (für weekly_specific)
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary für Speicherung."""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'enabled': self.enabled,
            'conditions': [c.to_dict() for c in self.conditions],
            'actions': [a.to_dict() for a in self.actions],
            'cooldown_minutes': self.cooldown_minutes,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'created_at': self.created_at.isoformat(),
            'tags': self.tags,
            'priority': self.priority,
            'recurring_pattern': self.recurring_pattern,
            'recurring_weekdays': self.recurring_weekdays,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Rule':
        """Erstellt Regel aus Dictionary."""
        return cls(
            rule_id=data.get('rule_id', str(uuid.uuid4())),
            name=data.get('name', ''),
            enabled=data.get('enabled', True),
            conditions=[RuleCondition.from_dict(c) for c in data.get('conditions', [])],
            actions=[RuleAction.from_dict(a) for a in data.get('actions', [])],
            cooldown_minutes=data.get('cooldown_minutes', 15),
            last_triggered=datetime.fromisoformat(data['last_triggered']) 
                if data.get('last_triggered') else None,
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            tags=data.get('tags', []),
            priority=data.get('priority', 0),
            recurring_pattern=data.get('recurring_pattern', 'once'),
            recurring_weekdays=data.get('recurring_weekdays', []),
        )
    
    def is_cooldown_expired(self) -> bool:
        """Prüft, ob der Cooldown abgelaufen ist."""
        if self.last_triggered is None:
            return True
        
        # Bei wiederholenden Regeln: Prüfe nicht nur Cooldown, sondern auch das Muster
        if self.recurring_pattern != "once":
            return self._check_recurring_pattern()
        
        # Für "once" Regeln: normaler Cooldown
        elapsed = (datetime.now() - self.last_triggered).total_seconds() / 60
        return elapsed >= self.cooldown_minutes
    
    def _check_recurring_pattern(self) -> bool:
        """
        Prüft, ob eine wiederholende Regel erneut auslöst werden kann.
        """
        if not self.last_triggered:
            return True
        
        now = datetime.now()
        
        if self.recurring_pattern == "daily":
            # Täglich: Prüfe, ob an einem anderen Tag ausgelöst wurde
            return now.date() != self.last_triggered.date()
        
        elif self.recurring_pattern == "weekly":
            # Wöchentlich: Prüfe, ob mindestens 7 Tage vergangen sind
            elapsed_days = (now - self.last_triggered).days
            return elapsed_days >= 7
        
        elif self.recurring_pattern == "weekly_specific":
            # Wöchentlich an bestimmten Wochentagen
            if not self.recurring_weekdays:
                return False
            
            current_weekday = now.weekday()
            
            # Prüfe, ob heute ein Recurring-Wochentag ist
            if current_weekday not in self.recurring_weekdays:
                return False
            
            # Prüfe, ob heute bereits ausgelöst wurde
            if now.date() == self.last_triggered.date():
                return False
            
            return True
        
        return False
    
    def can_trigger(self) -> bool:
        """Prüft, ob die Regel ausgelöst werden kann."""
        return self.enabled and self.is_cooldown_expired()
    
    def mark_triggered(self):
        """Markiert die Regel als ausgelöst."""
        self.last_triggered = datetime.now()
