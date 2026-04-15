"""Einstellungs-Widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSpinBox, QComboBox, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

from app.models import Settings
from app.gui.custom_widgets import CustomCheckBox


class SettingsWidget(QWidget):
    """Widget fur Einstellungen."""
    
    def __init__(self, main_window):
        """Initialisiert das Einstellungs-Widget."""
        super().__init__()
        self.main_window = main_window
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Richtet die UI ein."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Tracking-Bereich
        tracking_group = QGroupBox("Tracking-Einstellungen")
        tracking_layout = QVBoxLayout()
        
        tracking_layout.addWidget(QLabel("Tracking-Intervall (Sekunden):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(30)
        self.interval_spin.setValue(2)
        tracking_layout.addWidget(self.interval_spin)
        
        tracking_group.setLayout(tracking_layout)
        layout.addWidget(tracking_group)
        
        # Benachrichtigungen
        notification_group = QGroupBox("Benachrichtigungen")
        notification_layout = QVBoxLayout()
        
        self.notifications_check = CustomCheckBox("Benachrichtigungen aktiviert")
        self.notifications_check.setChecked(True)
        notification_layout.addWidget(self.notifications_check)
        
        notification_group.setLayout(notification_layout)
        layout.addWidget(notification_group)
        
        # Interface
        ui_group = QGroupBox("Oberflache")
        ui_layout = QVBoxLayout()
        
        ui_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        ui_layout.addWidget(self.theme_combo)
        
        self.start_minimized_check = CustomCheckBox("Mit Windows minimiert starten")
        ui_layout.addWidget(self.start_minimized_check)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Datenverwaltung
        data_group = QGroupBox("Datenverwaltung")
        data_layout = QVBoxLayout()
        
        clear_btn = QPushButton("Alle Daten zurücksetzen")
        clear_btn.clicked.connect(self._clear_all_data)
        data_layout.addWidget(clear_btn)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        layout.addStretch()
        
        # Save-Button
        save_btn = QPushButton("Einstellungen speichern")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
    
    def _load_settings(self):
        """Ladet die Einstellungen in die UI."""
        settings = self.main_window.settings
        
        self.interval_spin.setValue(settings.tracking_interval_seconds)
        self.notifications_check.setChecked(settings.notifications_enabled)
        self.theme_combo.setCurrentText(settings.theme.capitalize())
        self.start_minimized_check.setChecked(settings.start_minimized)
    
    def _save_settings(self):
        """Speichert die Einstellungen."""
        settings = Settings(
            tracking_interval_seconds=self.interval_spin.value(),
            notifications_enabled=self.notifications_check.isChecked(),
            theme=self.theme_combo.currentText().lower(),
            start_minimized=self.start_minimized_check.isChecked(),
        )
        
        self.main_window.save_settings(settings)
        
        # Wende Theme an
        self.main_window.apply_theme(settings.theme)
        
        QMessageBox.information(
            self,
            "Erfolg",
            "Einstellungen gespeichert!"
        )
    
    def _clear_all_data(self):
        """Loscht alle Daten."""
        reply = QMessageBox.question(
            self,
            "Daten löschen?",
            "Möchten Sie wirklich ALLE Daten zurücksetzen?\n"
            "Dies kann nicht rückgängig gemacht werden!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Losche Regeln
            self.main_window.rules.clear()
            self.main_window.storage_manager.save_rules([])
            
            QMessageBox.information(
                self,
                "Erfolg",
                "Alle Daten wurden zurückgesetzt"
            )
