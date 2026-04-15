"""Utility-Funktionen und Helper."""
from datetime import datetime
import json


def get_today_date_str() -> str:
    """Gibt das heutige Datum als String zurück (YYYY-MM-DD)."""
    return datetime.now().date().isoformat()


def format_minutes(minutes: float) -> str:
    """Formatiert Minuten in ein lesbares Format mit Sekunden."""
    # Konvertiere Minuten in Sekunden
    total_seconds = int(minutes * 60)
    
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    mins = remaining_seconds // 60
    secs = remaining_seconds % 60
    
    # Formatiere je nach Größe
    if hours > 0:
        if mins > 0:
            return f"{hours}h {mins}m {secs}s"
        else:
            return f"{hours}h {secs}s"
    elif mins > 0:
        return f"{mins}m {secs}s"
    else:
        return f"{secs}s"


def format_time(dt: datetime) -> str:
    """Formatiert ein Datetime-Objekt in ein lesbares Format."""
    return dt.strftime("%H:%M:%S")


def format_datetime(dt: datetime) -> str:
    """Formatiert ein Datetime-Objekt mit Datum und Zeit."""
    return dt.strftime("%d.%m.%Y %H:%M:%S")


def safe_json_write(file_path: str, data: dict):
    """Sichert ein Dict in JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Schreiben von {file_path}: {e}")


def safe_json_read(file_path: str) -> dict:
    """Liest JSON-Datei sicher."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Lesen von {file_path}: {e}")
        return {}
