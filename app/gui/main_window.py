"""Haupt-Fenster der Anwendung."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QSystemTrayIcon, QMenu
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import os

from app.core import WindowTracker, UsageTracker, RuleEngine
from app.storage import StorageManager
from app.services import NotificationService
from app.models import Rule

from .dashboard import DashboardWidget
from .rules_manager import RulesManagerWidget
from .statistics import StatisticsWidget
from .settings import SettingsWidget


class MainWindow(QMainWindow):
    """Hauptfenster der SmartCue-Anwendung."""
    
    # Signals
    update_dashboard = pyqtSignal(str, str, float)  # app_name, process_name, usage_minutes
    rule_triggered = pyqtSignal(Rule, str)  # rule, notification_message
    
    def __init__(self):
        """Initialisiert das Hauptfenster."""
        super().__init__()
        
        self.setWindowTitle("SmartCue - Intelligentes Reminder-Tool")
        self.setGeometry(100, 100, 1000, 650)
        
        # Initialisiere Core-Komponenten
        self.storage_manager = StorageManager()
        self.window_tracker = WindowTracker()
        self.usage_tracker = UsageTracker()
        self.rule_engine = RuleEngine(self.usage_tracker)
        self.notification_service = NotificationService()
        
        # Lade Daten
        self.rules = self.storage_manager.load_rules()
        self.settings = self.storage_manager.load_settings()
        
        # GUI-Setup
        self._setup_ui()
        self._setup_tray()
        self._setup_tracking()
        
        # Wende Einstellungen an
        self.notification_service.set_enabled(self.settings.notifications_enabled)
        self.apply_theme(self.settings.theme)
        
        # Signale verbinden
        self.rule_engine.register_trigger_callback(self._on_rule_triggered)
    
    def _setup_ui(self):
        """Richtet die Benutzeroberfläche ein."""
        # Zentral-Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs erstellen
        self.tabs = QTabWidget()
        
        self.dashboard_widget = DashboardWidget(self)
        self.rules_widget = RulesManagerWidget(self)
        self.statistics_widget = StatisticsWidget(self)
        self.settings_widget = SettingsWidget(self)
        
        self.tabs.addTab(self.dashboard_widget, "Dashboard")
        self.tabs.addTab(self.rules_widget, "Regeln")
        self.tabs.addTab(self.statistics_widget, "Statistiken")
        self.tabs.addTab(self.settings_widget, "Einstellungen")
        
        layout.addWidget(self.tabs)
        
        # Menüleiste
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Datei")
        
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("Hilfe")
        about_action = QAction("Über SmartCue", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_tray(self):
        """Richtet das System-Tray ein."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Erstelle Tray-Menü
        tray_menu = QMenu()
        
        show_action = QAction("Anzeigen", self)
        show_action.triggered.connect(self.showNormal)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Verbinde Tray-Icon-Klicks
        self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _on_tray_activated(self, reason):
        """Callback für Tray-Icon Aktivierung."""
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()
    
    def _setup_tracking(self):
        """Richtet das Tracking ein."""
        self.tracking_timer = QTimer()
        self.tracking_timer.timeout.connect(self._track_and_evaluate)
        interval_ms = int(self.settings.tracking_interval_seconds * 1000)
        self.tracking_timer.start(interval_ms)
        
        # Timer zum Speichern der Sitzung (alle 5 Minuten)
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self._save_session_data)
        self.save_timer.start(5 * 60 * 1000)  # 5 Minuten
        
        # Aktueller Dattrack
        from app.utils import get_today_date_str
        self.current_date = get_today_date_str()
    
    def _save_session_data(self):
        """Speichert die aktuelle Sitzungsdaten in der Datenbank."""
        from app.utils import get_today_date_str
        from app.models import DailyUsageStats
        
        today = get_today_date_str()
        
        # Prüfe auf Tagswechsel
        if today != self.current_date:
            # Tag hat sich geändert - speichere alte Daten und reset
            self._finalize_daily_stats(self.current_date)
            self.current_date = today
            self.usage_tracker.reset_today()
        
        # Speichere heutige Statistiken
        daily_stats = self.usage_tracker.get_daily_stats()
        
        if daily_stats:
            stats_model = DailyUsageStats(
                date=today,
                app_usage=daily_stats,
                reminders_triggered=0,
                focus_time_minutes=0
            )
            # Synchronisiere mit Datenbank (aber speichere nur wenn signifikant)
            for app_name, minutes in daily_stats.items():
                if minutes > 0.1:  # Nur wenn mehr als ein paar Sekunden
                    self.storage_manager.update_app_all_time_usage(app_name, minutes)
    
    def _finalize_daily_stats(self, date_str: str):
        """Finalisiert die Statistiken für den gegebenen Tag."""
        from app.models import DailyUsageStats
        
        daily_stats = self.usage_tracker.get_daily_stats()
        if daily_stats:
            stats_model = DailyUsageStats(
                date=date_str,
                app_usage=daily_stats,
                reminders_triggered=0,
                focus_time_minutes=0
            )
            self.storage_manager.save_daily_stats(stats_model)
    
    def _track_and_evaluate(self):
        """Verfolgt die aktive App und evaluiert Regeln."""
        # Hole aktive App
        app_name, process_name, window_title = self.window_tracker.get_active_window()
        
        if app_name is None:
            return
        
        print(f"DEBUG _track_and_evaluate: App={app_name}, Process={process_name}")
        
        # Update Usage Tracker
        self.usage_tracker.update_active_app(app_name, process_name)
        
        # Hole Nutzungsdauer
        usage_minutes = self.usage_tracker.get_app_usage_minutes(app_name, scope="session")
        
        # Emit Signal für Dashboard
        self.update_dashboard.emit(app_name, process_name, usage_minutes)
        
        # Evaluiere Regeln
        triggered_rules = self.rule_engine.evaluate_rules(
            self.rules, app_name, process_name, window_title
        )
        
        for rule in triggered_rules:
            self.rule_triggered.emit(rule, "Regel ausgelöst")
            self._trigger_notification(rule)
    
    def _trigger_notification(self, rule: Rule):
        """Triggert eine Benachrichtigung für eine Regel."""
        print(f"✓ REGEL AUSGELÖST: {rule.name}")
        if rule.actions:
            action = rule.actions[0]  # Nimm erste Aktion
            print(f"  Titel: {action.title}")
            print(f"  Nachricht: {action.message}")
            self.notification_service.show_notification(
                title=action.title,
                message=action.message
            )
        
        # Speichere im Log
        from app.models import ReminderLog
        action = rule.actions[0] if rule.actions else None
        if action:
            reminder_log = ReminderLog(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                title=action.title,
                message=action.message,
            )
            self.storage_manager.log_reminder(reminder_log)
    
    def _on_rule_triggered(self, rule, context):
        """Callback wenn Regel ausgelöst wird."""
        pass  # Wird über Signals gehandhabt
    
    def reload_rules(self):
        """Lädt die Regeln neu."""
        self.rules = self.storage_manager.load_rules()
        self.rules_widget.refresh_list()
    
    def save_rule(self, rule: Rule):
        """Speichert eine Regel."""
        self.storage_manager.save_rule(rule)
        self.reload_rules()
    
    def delete_rule(self, rule_id: str):
        """Löscht eine Regel."""
        self.storage_manager.delete_rule(rule_id)
        self.reload_rules()
    
    def save_settings(self, settings):
        """Speichert die Einstellungen."""
        self.settings = settings
        self.storage_manager.save_settings(settings)
        self.notification_service.set_enabled(settings.notifications_enabled)
    
    def apply_theme(self, theme: str):
        """Wendet ein Theme an."""
        if theme == "dark":
            stylesheet = """
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #444;
                    padding: 8px 15px;
                }
                QTabBar::tab:selected {
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 8px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
                QCheckBox {
                    color: #ffffff;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    background-color: #3d3d3d;
                    border: 2px solid #555;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #0078d4;
                    border: 2px solid #0078d4;
                    image: url(checked);
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #777;
                }
                QSpinBox, QDoubleSpinBox {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                    selection-background-color: #555;
                }
                QSpinBox::up-button, QSpinBox::down-button,
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    background-color: #2d2d2d;
                    border: 1px solid #555;
                    width: 18px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover,
                QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                    background-color: #3d3d3d;
                }
                QComboBox {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    background-color: #2d2d2d;
                    border: 1px solid #555;
                    width: 20px;
                }
                QComboBox QAbstractItemView {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    selection-background-color: #555;
                }
                QTableWidget, QTableView {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    alternate-background-color: #2d2d2d;
                    gridline-color: #444;
                    border: 1px solid #555;
                }
                QTableWidget::item:selected, QTableView::item:selected {
                    background-color: #555;
                }
                QHeaderView::section {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 2px solid #555;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 15px 5px 5px 5px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    top: -5px;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                    selection-background-color: #555;
                }
                QScrollBar:vertical {
                    background-color: #2b2b2b;
                    width: 12px;
                    border: 1px solid #555;
                }
                QScrollBar::handle:vertical {
                    background-color: #555;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #777;
                }
            """
        else:  # light theme
            stylesheet = """
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #ddd;
                    padding: 8px 15px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-bottom: 3px solid #0078d4;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #ddd;
                    padding: 8px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QCheckBox {
                    color: #000000;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    background-color: #ffffff;
                    border: 2px solid #ddd;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #0078d4;
                    border: 2px solid #0078d4;
                    image: url(checked);
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #999;
                }
                QSpinBox, QDoubleSpinBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ddd;
                    padding: 5px;
                    selection-background-color: #ddd;
                }
                QSpinBox::up-button, QSpinBox::down-button,
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    background-color: #f0f0f0;
                    border: 1px solid #ddd;
                    width: 18px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover,
                QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                    background-color: #e0e0e0;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ddd;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    background-color: #f0f0f0;
                    border: 1px solid #ddd;
                    width: 20px;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #000000;
                    selection-background-color: #ddd;
                }
                QTableWidget, QTableView {
                    background-color: #ffffff;
                    color: #000000;
                    alternate-background-color: #f5f5f5;
                    gridline-color: #ddd;
                    border: 1px solid #ddd;
                }
                QTableWidget::item:selected, QTableView::item:selected {
                    background-color: #ddd;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #ddd;
                    padding: 5px;
                }
                QGroupBox {
                    color: #000000;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 15px 5px 5px 5px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    top: -5px;
                }
                QLabel {
                    color: #000000;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ddd;
                    padding: 5px;
                    selection-background-color: #ddd;
                }
                QScrollBar:vertical {
                    background-color: #ffffff;
                    width: 12px;
                    border: 1px solid #ddd;
                }
                QScrollBar::handle:vertical {
                    background-color: #ddd;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #bbb;
                }
            """
        
        self.setStyleSheet(stylesheet)
    
    def _show_about(self):
        """Zeigt About-Dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Über SmartCue",
            "SmartCue v1.0\n\n"
            "Ein intelligentes Reminder- und Fokus-Tool für Windows.\n\n"
            "(c) 2026"
        )
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird."""
        # Speichere Sitzungsdaten bevor die App beendet wird
        self._save_session_data()
        
        if self.settings.start_minimized:
            self.hide()
            event.ignore()
        else:
            self.tracking_timer.stop()
            if hasattr(self, 'save_timer'):
                self.save_timer.stop()
            event.accept()
    
    def changeEvent(self, event):
        """Verwaltet Fenster-Events."""
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() == (self.windowState() | Qt.WindowState.WindowMinimized):
                self.hide()
                event.ignore()
            else:
                super().changeEvent(event)
        else:
            super().changeEvent(event)
