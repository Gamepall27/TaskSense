"""Benutzerdefinierte Widget-Komponenten."""
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QRect


class CustomCheckBox(QCheckBox):
    """Ein benutzerdefiniertes Checkbox-Widget mit sichtbarem Häkchen."""
    
    def __init__(self, text: str = "", parent=None):
        """Initialisiert das Custom Checkbox."""
        super().__init__(text, parent)
        self.setMinimumHeight(24)
    
    def paintEvent(self, event):
        """Zeichnet die Checkbox mit sichtbarem Häkchen."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Checkbox-Größe
        checkbox_size = 18
        margin = 3
        x = margin
        y = (self.height() - checkbox_size) // 2
        
        # Hole aktuellen Text-Color vom Palette
        text_color = self.palette().color(self.foregroundRole())
        is_dark = text_color.lightness() > 128
        
        if is_dark:
            bg_color = QColor("#3d3d3d")
            border_color = QColor("#555")
            check_color = QColor("#ffffff")
            hover_color = QColor("#0078d4")
        else:
            bg_color = QColor("#ffffff")
            border_color = QColor("#ddd")
            check_color = QColor("#000000")
            hover_color = QColor("#0078d4")
        
        # Zeichne Checkbox-Box
        checkbox_rect = QRect(x, y, checkbox_size, checkbox_size)
        
        if self.isChecked():
            painter.fillRect(checkbox_rect, hover_color)
            painter.setPen(QPen(hover_color, 2))
        else:
            painter.fillRect(checkbox_rect, bg_color)
            painter.setPen(QPen(border_color, 2))
        
        painter.drawRect(checkbox_rect)
        
        # Zeichne Häkchen wenn gecheckt
        if self.isChecked():
            painter.setPen(QPen(check_color, 2))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(checkbox_rect, Qt.AlignmentFlag.AlignCenter, "✓")
        
        # Zeichne Text
        text_rect = QRect(x + checkbox_size + 8, 0, self.width() - x - checkbox_size - 8, self.height())
        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self.text())
