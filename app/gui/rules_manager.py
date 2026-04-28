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

        self.limit_info_label = QLabel("")
        self.limit_info_label.setWordWrap(True)
        self.limit_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.limit_info_label.setVisible(not self.main_window.product.is_pro)
        layout.addWidget(self.limit_info_label)
        
        # Button-Leiste (links ausgerichtet)
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Neue Regel")
        self.add_btn.setMinimumWidth(120)
        self.add_btn.clicked.connect(self._add_rule)
        button_layout.addWidget(self.add_btn)
        
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

        self._refresh_limit_state()

    def _refresh_limit_state(self):
        """Aktualisiert Lite-Hinweise und Button-Status."""
        if self.main_window.product.is_pro:
            return

        max_rules = self.main_window.product.max_rules or 0
        current_count = len(self.main_window.rules)
        remaining = max(max_rules - current_count, 0)

        self.limit_info_label.setText(
            f"{current_count}/{max_rules} Regeln belegt. "
            f"Noch frei: {remaining}. {self.main_window.product.upgrade_pitch}"
        )
        self.add_btn.setEnabled(current_count < max_rules)
    
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
        if not self.main_window.can_create_rule():
            return
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

    CONDITION_TYPES = {
        "app_is": "App ist genau",
        "app_closed": "App wird geschlossen",
        "app_contains": "App enthält",
        "app_not": "App ist nicht",
        "usage_time_greater": "Nutzungsdauer über (Minuten)",
        "time_after": "Nach Uhrzeit (HH:MM)",
        "time_before": "Vor Uhrzeit (HH:MM)",
        "weekday": "Am Wochentag",
    }
    CONDITION_TYPES_REVERSE = {v: k for k, v in CONDITION_TYPES.items()}
    CUSTOM_VALUE_LABEL = "Eigene Eingabe"
    COMMON_APPS = [
        "Chrome",
        "Firefox",
        "Edge",
        "VS Code",
        "Excel",
        "Word",
        "PowerPoint",
        "Outlook",
        "Slack",
        "Teams",
        "Zoom",
        "VLC",
        "Spotify",
        "Discord",
        "Telegram",
        "Notion",
    ]
    WEEKDAY_OPTIONS = [
        ("Montag", "Monday"),
        ("Dienstag", "Tuesday"),
        ("Mittwoch", "Wednesday"),
        ("Donnerstag", "Thursday"),
        ("Freitag", "Friday"),
        ("Samstag", "Saturday"),
        ("Sonntag", "Sunday"),
    ]
    TIME_OPTIONS = ["06:00", "08:00", "09:00", "12:00", "17:00", "18:00", "20:00", "22:00", "23:00"]
    USAGE_TIME_OPTIONS = ["15", "30", "45", "60", "90", "120", "180", "240"]

    def __init__(self, rule=None, main_window=None):
        """Initialisiert den RuleEditorDialog."""
        super().__init__()
        from app.models import Rule
        self.rule = rule if rule is not None else Rule()
        self.main_window = main_window

        self.setWindowTitle("Regel bearbeiten" if rule and rule.rule_id else "Neue Regel")
        self.setGeometry(200, 200, 500, 800)

        self._setup_ui()
        self._on_condition_type_changed(self.condition_type_combo.currentText())
        self._load_rule_data()

    def _setup_ui(self):
        """Richtet die UI ein."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Regelname:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Bedingung:"))
        self.condition_type_combo = QComboBox()
        self.condition_type_combo.addItems(self.CONDITION_TYPES.values())
        self.condition_type_combo.currentTextChanged.connect(self._on_condition_type_changed)
        layout.addWidget(self.condition_type_combo)

        layout.addWidget(QLabel("Bedingungswert:"))
        self.condition_value_combo = QComboBox()
        self.condition_value_combo.currentTextChanged.connect(self._on_condition_value_changed)
        layout.addWidget(self.condition_value_combo)

        self.custom_value_label = QLabel("Eigener Wert:")
        self.custom_value_label.setVisible(False)
        layout.addWidget(self.custom_value_label)

        self.condition_value_input = QLineEdit()
        self.condition_value_input.setVisible(False)
        layout.addWidget(self.condition_value_input)

        layout.addWidget(QLabel("Notifikations-Titel:"))
        self.action_title_input = QLineEdit()
        layout.addWidget(self.action_title_input)

        layout.addWidget(QLabel("Notifikations-Text:"))
        self.action_message_input = QLineEdit()
        layout.addWidget(self.action_message_input)

        layout.addWidget(QLabel("Cooldown (Minuten):"))
        self.cooldown_spin = QSpinBox()
        self.cooldown_spin.setMinimum(1)
        self.cooldown_spin.setMaximum(1440)
        self.cooldown_spin.setValue(15)
        layout.addWidget(self.cooldown_spin)

        layout.addWidget(QLabel("Wiederholung:"))
        self.recurring_combo = QComboBox()
        self.recurring_combo.addItems(["Einmalig", "Täglich", "Wöchentlich", "Bestimmte Wochentage"])
        self.recurring_combo.currentTextChanged.connect(self._on_recurring_changed)
        layout.addWidget(self.recurring_combo)

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

        self.enabled_check = CustomCheckBox("Regel aktiviert")
        self.enabled_check.setChecked(True)
        layout.addWidget(self.enabled_check)

        layout.addStretch()

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

    def _on_condition_type_changed(self, display_text: str):
        """Aktualisiert Vorschlagswerte passend zum gewählten Bedingungstyp."""
        technical_name = self.CONDITION_TYPES_REVERSE.get(display_text, display_text)
        options = self._get_condition_value_options(technical_name)

        self.condition_value_combo.blockSignals(True)
        self.condition_value_combo.clear()
        for label, value in options:
            self.condition_value_combo.addItem(label, value)
        self.condition_value_combo.blockSignals(False)

        self.condition_value_input.clear()
        self._set_custom_value_visible(False)
        if self.condition_value_combo.count() > 0:
            self.condition_value_combo.setCurrentIndex(0)
        self._on_condition_value_changed(self.condition_value_combo.currentText())

    def _on_condition_value_changed(self, selected_text: str):
        """Blendet das Freitextfeld nur für eigene Werte ein."""
        selected_value = self.condition_value_combo.currentData()
        use_custom = selected_value is None or selected_text == self.CUSTOM_VALUE_LABEL
        self._set_custom_value_visible(use_custom)
        if use_custom:
            self.condition_value_input.setFocus()

    def _set_custom_value_visible(self, visible: bool):
        """Steuert die Sichtbarkeit des Freitextfelds."""
        self.custom_value_label.setVisible(visible)
        self.condition_value_input.setVisible(visible)

    def _get_condition_value_options(self, condition_type: str):
        """Liefert Vorschlagswerte für den gewählten Bedingungstyp."""
        if condition_type in {"app_is", "app_closed", "app_contains", "app_not"}:
            options = [(app_name, app_name) for app_name in self._get_app_suggestions()]
        elif condition_type == "weekday":
            options = self.WEEKDAY_OPTIONS[:]
        elif condition_type in {"time_after", "time_before"}:
            options = [(time_value, time_value) for time_value in self.TIME_OPTIONS]
        elif condition_type == "usage_time_greater":
            options = [(f"{minutes} Minuten", minutes) for minutes in self.USAGE_TIME_OPTIONS]
        else:
            options = []

        options.append((self.CUSTOM_VALUE_LABEL, None))
        return options

    def _get_app_suggestions(self):
        """Sammelt passende App-Vorschläge aus bekannten und lokalen Daten."""
        app_names = set(self.COMMON_APPS)

        try:
            app_names.update(self.main_window.usage_tracker.get_daily_stats().keys())
        except Exception:
            pass

        try:
            app_names.update(self.main_window.storage_manager.get_all_time_stats().keys())
        except Exception:
            pass

        for rule in getattr(self.main_window, "rules", []):
            for condition in rule.conditions:
                if condition.condition_type in {"app_is", "app_closed", "app_contains", "app_not"} and condition.value:
                    app_names.add(condition.value)

        return sorted(app_name for app_name in app_names if app_name)

    def _set_condition_value(self, condition_value: str):
        """Setzt den gespeicherten Regelwert in Dropdown oder Freitextfeld."""
        index = self.condition_value_combo.findData(condition_value)
        if index >= 0:
            self.condition_value_combo.setCurrentIndex(index)
            self.condition_value_input.clear()
            self._set_custom_value_visible(False)
            return

        custom_index = self.condition_value_combo.findText(self.CUSTOM_VALUE_LABEL)
        if custom_index >= 0:
            self.condition_value_combo.setCurrentIndex(custom_index)
        self.condition_value_input.setText(condition_value)
        self._set_custom_value_visible(True)

    def _get_selected_condition_value(self) -> str:
        """Liefert den finalen Regelwert aus Dropdown oder Freitext."""
        selected_value = self.condition_value_combo.currentData()
        if selected_value is None:
            return self.condition_value_input.text().strip()
        return str(selected_value).strip()

    def _load_rule_data(self):
        """Ladet die Daten der Regel in die UI."""
        self.name_input.setText(self.rule.name)

        if self.rule.conditions:
            cond = self.rule.conditions[0]
            display_text = self.CONDITION_TYPES.get(cond.condition_type, cond.condition_type)
            self.condition_type_combo.setCurrentText(display_text)
            self._set_condition_value(cond.value)

        if self.rule.actions:
            action = self.rule.actions[0]
            self.action_title_input.setText(action.title)
            self.action_message_input.setText(action.message)

        self.cooldown_spin.setValue(self.rule.cooldown_minutes)
        self.enabled_check.setChecked(self.rule.enabled)

        recurring_map = {"once": "Einmalig", "daily": "Täglich", "weekly": "Wöchentlich", "weekly_specific": "Bestimmte Wochentage"}
        self.recurring_combo.setCurrentText(recurring_map.get(self.rule.recurring_pattern, "Einmalig"))

        for i, check in self.weekday_checks.items():
            check.setChecked(i in self.rule.recurring_weekdays)

    def get_rule(self) -> Rule:
        """Gibt die bearbeitete Regel zurück."""
        self.rule.name = self.name_input.text()
        self.rule.cooldown_minutes = self.cooldown_spin.value()
        self.rule.enabled = self.enabled_check.isChecked()

        display_text = self.condition_type_combo.currentText()
        technical_name = self.CONDITION_TYPES_REVERSE.get(display_text, display_text)

        condition = RuleCondition(
            condition_type=technical_name,
            value=self._get_selected_condition_value(),
        )
        self.rule.conditions = [condition]

        action = RuleAction(
            title=self.action_title_input.text(),
            message=self.action_message_input.text(),
        )
        self.rule.actions = [action]

        recurring_map = {"Einmalig": "once", "Täglich": "daily", "Wöchentlich": "weekly", "Bestimmte Wochentage": "weekly_specific"}
        self.rule.recurring_pattern = recurring_map.get(self.recurring_combo.currentText(), "once")
        self.rule.recurring_weekdays = [i for i, check in self.weekday_checks.items() if check.isChecked()]

        return self.rule
