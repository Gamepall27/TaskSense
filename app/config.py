"""Beispiel-Konfiguration für TaskSense."""

EXAMPLE_RULES = [
    {
        "name": "Chrome Pause-Erinnerung",
        "condition_type": "usage_time_greater",
        "condition_value": "120",
        "action_title": "Pause einlegen!",
        "action_message": "Du hast Chrome bereits 120 Minuten genutzt. Nimm dir eine kurze Pause!",
        "cooldown_minutes": 15,
    },
    {
        "name": "Spät-Worker Alert",
        "condition_type": "time_after",
        "condition_value": "22:00",
        "action_title": "Feierabend?",
        "action_message": "Es ist 22 Uhr. Solltest du nicht langsam Feierabend machen?",
        "cooldown_minutes": 60,
    },
    {
        "name": "VS Code Git-Commit Reminder",
        "condition_type": "app_is",
        "condition_value": "VS Code",
        "action_title": "Git Commit nicht vergessen",
        "action_message": "Denke daran, deine Änderungen zu committen!",
        "cooldown_minutes": 30,
    },
    {
        "name": "Arbeitsstart",
        "condition_type": "time_after",
        "condition_value": "09:00",
        "action_title": "Guten Morgen!",
        "action_message": "Die Arbeitszeit hat begonnen. Viel Erfolg heute!",
        "cooldown_minutes": 1440,  # 24h Cooldown
    },
]
