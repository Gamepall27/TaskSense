"""Dashboard-Widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.utils import format_minutes, get_today_date_str


class DashboardWidget(QWidget):
    """Dashboard mit Übersicht der aktiven App und Statistiken."""
    
    def __init__(self, main_window):
        """Initialisiert das Dashboard."""
        super().__init__()
        self.main_window = main_window
        
        self._setup_ui()
        
        # Verbinde Signals
        self.main_window.update_dashboard.connect(self._update_active_app)
    
    def _setup_ui(self):
        """Richtet die UI ein."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Aktuelle App
        current_group = QGroupBox("Aktuell aktive Anwendung")
        current_layout = QVBoxLayout()
        
        self.app_name_label = QLabel("Keine aktive App")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.app_name_label.setFont(font)
        
        self.usage_label = QLabel("Nutzungsdauer: 0m")
        font.setPointSize(11)
        self.usage_label.setFont(font)
        
        current_layout.addWidget(self.app_name_label)
        current_layout.addWidget(self.usage_label)
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # Top Apps
        top_group = QGroupBox("Heute meistgenutzte Apps")
        top_layout = QVBoxLayout()
        
        self.top_apps_table = QTableWidget(5, 2)
        self.top_apps_table.setHorizontalHeaderLabels(["App", "Nutzungsdauer"])
        self.top_apps_table.resizeColumnsToContents()
        self.top_apps_table.setColumnWidth(0, 200)
        self.top_apps_table.setColumnWidth(1, 200)
        # Verbinde Double-Click Event
        self.top_apps_table.itemDoubleClicked.connect(self._on_app_double_clicked)
        
        top_layout.addWidget(self.top_apps_table)
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)
        
        # Letzte Erinnerung
        reminder_group = QGroupBox("Letzte ausgelöste Erinnerung")
        reminder_layout = QVBoxLayout()
        
        self.last_reminder_label = QLabel("Keine Erinnerung ausgelöst")
        reminder_layout.addWidget(self.last_reminder_label)
        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)
        
        layout.addStretch()
    
    def _update_active_app(self, app_name: str, process_name: str, usage_minutes: float):
        """Updated die Anzeige der aktiven App."""
        self.app_name_label.setText(f"App: {app_name} ({process_name})")
        self.usage_label.setText(f"Nutzungsdauer: {format_minutes(usage_minutes)}")
        
        # Update Top Apps
        self._refresh_top_apps()
    
    def _refresh_top_apps(self):
        """Aktualisiert die Liste der meistgenutzten Apps."""
        daily_stats = self.main_window.usage_tracker.get_daily_stats()
        
        # Sortiere nach Nutzungsdauer
        sorted_apps = sorted(daily_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Fülle Tabelle
        self.top_apps_table.setRowCount(len(sorted_apps))
        
        for row, (app_name, minutes) in enumerate(sorted_apps):
            self.top_apps_table.setItem(row, 0, QTableWidgetItem(app_name))
            self.top_apps_table.setItem(row, 1, QTableWidgetItem(format_minutes(minutes)))
    
    def _on_app_double_clicked(self, item):
        """Handler: Öffnet Rule-Editor Dialog beim Double-Click auf eine App."""
        from app.gui.rules_manager import RuleEditorDialog
        from app.models import Rule, RuleCondition, RuleAction
        
        # Hole App-Name aus der ersten Spalte
        row = item.row()
        app_item = self.top_apps_table.item(row, 0)
        if not app_item:
            return
        
        app_name = app_item.text()
        
        # Erstelle neue Regel mit Vorbefüllung
        new_rule = Rule()
        new_rule.name = f"Erinnerung für {app_name}"
        new_rule.conditions = [
            RuleCondition(
                condition_type="app_is",
                value=app_name
            )
        ]
        new_rule.actions = [
            RuleAction(
                title=f"{app_name} aktiv",
                message=f"Die App {app_name} ist aktiv. Möchten Sie pausieren?"
            )
        ]
        
        # Öffne Dialog
        dialog = RuleEditorDialog(new_rule, self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.main_window.save_rule(rule)
