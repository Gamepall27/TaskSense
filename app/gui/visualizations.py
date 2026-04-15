"""Visualisierungen für Statistiken."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime


class ChartWidget(QWidget):
    """Basis-Widget für Diagramme."""
    
    def __init__(self):
        """Initialisiert das Chart-Widget."""
        super().__init__()
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)


class BarChartWidget(ChartWidget):
    """Balkendiagramm für App-Nutzungszeiten."""
    
    def __init__(self):
        """Initialisiert das Balkendiagramm."""
        super().__init__()
        self.data = {}
    
    def update_data(self, data: dict, title: str = ""):
        """
        Aktualisiert die Daten und zeichnet das Diagramm neu.
        
        Args:
            data: Dict mit app_name -> minutes
            title: Titel des Diagramms
        """
        self.data = data
        self._redraw(title)
    
    def _redraw(self, title: str = ""):
        """Zeichnet das Diagramm neu."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not self.data:
            ax.text(0.5, 0.5, "Keine Daten vorhanden", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return
        
        # Sortiere nach Wert absteigend
        apps = list(self.data.keys())
        minutes = list(self.data.values())
        
        # Begrenzen auf Top 10
        if len(apps) > 10:
            apps = apps[:10]
            minutes = minutes[:10]
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(apps)))
        bars = ax.bar(apps, minutes, color=colors)
        
        ax.set_ylabel("Minuten", fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        
        # Werte auf Balken anzeigen
        for bar, minute in zip(bars, minutes):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{minute:.0f}m',
                   ha='center', va='bottom', fontsize=9)
        
        self.figure.tight_layout()
        self.canvas.draw()


class HeatmapWidget(ChartWidget):
    """Wochentags-Heatmap der App-Nutzung."""
    
    def __init__(self):
        """Initialisiert die Heatmap."""
        super().__init__()
    
    def update_data(self, hourly_data: dict):
        """
        Aktualisiert die Heatmap mit Stundendaten.
        
        Args:
            hourly_data: Dict mit (hour, app) -> minutes
        """
        self._redraw(hourly_data)
    
    def _redraw(self, hourly_data: dict):
        """Zeichnet die Heatmap neu."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not hourly_data:
            ax.text(0.5, 0.5, "Keine Stundendaten vorhanden", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return
        
        # Erstelle 24x1 Matrix für jede Stunde des Tages
        hours = np.zeros(24)
        for (hour, _), minutes in hourly_data.items():
            if 0 <= hour < 24:
                hours[hour] += minutes
        
        # Zeichne Heatmap
        heat_map = ax.imshow([hours], cmap='YlOrRd', aspect='auto', interpolation='nearest')
        ax.set_yticks([0])
        ax.set_yticklabels(['Heute'])
        ax.set_xticks(range(24))
        ax.set_xticklabels([f"{i:02d}:00" for i in range(24)])
        ax.tick_params(axis='x', rotation=45)
        
        # Colorbar hinzufügen
        self.figure.colorbar(heat_map, ax=ax, label='Minuten')
        
        ax.set_title("Aktivität pro Stunde", fontsize=12, fontweight='bold')
        self.figure.tight_layout()
        self.canvas.draw()


class PieChartWidget(ChartWidget):
    """Kreisdiagramm für App-Anteile."""
    
    def __init__(self):
        """Initialisiert das Kreisdiagramm."""
        super().__init__()
    
    def update_data(self, data: dict, title: str = ""):
        """
        Aktualisiert die Daten und zeichnet das Diagramm neu.
        
        Args:
            data: Dict mit app_name -> minutes
            title: Titel des Diagramms
        """
        self._redraw(data, title)
    
    def _redraw(self, data: dict, title: str = ""):
        """Zeichnet das Kreisdiagramm neu."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, "Keine Daten vorhanden", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return
        
        # Nimm Top 8 Apps, Rest als "Sonstige"
        apps = sorted(data.items(), key=lambda x: x[1], reverse=True)
        if len(apps) > 8:
            top_apps = apps[:7]
            other_minutes = sum(v for _, v in apps[7:])
            top_apps.append(("Sonstige", other_minutes))
            apps = top_apps
        
        labels = [app for app, _ in apps]
        sizes = [minutes for _, minutes in apps]
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            colors=colors, startangle=90)
        
        # Formatiere Text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        for text in texts:
            text.set_fontsize(10)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        self.figure.tight_layout()
        self.canvas.draw()


class TimelineWidget(ChartWidget):
    """Timeline-Diagramm für Tagesübersicht."""
    
    def __init__(self):
        """Initialisiert die Timeline."""
        super().__init__()
    
    def update_data(self, timeline_data: list):
        """
        Aktualisiert die Timeline.
        
        Args:
            timeline_data: Liste von (app_name, start_hour, end_hour, duration_minutes)
        """
        self._redraw(timeline_data)
    
    def _redraw(self, timeline_data: list):
        """Zeichnet die Timeline neu."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not timeline_data:
            ax.text(0.5, 0.5, "Keine Zeitleisten-Daten vorhanden", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return
        
        # Sortiere nach Startzeit
        sorted_data = sorted(timeline_data, key=lambda x: x[1])
        
        y_pos = 0
        colors = plt.cm.tab20(np.linspace(0, 1, len(sorted_data)))
        
        for (app_name, start_hour, duration_minutes, _), color in zip(sorted_data, colors):
            end_hour = start_hour + (duration_minutes / 60)
            
            # Zeichne Balken
            ax.barh(y_pos, duration_minutes/60, left=start_hour, height=0.8, 
                   label=app_name, color=color)
            
            y_pos += 1
        
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 2))
        ax.set_xticklabels([f"{i:02d}:00" for i in range(0, 25, 2)])
        ax.set_yticks(range(len(sorted_data)))
        ax.set_yticklabels([item[0][:15] for item in sorted_data])  # App-Namen, max 15 Zeichen
        
        ax.set_xlabel("Tageszeit", fontsize=10)
        ax.set_title("Tages-Timeline", fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
