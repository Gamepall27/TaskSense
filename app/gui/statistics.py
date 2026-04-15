"""Statistik-Widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog,
    QPushButton, QCheckBox, QMessageBox, QScrollArea, QGroupBox, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

from app.utils import format_minutes, get_today_date_str
from app.gui.charts import BarChartWidget, PieChartWidget, HeatmapWidget
from app.gui.custom_widgets import CustomCheckBox


class StatisticsWidget(QWidget):
    """Widget für Statistiken und Auswertungen."""
    
    def __init__(self, main_window):
        """Initialisiert das Statistik-Widget."""
        super().__init__()
        self.main_window = main_window
        self.enabled_visualizations = {
            "table_today": True,
            "table_reminders": True,
            "table_all_time": True,
        }
        
        self._setup_ui()
        self._refresh_statistics()
        
        # Verbinde Signal für Daten-Updates
        self.main_window.update_dashboard.connect(self._on_data_updated)
    
    def _setup_ui(self):
        """Richtet die UI ein."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Settings Button
        settings_btn = QPushButton("Visualisierungen konfigurieren")
        settings_btn.clicked.connect(self._open_visualization_settings)
        layout.addWidget(settings_btn)
        
        # Tab-Widget
        self.tabs = QTabWidget()
        
        # Tab 1: Heute
        today_widget = QWidget()
        today_layout = QVBoxLayout()
        
        self.today_bar_chart = BarChartWidget()
        today_layout.addWidget(QLabel("Balkendiagramm - Heute"))
        today_layout.addWidget(self.today_bar_chart)
        
        self.today_pie_chart = PieChartWidget()
        today_layout.addWidget(QLabel("Kreisdiagramm - Heute"))
        today_layout.addWidget(self.today_pie_chart)
        
        today_widget.setLayout(today_layout)
        self.tabs.addTab(today_widget, "Heute")
        
        # Tab 2: Gesamtzeit
        alltime_widget = QWidget()
        alltime_layout = QVBoxLayout()
        
        self.alltime_bar_chart = BarChartWidget()
        alltime_layout.addWidget(QLabel("Balkendiagramm - Gesamtzeit"))
        alltime_layout.addWidget(self.alltime_bar_chart)
        
        self.alltime_pie_chart = PieChartWidget()
        alltime_layout.addWidget(QLabel("Kreisdiagramm - Gesamtzeit"))
        alltime_layout.addWidget(self.alltime_pie_chart)
        
        alltime_widget.setLayout(alltime_layout)
        self.tabs.addTab(alltime_widget, "Gesamtzeit")
        
        # Tab 3: Heatmap
        heatmap_widget = QWidget()
        heatmap_layout = QVBoxLayout()
        
        self.heatmap = HeatmapWidget()
        heatmap_layout.addWidget(self.heatmap)
        heatmap_layout.addStretch()
        
        heatmap_widget.setLayout(heatmap_layout)
        self.tabs.addTab(heatmap_widget, "Stündliche Aktivität")
        
        # Tab 4: Detailtabellen
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        
        details_layout.addWidget(QLabel("Detaillierte Tabellen"))
        
        # Heute-Tabelle
        details_layout.addWidget(QLabel("Heute:"))
        self.today_table = QTableWidget()
        self.today_table.setColumnCount(2)
        self.today_table.setHorizontalHeaderLabels(["App", "Nutzungsdauer"])
        self.today_table.setMaximumHeight(150)
        details_layout.addWidget(self.today_table)
        
        # Gesamtzeit-Tabelle
        details_layout.addWidget(QLabel("Gesamtzeit:"))
        self.all_time_table = QTableWidget()
        self.all_time_table.setColumnCount(2)
        self.all_time_table.setHorizontalHeaderLabels(["App", "Gesamtnutzungsdauer"])
        self.all_time_table.setMaximumHeight(150)
        self.all_time_table.itemDoubleClicked.connect(self._on_app_double_clicked_all_time)
        details_layout.addWidget(self.all_time_table)
        
        # Erinnerungen-Tabelle
        details_layout.addWidget(QLabel("Erinnerungen:"))
        self.reminders_table = QTableWidget()
        self.reminders_table.setColumnCount(3)
        self.reminders_table.setHorizontalHeaderLabels(["Uhrzeit", "Titel", "Nachricht"])
        self.reminders_table.setMaximumHeight(150)
        details_layout.addWidget(self.reminders_table)
        
        details_widget.setLayout(details_layout)
        self.tabs.addTab(details_widget, "Tabellen")
        
        layout.addWidget(self.tabs)
    
    def _refresh_statistics(self):
        """Aktualisiert die Statistiken."""
        # App-Nutzung heute
        if self.enabled_visualizations.get("table_today", True):
            daily_stats = self.main_window.usage_tracker.get_daily_stats()
            sorted_apps = sorted(daily_stats.items(), key=lambda x: x[1], reverse=True)
            
            # Diagramme aktualisieren
            today_dict = dict(sorted_apps)
            self.today_bar_chart.set_data(today_dict, "Top Apps - Heute")
            self.today_pie_chart.set_data(today_dict, "App-Verteilung - Heute")
            
            # Tabelle aktualisieren
            self.today_table.setRowCount(len(sorted_apps))
            for row, (app_name, minutes) in enumerate(sorted_apps):
                app_item = QTableWidgetItem(app_name)
                app_item.setForeground(QBrush(QColor(255, 255, 255)))  # Weiße Schrift
                self.today_table.setItem(row, 0, app_item)
                
                item = QTableWidgetItem(format_minutes(minutes))
                self._color_item_by_usage(item, minutes)
                self.today_table.setItem(row, 1, item)
        
        # Erinnerungen heute
        if self.enabled_visualizations.get("table_reminders", True):
            reminders = self.main_window.storage_manager.get_reminders_today()
            self.reminders_table.setRowCount(len(reminders))
            
            for row, reminder in enumerate(reminders):
                time_str = reminder.triggered_at.strftime("%H:%M:%S")
                time_item = QTableWidgetItem(time_str)
                time_item.setForeground(QBrush(QColor(255, 255, 255)))  # Weiße Schrift
                self.reminders_table.setItem(row, 0, time_item)
                
                title_item = QTableWidgetItem(reminder.title)
                title_item.setForeground(QBrush(QColor(255, 255, 255)))  # Weiße Schrift
                self.reminders_table.setItem(row, 1, title_item)
                
                msg_item = QTableWidgetItem(reminder.message)
                msg_item.setForeground(QBrush(QColor(255, 255, 255)))  # Weiße Schrift
                self.reminders_table.setItem(row, 2, msg_item)
        
        # Gesamtnutzungszeiten über alle Sessions
        if self.enabled_visualizations.get("table_all_time", True):
            all_time_stats = self.main_window.storage_manager.get_all_time_stats()
            sorted_all_time = sorted(all_time_stats.items(), key=lambda x: x[1], reverse=True)
            
            # Diagramme aktualisieren
            alltime_dict = dict(sorted_all_time)
            self.alltime_bar_chart.set_data(alltime_dict, "Top Apps - Gesamtzeit")
            self.alltime_pie_chart.set_data(alltime_dict, "App-Verteilung - Gesamtzeit")
            
            # Heatmap mit simulierten Daten
            hourly_data = self._generate_hourly_data(all_time_stats)
            self.heatmap.set_data(hourly_data)
            
            # Tabelle aktualisieren
            self.all_time_table.setRowCount(len(sorted_all_time))
            for row, (app_name, minutes) in enumerate(sorted_all_time):
                app_item = QTableWidgetItem(app_name)
                app_item.setForeground(QBrush(QColor(255, 255, 255)))  # Weiße Schrift
                self.all_time_table.setItem(row, 0, app_item)
                
                item = QTableWidgetItem(format_minutes(minutes))
                self._color_item_by_usage(item, minutes)
                self.all_time_table.setItem(row, 1, item)
    
    def _generate_hourly_data(self, stats: dict) -> dict:
        """Generiert stündliche Daten aus Gesamtstatistiken (Simulation)."""
        hourly_data = {}
        
        # Simuliere Verteilung über 24 Stunden mit Peak um 14:00
        for app_name, total_minutes in stats.items():
            for hour in range(24):
                # Gaußsche Kurve um 14:00 mit relativ breiter Verteilung
                import math
                factor = math.exp(-((hour - 14) ** 2) / 25)
                hour_minutes = total_minutes * factor / 4  # Normalisierung
                hourly_data[(hour, app_name)] = max(0, hour_minutes)
        
        return hourly_data
    
    def _color_item_by_usage(self, item, minutes):
        """Färbt ein Item basierend auf der Nutzungsdauer (als Heatmap)."""
        # Setze Hintergrundfarbe und passende Textfarbe
        if minutes < 5:
            item.setBackground(QBrush(QColor(200, 255, 200)))  # Hellgrün
            item.setForeground(QBrush(QColor(0, 0, 0)))  # Schwarze Schrift
        elif minutes < 30:
            item.setBackground(QBrush(QColor(255, 255, 150)))  # Hellgelb
            item.setForeground(QBrush(QColor(0, 0, 0)))  # Schwarze Schrift
        elif minutes < 120:
            item.setBackground(QBrush(QColor(255, 200, 100)))  # Orange
            item.setForeground(QBrush(QColor(0, 0, 0)))  # Schwarze Schrift
        else:
            item.setBackground(QBrush(QColor(255, 120, 120)))  # Rot
            item.setForeground(QBrush(QColor(255, 255, 255)))  # Weiße Schrift für hohe Werte
    
    def _on_app_double_clicked_all_time(self, item):
        """Handler: Öffnet Rule-Editor Dialog beim Double-Click auf eine App im Gesamtnutzungs-Tab."""
        from app.gui.rules_manager import RuleEditorDialog
        from app.models import Rule, RuleCondition, RuleAction
        
        # Hole App-Name aus der ersten Spalte
        row = item.row()
        app_item = self.all_time_table.item(row, 0)
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
    
    def _open_visualization_settings(self):
        """Öffnet den Dialog zur Visualisierungskonfiguration."""
        dialog = VisualizationSettingsDialog(self, self.enabled_visualizations)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.enabled_visualizations = dialog.get_settings()
            self._refresh_statistics()
    
    def _on_data_updated(self, app_name: str, process_name: str, usage_minutes: float):
        """Slot: Wird aufgerufen wenn new Daten verfügbar sind."""
        self._refresh_statistics()
    
    def refresh(self):
        """Aktualisiert die Anzeige."""
        self._refresh_statistics()


