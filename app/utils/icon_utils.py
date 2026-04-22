"""Utilities für Icon-Erstellung."""
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont
from PyQt6.QtCore import Qt


def create_app_icon(size: int = 32) -> QIcon:
    """
    Erstellt ein einfaches App-Icon mit dem Text 'TS' (TaskSense).
    
    Args:
        size: Icon-Größe in Pixeln
        
    Returns:
        QIcon Objekt
    """
    # Erstelle Pixmap mit blauem Hintergrund
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(66, 133, 244))  # Google Blue
    
    # Zeichne Text auf Pixmap
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Schreibe "SC" in Weiß
    font = QFont("Arial", size // 2 - 2)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255))  # Weiße Schrift
    
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "SC")
    painter.end()
    
    return QIcon(pixmap)


def create_tray_icons() -> dict:
    """
    Erstellt verschiedene Icon-Größen für Tray und Fenster.
    
    Returns:
        Dictionary mit Icons verschiedener Größen
    """
    return {
        '16': create_app_icon(16),
        '32': create_app_icon(32),
        '64': create_app_icon(64),
    }
