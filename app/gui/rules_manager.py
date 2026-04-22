"""Regelverwaltungs-Widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLabel, QLineEdit, QComboBox,
    QSpinBox, QCheckBox, QMessageBox, QDialogButtonBox, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt

from app.models import Rule, RuleCondition, RuleAction
from app.gui.custom_widgets import CustomCheckBox


class RulesManagerWidget(QWidget):
    """Widget zur Verwaltung von Regeln."""
    
    def __init__(self, main_window):
        """Initialisiert the Regelverwaltung."""
        super().__init__()
        self.main_window = main_window
        
        self._setup_ui()
        self.refresh_list()
    
    def _setup_ui(self):
        """Richtet die UI mit modernem Design ein."""
        # Hauptlayout mit ScrollArea
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Content Widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Titel
        title_label = QLabel("Regeln verwalten")
        title_font = self.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Button-Leiste (links ausgerichtet)
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Neue Regel")
        add_btn.setMinimumWidth(120)
        add_btn.clicked.connect(self._add_rule)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️  Bearbeiten")
        edit_btn.setMinimumWidth(120)
        edit_btn.clicked.connect(self._edit_rule)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️  Löschen")
        delete_btn.setMinimumWidth(120)
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self._delete_rule)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Tabelle
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels([
            "Name", "Bedingung", "Cooldown (min)", "Enabled", "Aktion"
        ])
        self.rules_table.resizeColumnsToContents()
        # Verbinde Double-Click zum Bearbeiten
        self.rules_table.itemDoubleClicked.connect(self._on_rule_double_clicked)
        layout.addWidget(self.rules_table)
        
        # ScrollArea zusammensetzen
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def refresh_list(self):
        """Aktualisiert die Regelliste."""
        self.rules_table.setRowCount(len(self.main_window.rules))
        
        for row, rule in enumerate(self.main_window.rules):
            # Name
            name_item = QTableWidgetItem(rule.name)
            self.rules_table.setItem(row, 0, name_item)
            
            # Bedingung
            condition_text = self._format_conditions(rule.conditions)
            cond_item = QTableWidgetItem(condition_text)
            self.rules_table.setItem(row, 1, cond_item)
            
            # Cooldown
            cooldown_item = QTableWidgetItem(str(rule.cooldown_minutes))
            self.rules_table.setItem(row, 2, cooldown_item)
            
            # Enabled
            enabled_text = "Ja" if rule.enabled else "Nein"
            enabled_item = QTableWidgetItem(enabled_text)
            self.rules_table.setItem(row, 3, enabled_item)
            
            # Aktion
            action_text = self._format_actions(rule.actions)
            action_item = QTableWidgetItem(action_text)
            self.rules_table.setItem(row, 4, action_item)
    
    def _format_conditions(self, conditions) -> str:
        """Formatiert Bedingungen fur Anzeige."""
        if not conditions:
            return ""
        
        parts = []
        for cond in conditions:
            parts.append(f"{cond.condition_type}: {cond.value}")
        
        return " UND ".join(parts[:2])  # Max 2 anzeigen
    
    def _format_actions(self, actions) -> str:
        """Formatiert Aktionen fur Anzeige."""
        if not actions:
            return ""
        
        return actions[0].title[:30]  # Erste 30 Zeichen des Titels
    
    def _add_rule(self):
        """Öffnet Dialog zum Hinzufügen einer Regel."""
        from app.models import Rule
        new_rule = Rule()
        dialog = RuleEditorDialog(new_rule, self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.main_window.save_rule(rule)
    
    def _edit_rule(self):
        """Öffnet Dialog zum Bearbeiten einer Regel."""
        row = self.rules_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie eine Regel")
            return
        
        rule = self.main_window.rules[row]
        dialog = RuleEditorDialog(rule, self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_rule = dialog.get_rule()
            self.main_window.save_rule(updated_rule)
    
    def _delete_rule(self):
        """Löscht eine Regel."""
        row = self.rules_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie eine Regel")
            return
        
        rule = self.main_window.rules[row]
        reply = QMessageBox.question(
            self,
            "Löschen?",
            f"Möchten Sie die Regel '{rule.name}' wirklich löschen?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.delete_rule(rule.rule_id)
    
    def _on_rule_double_clicked(self, item):
        """Öffnet Bearbeitungs-Dialog beim Double-Click auf eine Regel."""
        row = item.row()
        if row < 0 or row >= len(self.main_window.rules):
            return
        
        rule = self.main_window.rules[row]
        dialog = RuleEditorDialog(rule, self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_rule = dialog.get_rule()
            self.main_window.save_rule(updated_rule)


class RuleEditorDialog(QDialog):
    """Dialog zum Editieren einer Regel."""
    
    # Mapping für verständlichere Bedingungsbeschreibungen
    CONDITION_TYPES = {
        "app_is": "App ist genau",
        "app_contains": "App enthält",
        "app_not": "App ist nicht",
        "usage_time_greater": "Nutzungsdauer über (Minuten)",
        "time_after": "Nach Uhrzeit (HH:MM)",
        "time_before": "Vor Uhrzeit (HH:MM)",
        "weekday": "Am Wochentag",
    }
    
    # Reverse mapping für speichern
    CONDITION_TYPES_REVERSE = {v: k for k, v in CONDITION_TYPES.items()}
    
    def __init__(self, rule=None, main_window=None):
        """Initialisiert den RuleEditorDialog."""
        super().__init__()
        from app.models import Rule
        self.rule = rule if rule is not None else Rule()
        self.main_window = main_window
        
        self.setWindowTitle("Regel bearbeiten" if rule and rule.rule_id else "Neue Regel")
        self.setGeometry(200, 200, 500, 800)
        
        self._setup_ui()
        self._load_rule_data()
    
    def _setup_ui(self):
        """Richtet die UI ein."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Name
        layout.addWidget(QLabel("Regelname:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Bedingung
        layout.addWidget(QLabel("Bedingung:"))
        self.condition_type_combo = QComboBox()
        self.condition_type_combo.addItems(self.CONDITION_TYPES.values())
        layout.addWidget(self.condition_type_combo)
        
        layout.addWidget(QLabel("Bedingungswert:"))
        self.condition_value_input = QLineEdit()
        layout.addWidget(self.condition_value_input)
        
        # Aktion
        layout.addWidget(QLabel("Notifikations-Titel:"))
        self.action_title_input = QLineEdit()
        layout.addWidget(self.action_title_input)
        
        layout.addWidget(QLabel("Notifikations-Text:"))
        self.action_message_input = QLineEdit()
        layout.addWidget(self.action_message_input)
        
        # Cooldown
        layout.addWidget(QLabel("Cooldown (Minuten):"))
        self.cooldown_spin = QSpinBox()
        self.cooldown_spin.setMinimum(1)
        self.cooldown_spin.setMaximum(1440)
        self.cooldown_spin.setValue(15)
        layout.addWidget(self.cooldown_spin)
        
        # Wiederholungsmuster
        layout.addWidget(QLabel("Wiederholung:"))
        self.recurring_combo = QComboBox()
        self.recurring_combo.addItems(["Einmalig", "Täglich", "Wöchentlich", "Bestimmte Wochentage"])
        self.recurring_combo.currentTextChanged.connect(self._on_recurring_changed)
        layout.addWidget(self.recurring_combo)
        
        # Wochentags-Auswahl (nur sichtbar bei "Bestimmte Wochentage")
        self.weekdays_group = QGroupBox("Wochentage auswählen")
        weekdays_layout = QVBoxLayout()
        self.weekday_checks = {}
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        for i, day in enumerate(weekdays):
            check = CustomCheckBox(day)
            self.weekday_checks[i] = check
            weekdays_layout.addWidget(check)
        self.weekdays_group.setLayout(weekdays_layout)
        self.weekdays_group.setVisible(False)
        layout.addWidget(self.weekdays_group)
        
        # Enabled
        self.enabled_check = CustomCheckBox("Regel aktiviert")
        self.enabled_check.setChecked(True)
        layout.addWidget(self.enabled_check)
        
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_recurring_changed(self, text: str):
        """Zeigt/versteckt die Wochentags-Auswahl basierend auf dem Wiederholungsmuster."""
        self.weekdays_group.setVisible(text == "Bestimmte Wochentage")
    
    def _load_rule_data(self):
        """Ladet die Daten der Regel in die UI."""
        self.name_input.setText(self.rule.name)
        
        if self.rule.conditions:
            cond = self.rule.conditions[0]
            # Konvertiere den technischen Namen zum Anzeigenamen
            display_text = self.CONDITION_TYPES.get(cond.condition_type, cond.condition_type)
            self.condition_type_combo.setCurrentText(display_text)
            self.condition_value_input.setText(cond.value)
        
        if self.rule.actions:
            action = self.rule.actions[0]
            self.action_title_input.setText(action.title)
            self.action_message_input.setText(action.message)
        
        self.cooldown_spin.setValue(self.rule.cooldown_minutes)
        self.enabled_check.setChecked(self.rule.enabled)
        
        # Lade Recurring-Muster
        recurring_map = {"once": "Einmalig", "daily": "Täglich", "weekly": "Wöchentlich", "weekly_specific": "Bestimmte Wochentage"}
        self.recurring_combo.setCurrentText(recurring_map.get(self.rule.recurring_pattern, "Einmalig"))
        
        # Lade Wochentage
        for i, check in self.weekday_checks.items():
            check.setChecked(i in self.rule.recurring_weekdays)
    
    def get_rule(self) -> Rule:
        """Gibt die bearbeitete Regel zurück."""
        self.rule.name = self.name_input.text()
        self.rule.cooldown_minutes = self.cooldown_spin.value()
        self.rule.enabled = self.enabled_check.isChecked()
        
        # Bedingung - konvertiere Anzeigenamen zurück zu technischem Namen
        display_text = self.condition_type_combo.currentText()
        technical_name = self.CONDITION_TYPES_REVERSE.get(display_text, display_text)
        
        condition = RuleCondition(
            condition_type=technical_name,
            value=self.condition_value_input.text(),
        )
        self.rule.conditions = [condition]
        
        # Aktion
        action = RuleAction(
            title=self.action_title_input.text(),
            message=self.action_message_input.text(),
        )
        self.rule.actions = [action]
        
        # Recurring-Muster
        recurring_map = {"Einmalig": "once", "Täglich": "daily", "Wöchentlich": "weekly", "Bestimmte Wochentage": "weekly_specific"}
        self.rule.recurring_pattern = recurring_map.get(self.recurring_combo.currentText(), "once")
        
        # Wochentage
        self.rule.recurring_weekdays = [i for i, check in self.weekday_checks.items() if check.isChecked()]
        
        return self.rule
