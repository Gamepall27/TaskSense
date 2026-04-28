"""Statistik-Widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog,
    QPushButton, QMessageBox, QScrollArea, QGroupBox, QLabel, QHBoxLayout,
    QFrame, QGraphicsBlurEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QFont

from app.utils import format_minutes, create_usage_preview_rows, create_reminder_preview_rows
from app.gui.charts import BarChartWidget, PieChartWidget, HeatmapWidget
from app.gui.custom_widgets import CustomCheckBox


class StatisticsWidget(QWidget):
    """Widget für Statistiken und Auswertungen."""

    def __init__(self, main_window):
        """Initialisiert das Statistik-Widget."""
        super().__init__()
        self.main_window = main_window
        self.preview_mode = self.main_window.product.statistics_preview_locked
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
        """Richtet die UI ein mit modernem Design."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Statistiken & Analysen")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.settings_btn = QPushButton("Visualisierungen anpasssen")
        self.settings_btn.setMinimumWidth(200)
        self.settings_btn.clicked.connect(self._open_visualization_settings)
        button_layout.addWidget(self.settings_btn)

        self.reset_btn = QPushButton("🔄 Statistik zurücksetzen")
        self.reset_btn.setMinimumWidth(200)
        self.reset_btn.setObjectName("dangerButton")
        self.reset_btn.clicked.connect(self._reset_all_time_stats)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)
        layout.addSpacing(10)

        self.tabs = QTabWidget()

        today_widget = QWidget()
        today_layout = QVBoxLayout()
        today_layout.setSpacing(15)
        today_layout.setContentsMargins(10, 10, 10, 10)

        self.today_bar_chart = BarChartWidget()
        today_layout.addWidget(QLabel("Balkendiagramm - Heute"))
        today_layout.addWidget(self.today_bar_chart)

        self.today_pie_chart = PieChartWidget()
        today_layout.addWidget(QLabel("Kreisdiagramm - Heute"))
        today_layout.addWidget(self.today_pie_chart)

        today_widget.setLayout(today_layout)
        self.tabs.addTab(today_widget, "Heute")

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

        heatmap_widget = QWidget()
        heatmap_layout = QVBoxLayout()

        self.heatmap = HeatmapWidget()
        heatmap_layout.addWidget(self.heatmap)
        heatmap_layout.addStretch()

        heatmap_widget.setLayout(heatmap_layout)
        self.tabs.addTab(heatmap_widget, "Stündliche Aktivität")

        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel("Detaillierte Tabellen"))

        details_layout.addWidget(QLabel("Heute:"))
        self.today_table = QTableWidget()
        self.today_table.setColumnCount(2)
        self.today_table.setHorizontalHeaderLabels(["App", "Nutzungsdauer"])
        details_layout.addWidget(self.today_table)

        details_layout.addWidget(QLabel("Gesamtzeit:"))
        self.all_time_table = QTableWidget()
        self.all_time_table.setColumnCount(2)
        self.all_time_table.setHorizontalHeaderLabels(["App", "Gesamtnutzungsdauer"])
        self.all_time_table.itemDoubleClicked.connect(self._on_app_double_clicked_all_time)
        details_layout.addWidget(self.all_time_table)

        details_layout.addWidget(QLabel("Erinnerungen:"))
        self.reminders_table = QTableWidget()
        self.reminders_table.setColumnCount(3)
        self.reminders_table.setHorizontalHeaderLabels(["Uhrzeit", "Titel", "Nachricht"])
        details_layout.addWidget(self.reminders_table)

        details_layout.addStretch()
        details_widget.setLayout(details_layout)
        self.tabs.addTab(details_widget, "Tabellen")

        layout.addWidget(self.tabs)
        layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        if self.preview_mode:
            self._setup_preview_overlay()

    def _setup_preview_overlay(self):
        """Aktiviert die Lite-Vorschau mit Blur und Hinweis-Overlay."""
        blur_effect = QGraphicsBlurEffect(self.tabs)
        blur_effect.setBlurRadius(8)
        self.tabs.setGraphicsEffect(blur_effect)
        self.tabs.setEnabled(False)
        self.settings_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)

        self.preview_overlay = QFrame(self)
        self.preview_overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(248, 249, 250, 220);
                border: 1px solid rgba(107, 114, 128, 90);
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
                color: #1F2937;
            }
        """)

        overlay_layout = QVBoxLayout(self.preview_overlay)
        overlay_layout.setContentsMargins(28, 28, 28, 28)
        overlay_layout.setSpacing(10)
        overlay_layout.addStretch()

        title_label = QLabel("Statistik-Vorschau")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(title_label)

        message_label = QLabel(self.main_window.product.stats_preview_message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(message_label)
        overlay_layout.addStretch()

        self._position_preview_overlay()

    def _refresh_statistics(self):
        """Aktualisiert die Statistiken."""
        if self.enabled_visualizations.get("table_today", True):
            daily_stats = self.main_window.usage_tracker.get_daily_stats()
            if self.preview_mode:
                preview_rows = create_usage_preview_rows(daily_stats, max_rows=5)
                today_dict = {name: value for name, value, _ in preview_rows}
                table_rows = [(name, display_text, value) for name, value, display_text in preview_rows]
            else:
                sorted_apps = sorted(daily_stats.items(), key=lambda item: item[1], reverse=True)
                today_dict = dict(sorted_apps)
                table_rows = [
                    (app_name, format_minutes(minutes), minutes)
                    for app_name, minutes in sorted_apps
                ]

            self.today_bar_chart.set_data(today_dict, "Top Apps - Heute")
            self.today_pie_chart.set_data(today_dict, "App-Verteilung - Heute")

            self.today_table.setRowCount(len(table_rows))
            for row, (app_name, time_text, minutes) in enumerate(table_rows):
                app_item = QTableWidgetItem(app_name)
                app_item.setForeground(QBrush(QColor(255, 255, 255)))
                self.today_table.setItem(row, 0, app_item)

                item = QTableWidgetItem(time_text)
                self._color_item_by_usage(item, minutes)
                self.today_table.setItem(row, 1, item)

        if self.enabled_visualizations.get("table_reminders", True):
            reminders = self.main_window.storage_manager.get_reminders_today()
            reminder_rows = create_reminder_preview_rows(reminders) if self.preview_mode else reminders
            self.reminders_table.setRowCount(len(reminder_rows))

            for row, reminder in enumerate(reminder_rows):
                if self.preview_mode:
                    time_str, title_text, message_text = reminder
                else:
                    time_str = reminder.triggered_at.strftime("%H:%M:%S")
                    title_text = reminder.title
                    message_text = reminder.message

                time_item = QTableWidgetItem(time_str)
                time_item.setForeground(QBrush(QColor(255, 255, 255)))
                self.reminders_table.setItem(row, 0, time_item)

                title_item = QTableWidgetItem(title_text)
                title_item.setForeground(QBrush(QColor(255, 255, 255)))
                self.reminders_table.setItem(row, 1, title_item)

                msg_item = QTableWidgetItem(message_text)
                msg_item.setForeground(QBrush(QColor(255, 255, 255)))
                self.reminders_table.setItem(row, 2, msg_item)

        if self.enabled_visualizations.get("table_all_time", True):
            all_time_stats = self.main_window.storage_manager.get_all_time_stats()
            if self.preview_mode:
                preview_rows = create_usage_preview_rows(all_time_stats, max_rows=8)
                alltime_dict = {name: value for name, value, _ in preview_rows}
                table_rows = [(name, display_text, value) for name, value, display_text in preview_rows]
            else:
                sorted_all_time = sorted(all_time_stats.items(), key=lambda item: item[1], reverse=True)
                alltime_dict = dict(sorted_all_time)
                table_rows = [
                    (app_name, format_minutes(minutes), minutes)
                    for app_name, minutes in sorted_all_time
                ]

            self.alltime_bar_chart.set_data(alltime_dict, "Top Apps - Gesamtzeit")
            self.alltime_pie_chart.set_data(alltime_dict, "App-Verteilung - Gesamtzeit")

            hourly_data = self._generate_hourly_data(alltime_dict)
            self.heatmap.set_data(hourly_data)

            self.all_time_table.setRowCount(len(table_rows))
            for row, (app_name, display_text, minutes) in enumerate(table_rows):
                app_item = QTableWidgetItem(app_name)
                app_item.setForeground(QBrush(QColor(255, 255, 255)))
                self.all_time_table.setItem(row, 0, app_item)

                item = QTableWidgetItem(display_text)
                self._color_item_by_usage(item, minutes)
                self.all_time_table.setItem(row, 1, item)

    def _generate_hourly_data(self, stats: dict) -> dict:
        """Generiert stündliche Daten aus Gesamtstatistiken (Simulation)."""
        hourly_data = {}

        for app_name, total_minutes in stats.items():
            for hour in range(24):
                import math

                factor = math.exp(-((hour - 14) ** 2) / 25)
                hour_minutes = total_minutes * factor / 4
                hourly_data[(hour, app_name)] = max(0, hour_minutes)

        return hourly_data

    def _color_item_by_usage(self, item, minutes):
        """Färbt ein Item basierend auf der Nutzungsdauer."""
        if minutes < 5:
            item.setBackground(QBrush(QColor(200, 255, 200)))
            item.setForeground(QBrush(QColor(0, 0, 0)))
        elif minutes < 30:
            item.setBackground(QBrush(QColor(255, 255, 150)))
            item.setForeground(QBrush(QColor(0, 0, 0)))
        elif minutes < 120:
            item.setBackground(QBrush(QColor(255, 200, 100)))
            item.setForeground(QBrush(QColor(0, 0, 0)))
        else:
            item.setBackground(QBrush(QColor(255, 120, 120)))
            item.setForeground(QBrush(QColor(255, 255, 255)))

    def _on_app_double_clicked_all_time(self, item):
        """Öffnet Rule-Editor Dialog beim Double-Click auf eine App."""
        from app.gui.rules_manager import RuleEditorDialog
        from app.models import Rule, RuleCondition, RuleAction

        if self.preview_mode:
            self.main_window.show_pro_upgrade_dialog(
                "Statistiken entsperren",
                "App-Namen aus der Statistik lassen sich erst in TaskSense Pro direkt als Regeln übernehmen.",
            )
            return

        if not self.main_window.can_create_rule():
            return

        row = item.row()
        app_item = self.all_time_table.item(row, 0)
        if not app_item:
            return

        app_name = app_item.text()
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

        dialog = RuleEditorDialog(new_rule, self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.main_window.save_rule(rule)

    def _open_visualization_settings(self):
        """Öffnet den Dialog zur Visualisierungskonfiguration."""
        if self.preview_mode:
            self.main_window.show_pro_upgrade_dialog(
                "Visualisierungen gesperrt",
                "Die detaillierte Statistik-Konfiguration ist nur in TaskSense Pro verfügbar.",
            )
            return

        dialog = VisualizationSettingsDialog(self, self.enabled_visualizations)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.enabled_visualizations = dialog.get_settings()
            self._refresh_statistics()

    def _reset_all_time_stats(self):
        """Setzt alle Gesamtstatistiken mit Bestätigungsabfrage zurück."""
        if self.preview_mode:
            self.main_window.show_pro_upgrade_dialog(
                "Statistiken zurücksetzen",
                "Das Zurücksetzen vollständiger Statistiken ist nur in TaskSense Pro verfügbar.",
            )
            return

        reply = QMessageBox.warning(
            self,
            "Gesamtstatistik zurücksetzen",
            "Wirklich alle Gesamtstatistiken zurücksetzen?\n\n"
            "Dies kann nicht rückgängig gemacht werden!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.storage_manager.reset_all_time_stats()
            self._refresh_statistics()
            QMessageBox.information(
                self,
                "Erfolg",
                "Alle Gesamtstatistiken wurden zurückgesetzt."
            )

    def _on_data_updated(self, app_name: str, process_name: str, usage_minutes: float):
        """Slot: Wird aufgerufen wenn neue Daten verfügbar sind."""
        self._refresh_statistics()

    def _position_preview_overlay(self):
        """Positioniert das Vorschau-Overlay passend zur Widgetgröße."""
        if not getattr(self, "preview_overlay", None):
            return

        margin = 24
        top_offset = 88
        width = max(self.width() - (margin * 2), 0)
        height = max(self.height() - top_offset - margin, 0)
        self.preview_overlay.setGeometry(margin, top_offset, width, height)
        self.preview_overlay.raise_()

    def resizeEvent(self, event):
        """Aktualisiert Overlay-Position bei Größenänderungen."""
        super().resizeEvent(event)
        self._position_preview_overlay()

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
