"""Diagramm- und Visualisierungs-Widgets ohne externe Abhängigkeiten."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt, QRect


class BarChartWidget(QWidget):
    """Ein einfaches Balkendiagramm-Widget."""
    
    def __init__(self, parent=None):
        """Initialisiert das Widget."""
        super().__init__(parent)
        self.data = {}
        self.title = "Balkendiagramm"
        self.setMinimumHeight(250)
        # Kein hardcodiertes Stylesheet - nutze Theme vom Parent
    
    def set_data(self, data: dict, title: str = ""):
        """Setzt die Daten für das Diagramm."""
        self.data = data
        if title:
            self.title = title
        self.update()
    
    def paintEvent(self, event):
        """Malt das Balkendiagramm."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        margin = 40
        
        # Hintergrund (weiß - wird überschrieben wenn Dark-Mode)
        bg_color = self.palette().color(self.backgroundRole())
        painter.fillRect(self.rect(), bg_color)
        
        if not self.data:
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(width // 2 - 100, height // 2, "Keine Daten verfügbar")
            return
        
        # Titel - Theme-aware (dunkler Hintergrund im Darkmode, heller im Lightmode)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        # Erkenne Theme basierend auf Hintergrundfarbe
        bg_brightness = bg_color.lightness()
        is_dark_mode = bg_brightness < 128
        
        # Title styling
        title_rect = QRect(margin, 10, width - 2 * margin, 25)
        if is_dark_mode:
            title_bg = QColor(70, 70, 70)  # Dunkelgrau im Darkmode
            title_text = QColor(255, 255, 255)  # Weiß im Darkmode
        else:
            title_bg = QColor(240, 240, 240)  # Hellgrau im Lightmode
            title_text = QColor(0, 0, 0)  # Schwarz im Lightmode
        
        painter.fillRect(title_rect, title_bg)
        painter.setPen(title_text)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter, self.title)
        
        # Berechne max Wert
        max_val = max(self.data.values()) if self.data else 1
        if max_val == 0:
            max_val = 1
        
        # Zeichne Balken
        items = list(self.data.items())[:10]  # Limitiere auf 10 Einträge
        bar_width = (width - 2 * margin) // max(len(items), 1)
        chart_height = height - 2 * margin - 20
        
        colors = [
            QColor(52, 168, 219),   # Blau
            QColor(46, 204, 113),   # Grün
            QColor(241, 196, 15),   # Orange
            QColor(231, 76, 60),    # Rot
            QColor(155, 89, 182),   # Violett
            QColor(52, 73, 94),     # Dunkelblau
        ]
        
        for i, (label, value) in enumerate(items):
            x = int(margin + i * bar_width + 5)
            bar_height = int((value / max_val) * chart_height)
            y = int(height - margin - bar_height)
            
            # Zeichne Balken
            color = colors[i % len(colors)]
            painter.fillRect(QRect(x, y, int(bar_width - 10), bar_height), color)
            
            # Zeichne Label (schwarzer Text mit weißem Hintergrund)
            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)
            painter.setPen(QColor(0, 0, 0))  # Schwarze Schrift
            label_rect = QRect(x, height - margin + 15, int(bar_width - 10), 20)
            painter.fillRect(label_rect, QColor(255, 255, 255))  # Weißer Hintergrund
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label[:15])
            
            # Zeichne Wert (schwarze Schrift mit weißem Hintergrund)
            value_rect = QRect(x, y - 15, int(bar_width - 10), 20)
            painter.fillRect(value_rect, QColor(255, 255, 255))  # Weißer Hintergrund
            painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, f"{value:.0f}m")
        
        # Zeichne Achsen (in grau)
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawLine(margin, height - margin, width - margin, height - margin)  # X-Achse
        painter.drawLine(margin, margin, margin, height - margin)  # Y-Achse


