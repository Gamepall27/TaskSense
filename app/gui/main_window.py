"""Haupt-Fenster der Anwendung."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import os

from app import __version__
from app.core import WindowTracker, UsageTracker, RuleEngine
from app.product import PRODUCT
from app.storage import StorageManager
from app.services import NotificationService
from app.models import Rule
from app.utils.icon_utils import create_app_icon

from .dashboard import DashboardWidget
from .rules_manager import RulesManagerWidget
from .statistics import StatisticsWidget
from .settings import SettingsWidget
from .mini_stats import MiniStatsWindow


class MainWindow(QMainWindow):
    """Hauptfenster der TaskSense-Anwendung."""
    
    # Signals
    update_dashboard = pyqtSignal(str, str, float)  # app_name, process_name, usage_minutes
    rule_triggered = pyqtSignal(Rule, str)  # rule, notification_message
    
    def __init__(self):
        """Initialisiert das Hauptfenster."""
        super().__init__()
        self.product = PRODUCT
        
        self.setWindowTitle(f"{self.product.display_name} - Intelligentes Reminder-Tool")
        self.setGeometry(100, 100, 1000, 650)
        
        # Setze App-Icon
        app_icon = create_app_icon(64)
        self.setWindowIcon(app_icon)
        
        # Flag für echtes Beenden (nicht nur Minimieren)
        self._really_closing = False
        
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
        
        # Erstelle Mini-Statistik-Fenster
        self.mini_stats_window = MiniStatsWindow(self)
        
        # Wende Einstellungen an
        self.notification_service.set_enabled(self.settings.notifications_enabled)
        self.apply_theme(self.settings.theme)
        
        # Starte minimiert wenn Einstellung aktiv ist
        if self.settings.start_minimized:
            self.hide()
        
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
        exit_action.triggered.connect(self._quit_app)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("Hilfe")
        about_action = QAction(f"Über {self.product.display_name}", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_tray(self):
        """Richtet das System-Tray ein."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Setze Icon für Tray
        tray_icon = create_app_icon(32)
        self.tray_icon.setIcon(tray_icon)
        self.tray_icon.setToolTip(f"{self.product.display_name} - Intelligentes Reminder-Tool")
        
        # Erstelle Tray-Menü
        tray_menu = QMenu()
        
        show_action = QAction("Anzeigen", self)
        show_action.triggered.connect(self.showNormal)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Verbinde Tray-Icon-Klicks
        self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _on_tray_activated(self, reason):
        """Callback für Tray-Icon Aktivierung."""
        from PyQt6.QtWidgets import QSystemTrayIcon
        
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Linksklick: Mini-Fenster anzeigen
            if self.mini_stats_window.isVisible():
                self.mini_stats_window.hide()
            else:
                self.mini_stats_window.show()
                self.mini_stats_window.activateWindow()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Doppelklick: Hauptfenster anzeigen/verstecken
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()
    
    def _quit_app(self):
        """Beendet die Anwendung."""
        try:
            # Stoppe alle Timer zuerst
            if hasattr(self, 'tracking_timer'):
                self.tracking_timer.stop()
            if hasattr(self, 'save_timer'):
                self.save_timer.stop()
            
            # Speichere noch einmal alle Daten
            self._save_session_data()
            
            # Schließe das Mini-Fenster
            if hasattr(self, 'mini_stats_window') and self.mini_stats_window:
                try:
                    self.mini_stats_window.update_timer.stop()
                except:
                    pass
                try:
                    self.mini_stats_window.close()
                except:
                    pass
            
            # Setze Flag und beende die Anwendung
            self._really_closing = True
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
        except Exception as e:
            print(f"Fehler beim Beenden: {e}")
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
    
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
    
    def can_create_rule(self, existing_rule_id: str = None, show_dialog: bool = True) -> bool:
        """Prüft, ob eine weitere Regel in der aktuellen Edition erlaubt ist."""
        if self.product.max_rules is None:
            return True

        if existing_rule_id and any(rule.rule_id == existing_rule_id for rule in self.rules):
            return True

        if len(self.rules) < self.product.max_rules:
            return True

        if show_dialog:
            self.show_pro_upgrade_dialog(
                "Regel-Limit erreicht",
                (
                    f"In {self.product.display_name} sind maximal "
                    f"{self.product.max_rules} Regeln verfügbar."
                ),
            )

        return False

    def show_pro_upgrade_dialog(self, title: str, details: str):
        """Zeigt einen Upgrade-Hinweis für Lite-Funktionen."""
        QMessageBox.information(
            self,
            title,
            f"{details}\n\n{self.product.upgrade_pitch}",
        )

    def save_rule(self, rule: Rule):
        """Speichert eine Regel."""
        if not self.can_create_rule(existing_rule_id=rule.rule_id):
            return False
        self.storage_manager.save_rule(rule)
        self.reload_rules()
        return True
    
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
        """Wendet ein modernes, professionelles Theme an."""
        # Moderne Farbpalette
        colors = {
            'primary': '#4A90E2',      # Hauptblau
            'primary_hover': '#357ABD',
            'secondary': '#F39C12',    # Orange-Akzent
            'danger': '#E74C3C',       # Rot
            'success': '#27AE60',      # Grün
            'bg_dark': '#1A1D23',      # Sehr dunkles Grau
            'bg_card': '#242935',      # Dunkel-Karte
            'text_light': '#ECEFF1',   # Helles Text
            'text_muted': '#B0BEC5',   # Gedimmter Text
            'border': '#384856',       # Rand
        }
        
        if theme == "dark":
            stylesheet = f"""
                /* ===== MAIN WINDOW ===== */
                QMainWindow {{
                    background-color: {colors['bg_dark']};
                    color: {colors['text_light']};
                }}
                
                QWidget {{
                    background-color: {colors['bg_dark']};
                    color: {colors['text_light']};
                }}
                
                /* ===== TABS ===== */
                QTabWidget::pane {{
                    border: 0px;
                    background-color: {colors['bg_dark']};
                }}
                
                QTabBar {{
                    background-color: {colors['bg_dark']};
                    border-bottom: 2px solid {colors['border']};
                }}
                
                QTabBar::tab {{
                    background-color: transparent;
                    color: {colors['text_muted']};
                    padding: 12px 20px;
                    border: 0px;
                    font-weight: 500;
                    font-size: 11pt;
                    margin-right: 5px;
                }}
                
                QTabBar::tab:hover {{
                    color: {colors['text_light']};
                    border-bottom: 3px solid {colors['primary']};
                }}
                
                QTabBar::tab:selected {{
                    color: {colors['primary']};
                    border-bottom: 3px solid {colors['primary']};
                }}
                
                /* ===== BUTTONS ===== */
                QPushButton {{
                    background-color: {colors['primary']};
                    color: white;
                    border: 0px;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 10pt;
                    min-height: 35px;
                    margin: 3px;
                }}
                
                QPushButton:hover {{
                    background-color: {colors['primary_hover']};
                    border: 2px solid {colors['primary']};
                    padding: 8px 18px;
                }}
                
                QPushButton:pressed {{
                    background-color: #2E5AAE;
                    border: 2px solid {colors['primary']};
                    padding: 8px 18px;
                }}
                
                QPushButton[flat="false"] {{
                    background-color: {colors['bg_card']};
                    color: {colors['text_light']};
                    border: 2px solid {colors['border']};
                }}
                
                QPushButton[flat="false"]:hover {{
                    background-color: {colors['border']};
                    border: 2px solid {colors['primary']};
                }}
                
                /* Danger Buttons */
                QPushButton#dangerButton {{
                    background-color: {colors['danger']};
                }}
                
                QPushButton#dangerButton:hover {{
                    background-color: #C0392B;
                }}
                
                /* ===== LABELS ===== */
                QLabel {{
                    color: {colors['text_light']};
                    font-size: 10pt;
                }}
                
                QLabel#titleLabel {{
                    font-weight: bold;
                    font-size: 14pt;
                    color: {colors['primary']};
                }}
                
                QLabel#subtitleLabel {{
                    color: {colors['text_muted']};
                    font-size: 9pt;
                }}
                
                /* ===== INPUTS ===== */
                QLineEdit, QPlainTextEdit, QTextEdit {{
                    background-color: {colors['bg_card']};
                    color: {colors['text_light']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px;
                    selection-background-color: {colors['primary']};
                    font-size: 10pt;
                }}
                
                QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
                    border: 2px solid {colors['primary']};
                    background-color: {colors['bg_card']};
                }}
                
                QSpinBox, QDoubleSpinBox {{
                    background-color: {colors['bg_card']};
                    color: {colors['text_light']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 5px;
                    selection-background-color: {colors['primary']};
                }}
                
                QSpinBox::up-button, QSpinBox::down-button,
                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                    background-color: {colors['border']};
                    border: 0px;
                    width: 20px;
                }}
                
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                    background-color: {colors['primary']};
                }}
                
                QComboBox {{
                    background-color: {colors['bg_card']};
                    color: {colors['text_light']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 10pt;
                }}
                
                QComboBox::drop-down {{
                    background-color: {colors['border']};
                    border: 0px;
                    border-radius: 0px 6px 6px 0px;
                    width: 30px;
                }}
                
                QComboBox QAbstractItemView {{
                    background-color: {colors['bg_card']};
                    color: {colors['text_light']};
                    selection-background-color: {colors['primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 6px;
                }}
                
                /* ===== CHECKBOXES ===== */
                QCheckBox {{
                    color: {colors['text_light']};
                    spacing: 8px;
                    font-size: 10pt;
                }}
                
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    background-color: {colors['bg_card']};
                    border: 2px solid {colors['border']};
                    border-radius: 4px;
                }}
                
                QCheckBox::indicator:checked {{
                    background-color: {colors['primary']};
                    border: 2px solid {colors['primary']};
                }}
                
                QCheckBox::indicator:hover {{
                    border: 2px solid {colors['primary']};
                }}
                
                /* ===== TABLES ===== */
                QTableWidget, QTableView {{
                    background-color: {colors['bg_dark']};
                    color: {colors['text_light']};
                    alternate-background-color: {colors['bg_card']};
                    gridline-color: {colors['border']};
                    border: 1px solid {colors['border']};
                    border-radius: 6px;
                }}
                
                QTableWidget::item, QTableView::item {{
                    padding: 5px;
                    border-bottom: 1px solid {colors['border']};
                }}
                
                QTableWidget::item:selected, QTableView::item:selected {{
                    background-color: {colors['primary']};
                    color: white;
                }}
                
                QHeaderView::section {{
                    background-color: {colors['bg_card']};
                    color: {colors['text_light']};
                    border: 0px;
                    padding: 8px;
                    font-weight: bold;
                    border-right: 1px solid {colors['border']};
                }}
                
                /* ===== GROUPBOX ===== */
                QGroupBox {{
                    color: {colors['text_light']};
                    border: 2px solid {colors['border']};
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 15px 5px 5px 5px;
                    margin-top: 10px;
                    font-size: 11pt;
                }}
                
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                    top: -8px;
                    color: {colors['primary']};
                }}
                
                /* ===== SCROLLBARS ===== */
                QScrollBar:vertical {{
                    background-color: {colors['bg_dark']};
                    width: 12px;
                    border: 0px;
                }}
                
                QScrollBar::handle:vertical {{
                    background-color: {colors['border']};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                
                QScrollBar::handle:vertical:hover {{
                    background-color: {colors['primary']};
                }}
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    border: 0px;
                    background: transparent;
                }}
                
                QScrollBar:horizontal {{
                    background-color: {colors['bg_dark']};
                    height: 12px;
                    border: 0px;
                }}
                
                QScrollBar::handle:horizontal {{
                    background-color: {colors['border']};
                    border-radius: 6px;
                    min-width: 20px;
                }}
                
                QScrollBar::handle:horizontal:hover {{
                    background-color: {colors['primary']};
                }}
                
                /* ===== MENU ===== */
                QMenuBar {{
                    background-color: {colors['bg_dark']};
                    color: {colors['text_light']};
                    border-bottom: 1px solid {colors['border']};
                    spacing: 10px;
                }}
                
                QMenuBar::item:selected {{
                    background-color: {colors['primary']};
                    color: white;
                    border-radius: 4px;
                }}
                
                QMenu {{
                    background-color: {colors['bg_card']};
                    color: {colors['text_light']};
                    border: 1px solid {colors['border']};
                    border-radius: 6px;
                    padding: 5px 0px;
                }}
                
                QMenu::item:selected {{
                    background-color: {colors['primary']};
                    color: white;
                    padding-left: 20px;
                    padding-right: 20px;
                }}
            """
        else:  # light theme
            light_colors = {
                'primary': '#4A90E2',
                'primary_hover': '#357ABD',
                'bg_main': '#F8F9FA',
                'bg_card': '#FFFFFF',
                'text': '#2C3E50',
                'text_muted': '#7F8C8D',
                'border': '#E1E8ED',
                'danger': '#E74C3C',
            }
            
            stylesheet = f"""
                QMainWindow {{
                    background-color: {light_colors['bg_main']};
                    color: {light_colors['text']};
                }}
                
                QWidget {{
                    background-color: {light_colors['bg_main']};
                    color: {light_colors['text']};
                }}
                
                QTabBar {{
                    background-color: transparent;
                    border-bottom: 2px solid {light_colors['border']};
                }}
                
                QTabBar::tab {{
                    background-color: transparent;
                    color: {light_colors['text_muted']};
                    padding: 12px 20px;
                    border: 0px;
                    font-weight: 500;
                    font-size: 11pt;
                }}
                
                QTabBar::tab:selected {{
                    color: {light_colors['primary']};
                    border-bottom: 3px solid {light_colors['primary']};
                }}
                
                QPushButton {{
                    background-color: {light_colors['primary']};
                    color: white;
                    border: 0px;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 10pt;
                    min-height: 35px;
                }}
                
                QPushButton:hover {{
                    background-color: {light_colors['primary_hover']};
                }}
                
                QPushButton[flat="false"] {{
                    background-color: {light_colors['bg_card']};
                    color: {light_colors['text']};
                    border: 2px solid {light_colors['border']};
                }}
                
                QPushButton#dangerButton {{
                    background-color: {light_colors['danger']};
                }}
                
                QPushButton#dangerButton:hover {{
                    background-color: #C0392B;
                }}
                
                QLabel {{
                    color: {light_colors['text']};
                }}
                
                QLineEdit, QPlainTextEdit {{
                    background-color: {light_colors['bg_card']};
                    color: {light_colors['text']};
                    border: 2px solid {light_colors['border']};
                    border-radius: 6px;
                    padding: 8px;
                }}
                
                QLineEdit:focus {{
                    border: 2px solid {light_colors['primary']};
                }}
                
                QTableWidget, QTableView {{
                    background-color: {light_colors['bg_card']};
                    color: {light_colors['text']};
                    alternate-background-color: {light_colors['bg_main']};
                    gridline-color: {light_colors['border']};
                    border: 1px solid {light_colors['border']};
                    border-radius: 6px;
                }}
                
                QTableWidget::item:selected, QTableView::item:selected {{
                    background-color: {light_colors['primary']};
                    color: white;
                }}
            """
        
        self.setStyleSheet(stylesheet)
    
    def _show_about(self):
        """Zeigt About-Dialog."""
        QMessageBox.information(
            self,
            f"Über {self.product.display_name}",
            f"{self.product.display_name} v{__version__}\n\n"
            "Ein intelligentes Reminder- und Fokus-Tool für Windows.\n\n"
            "(c) 2026"
        )
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird."""
        # Wenn wirklich beenden aufgerufen wurde, beende die App
        if self._really_closing:
            try:
                # Speichere Sitzungsdaten
                self._save_session_data()
                
                # Stoppe alle Timer
                self.tracking_timer.stop()
                if hasattr(self, 'save_timer'):
                    self.save_timer.stop()
                
                # Schließe das Mini-Fenster
                if hasattr(self, 'mini_stats_window') and self.mini_stats_window:
                    self.mini_stats_window.update_timer.stop()
                    self.mini_stats_window.close()
            except Exception as e:
                print(f"Fehler beim Beenden: {e}")
            
            event.accept()
        else:
            # Minimiere ins Tray statt zu schließen
            self._save_session_data()
            self.hide()
            # Verstecke auch das Mini-Fenster
            if hasattr(self, 'mini_stats_window') and self.mini_stats_window:
                self.mini_stats_window.hide()
            event.ignore()
    
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
