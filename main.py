"""Haupteinstiegspunkt der TaskSense-Anwendung."""
import sys
import os

# Stelle sicher, dass das Projektverzeichnis im Path ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from app.gui import MainWindow
from app.storage import StorageManager
from app.config import EXAMPLE_RULES


def create_example_rules():
    """Erstellt Beispielregeln beim ersten Start."""
    storage_manager = StorageManager()
    rules = storage_manager.load_rules()
    
    # Falls noch keine Regeln existieren, erstelle Beispiele
    if not rules:
        from app.models import Rule, RuleCondition, RuleAction
        import uuid
        
        for example in EXAMPLE_RULES:
            rule = Rule(
                rule_id=str(uuid.uuid4()),
                name=example['name'],
                enabled=True,
                conditions=[
                    RuleCondition(
                        condition_type=example['condition_type'],
                        value=example['condition_value'],
                    )
                ],
                actions=[
                    RuleAction(
                        title=example['action_title'],
                        message=example['action_message'],
                    )
                ],
                cooldown_minutes=example.get('cooldown_minutes', 15),
            )
            storage_manager.save_rule(rule)


def main():
    """Startet die TaskSense-Anwendung."""
    # Erstelle Beispielregeln wenn nötig
    create_example_rules()
    
    # Erstelle QApplication
    app = QApplication(sys.argv)
    
    # Erstelle und zeige Hauptfenster
    main_window = MainWindow()
    
    # Prüfe, ob die App minimiert starten soll
    if not main_window.settings.start_minimized:
        main_window.show()
    
    # Starte Event Loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