class PieChartWidget(QWidget):
    """Ein einfaches Kreisdiagramm-Widget."""
    
    def __init__(self, parent=None):
        """Initialisiert das Widget."""
        super().__init__(parent)
        self.data = {}
        self.title = "Kreisdiagramm"
        self.setMinimumHeight(250)
        # Kein hardcodiertes Stylesheet - nutze Theme vom Parent
    
    def set_data(self, data: dict, title: str = ""):
        """Setzt die Daten für das Diagramm."""
        self.data = data
        if title:
            self.title = title
        self.update()
    
    def paintEvent(self, event):
        """Malt das Kreisdiagramm."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        margin = 40
        
        # Hintergrund
        bg_color = self.palette().color(self.backgroundRole())
        painter.fillRect(self.rect(), bg_color)
        
        if not self.data:
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(width // 2 - 100, height // 2, "Keine Daten verfügbar")
            return
        
        # Titel - Theme-aware
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        bg_brightness = bg_color.lightness()
        is_dark_mode = bg_brightness < 128
        
        title_rect = QRect(margin, 10, width - 2 * margin, 25)
        if is_dark_mode:
            title_bg = QColor(70, 70, 70)
            title_text = QColor(255, 255, 255)
        else:
            title_bg = QColor(240, 240, 240)
            title_text = QColor(0, 0, 0)
        
        painter.fillRect(title_rect, title_bg)
        painter.setPen(title_text)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter, self.title)
        
        # Berechne Gesamtsumme
        total = sum(self.data.values())
        if total == 0:
            painter.drawText(width // 2 - 50, height // 2, "Keine Daten")
            return
        
        # Zeichne Kreissegmente
        center_x = width // 2
        center_y = (height + margin) // 2
        radius = min((width - 2 * margin) // 2, (height - 2 * margin) // 2) - 20
        
        colors = [
            QColor(52, 168, 219),
            QColor(46, 204, 113),
            QColor(241, 196, 15),
            QColor(231, 76, 60),
            QColor(155, 89, 182),
            QColor(52, 73, 94),
        ]
        
        start_angle = 0
        for i, (label, value) in enumerate(list(self.data.items())[:6]):
            angle = (value / total) * 360
            color = colors[i % len(colors)]
            
            painter.setBrush(QBrush(color))
            painter.setPen(QColor(255, 255, 255))
            painter.drawPie(center_x - radius, center_y - radius, radius * 2, radius * 2,
                           int(start_angle * 16), int(angle * 16))
            
            # Zeichne Label (schwarze Schrift mit weißem Hintergrund)
            label_angle = start_angle + angle / 2
            import math
            label_x = center_x + (radius + 30) * math.cos(math.radians(label_angle - 90))
            label_y = center_y + (radius + 30) * math.sin(math.radians(label_angle - 90))
            
            font = QFont()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(0, 0, 0))  # Schwarze Schrift
            percentage = (value / total) * 100
            label_rect = QRect(int(label_x) - 30, int(label_y), 60, 20)
            painter.fillRect(label_rect, QColor(255, 255, 255))  # Weißer Hintergrund
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, f"{percentage:.0f}%")
            
            start_angle += angle


class HeatmapWidget(QWidget):
    """Ein einfaches Heatmap-Widget für stündliche Daten."""
    
    def __init__(self, parent=None):
        """Initialisiert das Widget."""
        super().__init__(parent)
        self.data = {}  # (hour, app) -> value
        self.setMinimumHeight(200)
        # Kein hardcodiertes Stylesheet - nutze Theme vom Parent
    
    def set_data(self, data: dict):
        """Setzt die Daten für die Heatmap."""
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        """Malt die Heatmap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        margin = 40
        
        # Hintergrund (weiß - wird überschrieben wenn Dark-Mode)
        bg_color = self.palette().color(self.backgroundRole())
        painter.fillRect(self.rect(), bg_color)
        
        text_color = self.palette().color(self.foregroundRole())
        
        if not self.data:
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(width // 2 - 100, height // 2, "Keine Daten verfügbar")
            return
        
        # Titel - Theme-aware
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        bg_brightness = bg_color.lightness()
        is_dark_mode = bg_brightness < 128
        
        title_rect = QRect(margin, 10, width - 2 * margin, 25)
        if is_dark_mode:
            title_bg = QColor(70, 70, 70)
            title_text = QColor(255, 255, 255)
        else:
            title_bg = QColor(240, 240, 240)
            title_text = QColor(0, 0, 0)
        
        painter.fillRect(title_rect, title_bg)
        painter.setPen(title_text)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter, "Stündliche Aktivität")
        
        # Berechne max Wert
        max_val = max(self.data.values()) if self.data else 1
        if max_val == 0:
            max_val = 1
        
        # Zeichne Stundenspalten
        cell_width = (width - 2 * margin) / 24
        cell_height = height - 2 * margin - 20
        
        for hour in range(24):
            x = margin + hour * cell_width
            
            # Berechne durchschnittlichen Wert für diese Stunde
            hour_values = [v for (h, a), v in self.data.items() if h == hour]
            hour_avg = sum(hour_values) / len(hour_values) if hour_values else 0
            
            # Farbe basierend auf Wert (blau bis rot spektrum)
            intensity = hour_avg / max_val if max_val > 0 else 0
            
            if intensity < 0.3:
                color = QColor(200, 220, 255)  # Hellblau
            elif intensity < 0.6:
                color = QColor(100, 150, 255)  # Blau
            elif intensity < 0.8:
                color = QColor(255, 200, 100)  # Orange
            else:
                color = QColor(255, 100, 100)  # Rot
            
            painter.fillRect(QRect(int(x), int(margin + 20), int(cell_width) - 1, int(cell_height)), color)
            
            # Zeichne Stundenlabel (schwarze Schrift mit weißem Hintergrund)
            font = QFont()
            font.setPointSize(7)
            painter.setFont(font)
            painter.setPen(QColor(0, 0, 0))  # Schwarze Schrift
            label_rect = QRect(int(x), height - margin + 5, int(cell_width), 15)
            painter.fillRect(label_rect, QColor(255, 255, 255, 200))  # Semi-transparenter weißer Hintergrund
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, f"{hour:02d}:00")
        
        # Legende (schwarzer Text)
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(margin, height - 15, "Blau = Wenig  |  Rot = Viel Aktivität")