class VisualizationSettingsDialog(QDialog):
    """Dialog zur Konfiguration von Visualisierungen."""
    
    def __init__(self, parent=None, enabled_visualizations=None):
        """Initialisiert den Dialog."""
        super().__init__(parent)
        self.setWindowTitle("Visualisierungen konfigurieren")
        self.setGeometry(200, 200, 400, 300)
        
        self.enabled_visualizations = enabled_visualizations or {}
        self.checkboxes = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Richtet die UI ein."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Scroll-Area für Checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        group = QGroupBox("Verfügbare Statistiken")
        group_layout = QVBoxLayout()
        
        visualizations = [
            ("table_today", "Tabelle - Heute"),
            ("table_reminders", "Tabelle - Erinnerungen heute"),
            ("table_all_time", "Tabelle - Gesamtzeit"),
        ]
        
        for key, label in visualizations:
            checkbox = CustomCheckBox(label)
            checkbox.setChecked(self.enabled_visualizations.get(key, True))
            self.checkboxes[key] = checkbox
            group_layout.addWidget(checkbox)
        
        group_layout.addStretch()
        group.setLayout(group_layout)
        scroll.setWidget(group)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_settings(self):
        """Gibt die ausgewählten Einstellungen zurück."""
        return {key: checkbox.isChecked() for key, checkbox in self.checkboxes.items()}
