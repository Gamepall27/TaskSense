"""Dashboard-Widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QDialog, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

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
    
    def _create_card_title(self, text: str, accent_color: str = "#3498db") -> QLabel:
        """Erstellt einen formatierten Kartentitel mit Akzent-Linie.
        
        Args:
            text: Der Titel-Text
            accent_color: Akzentfarbe für linke Linie (hex format)
        
        Returns:
            QLabel mit formatiertem Titel und Akzent
        """
        title_label = QLabel(text)
        
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Erkenne Dark Mode
        bg_color = self.palette().color(self.backgroundRole())
        bg_brightness = bg_color.lightness()
        is_dark_mode = bg_brightness < 128
        
        # Passe Hintergrundfarbe basierend auf Dark Mode an
        if is_dark_mode:
            bg_color_hex = "#2D3139"  # Dunkelgrau für Dark Mode
            text_color = "#FFFFFF"  # Weiß für Dark Mode
        else:
            bg_color_hex = "#f8f9fa"  # Hellgrau für Light Mode
            text_color = accent_color
        
        # Stilisierung mit linker Akzent-Linie statt voller Hintergrund
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                padding-left: 12px;
                padding-right: 12px;
                padding-top: 8px;
                padding-bottom: 8px;
                border-left: 4px solid {accent_color};
                background-color: {bg_color_hex};
                border-radius: 3px;
            }}
        """)
        
        title_label.setMinimumHeight(40)
        return title_label
    
    def _setup_ui(self):
        """Richtet die UI ein mit modernem, zentriertem Design."""
        # Hauptlayout mit ScrollArea
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Content Widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # === Aktuelle App Section (Zentriert) ===
        active_title_frame = self._create_card_title("Aktive App", "#6B7280")
        layout.addWidget(active_title_frame)
        
        current_group = QGroupBox("")
        current_group.setMaximumWidth(500)
        current_layout = QVBoxLayout()
        current_layout.setSpacing(10)
        current_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.app_name_label = QLabel("Keine aktive App")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.app_name_label.setFont(font)
        self.app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.usage_label = QLabel("Nutzungsdauer: 0m")
        font.setPointSize(12)
        self.usage_label.setFont(font)
        self.usage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.process_label = QLabel("")
        font.setPointSize(10)
        self.process_label.setFont(font)
        self.process_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        current_layout.addWidget(self.app_name_label)
        current_layout.addWidget(self.usage_label)
        current_layout.addWidget(self.process_label)
        current_group.setLayout(current_layout)
        
        # Container für zentrierte Gruppierung
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.addStretch()
        center_layout.addWidget(current_group)
        center_layout.addStretch()
        
        layout.addWidget(center_container)
        
        # === Top Apps ===
        layout.addSpacing(10)
        top_label_frame = self._create_card_title("Top 5 Apps heute", "#7C3AED")
        layout.addWidget(top_label_frame)
        top_group = QGroupBox("")
        top_layout = QVBoxLayout()
        
        self.top_apps_table = QTableWidget(5, 2)
        self.top_apps_table.setHorizontalHeaderLabels(["App", "Nutzungsdauer"])
        self.top_apps_table.resizeColumnsToContents()
        self.top_apps_table.setColumnWidth(0, 200)
        self.top_apps_table.setColumnWidth(1, 200)
        # Erhöhe Zeilenhöhe
        self.top_apps_table.verticalHeader().setDefaultSectionSize(50)
        self.top_apps_table.setMinimumHeight(300)
        # Verbinde Double-Click Event
        self.top_apps_table.itemDoubleClicked.connect(self._on_app_double_clicked)
        
        top_layout.addWidget(self.top_apps_table)
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)
        
        # Letzte Erinnerung
        reminder_title_frame = self._create_card_title("Letzte Erinnerung", "#F59E0B")
        layout.addWidget(reminder_title_frame)
        
        reminder_group = QGroupBox("")
        reminder_layout = QVBoxLayout()
        
        self.last_reminder_label = QLabel("Keine Erinnerung ausgelöst")
        reminder_layout.addWidget(self.last_reminder_label)
        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)
        
        layout.addStretch()
        
        # ScrollArea zusammensetzen
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
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
