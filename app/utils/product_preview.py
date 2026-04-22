"""Hilfsfunktionen für anonymisierte Lite-Vorschauen."""
from typing import Dict, List, Tuple


def obfuscate_usage_minutes(minutes: float) -> Tuple[str, float]:
    """Ordnet Nutzungszeit groben Vorschau-Buckets zu."""
    if minutes < 15:
        return "unter 15 min", 10.0
    if minutes < 45:
        return "ca. 15-45 min", 30.0
    if minutes < 120:
        return "ca. 45-120 min", 75.0
    if minutes < 240:
        return "ca. 2-4 h", 180.0
    return "4 h+", 300.0


def create_usage_preview_rows(
    stats: Dict[str, float],
    max_rows: int = 5,
) -> List[Tuple[str, float, str]]:
    """Erstellt anonymisierte Zeilen für Statistik-Vorschauen."""
    sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)[:max_rows]
    rows = []

    for index, (_, minutes) in enumerate(sorted_stats, start=1):
        display_text, preview_value = obfuscate_usage_minutes(minutes)
        rows.append((f"App {index}", preview_value, display_text))

    return rows


def create_reminder_preview_rows(reminders: list, max_rows: int = 6) -> List[Tuple[str, str, str]]:
    """Erstellt anonymisierte Reminder-Zeilen für Lite."""
    rows = []

    for reminder in reminders[:max_rows]:
        rounded_hour = (reminder.triggered_at.hour // 2) * 2
        rows.append(
            (
                f"~{rounded_hour:02d}:00",
                "In Pro sichtbar",
                "Titel und Nachricht sind nur in TaskSense Pro sichtbar.",
            )
        )

    return rows
