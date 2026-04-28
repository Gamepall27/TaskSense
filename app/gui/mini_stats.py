"""Mini-Fenster für schnelle Statistik-Anzeige."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QScrollArea, QPushButton, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtGui import QColor, QBrush, QFont

from app.utils import format_minutes, create_usage_preview_rows


class MiniStatsWindow(QWidget):
    """Mini-Fenster für Statistiken."""
    
    def __init__(self, main_window):
        """Initialisiert das Mini-Statistik-Fenster."""
        super().__init__()
        self.main_window = main_window
        self.preview_mode = self.main_window.product.statistics_preview_locked
        self.setWindowTitle(f"{self.main_window.product.display_name} - Statistiken")
        self.resize(400, 350)
        self.setFixedSize(400, 350)
        
        # Frameless Tool Window verhindert Verschieben über die Titelleiste.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        self._setup_ui()
        
        # Auto-Aktualisierung alle 2 Sekunden
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._refresh_stats)
        self.update_timer.start(2000)

    def _move_to_bottom_right(self):
        """Positioniert das Fenster unten rechts im verfügbaren Bildschirmbereich."""
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return

        available = screen.availableGeometry()
        margin = 12
        x = available.right() - self.width() - margin
        y = available.bottom() - self.height() - margin
        self.move(x, y)
    
    def _setup_ui(self):
        """Richtet die UI mit modernem Design ein."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Titel
        title = QLabel("Statistiken")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Separator Line
        sep = QLabel("")
        sep.setMaximumHeight(1)
        sep.setStyleSheet("background-color: #384856;")
        layout.addWidget(sep)
        
        # Heute-Label
        today_label = QLabel("Heute" if not self.preview_mode else "Heute (Vorschau)")
        today_label_font = QFont()
        today_label_font.setPointSize(10)
        today_label_font.setBold(True)
        today_label.setFont(today_label_font)
        layout.addWidget(today_label)
        
        # Heute-Tabelle
        self.today_table = QTableWidget()
        self.today_table.setColumnCount(2)
        self.today_table.setHorizontalHeaderLabels(["App", "Zeit"])
        self.today_table.setMaximumHeight(110)
        self.today_table.setRowCount(0)
        self.today_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.today_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.today_table.setAlternatingRowColors(True)
        layout.addWidget(self.today_table)
        
        # Gesamtzeit-Label
        layout.addSpacing(5)
        alltime_label = QLabel("Gesamtzeit (Top 3)" if not self.preview_mode else "Gesamtzeit (Vorschau)")
        alltime_label_font = QFont()
        alltime_label_font.setPointSize(10)
        alltime_label_font.setBold(True)
        alltime_label.setFont(alltime_label_font)
        layout.addWidget(alltime_label)
        
        # Gesamtzeit-Tabelle
        self.alltime_table = QTableWidget()
        self.alltime_table.setColumnCount(2)
        self.alltime_table.setHorizontalHeaderLabels(["App", "Zeit"])
        self.alltime_table.setMaximumHeight(80)
        self.alltime_table.setRowCount(0)
        self.alltime_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.alltime_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.alltime_table.setAlternatingRowColors(True)
        layout.addWidget(self.alltime_table)
        
        layout.addSpacing(5)
        
        # Button-Leiste
        button_layout = QHBoxLayout()
        
        open_btn = QPushButton("📂 Öffnen")
        open_btn.setMinimumWidth(80)
        open_btn.clicked.connect(self._open_full_window)
        button_layout.addWidget(open_btn)
        
        close_btn = QPushButton("❌ Schließen")
        close_btn.setMinimumWidth(80)
        close_btn.clicked.connect(self.hide)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _refresh_stats(self):
        """Aktualisiert die Statistiken."""
        # Heute
        daily_stats = self.main_window.usage_tracker.get_daily_stats()
        if self.preview_mode:
            sorted_today = create_usage_preview_rows(daily_stats, max_rows=5)
        else:
            sorted_today = sorted(daily_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        self.today_table.setRowCount(len(sorted_today))
        for row, entry in enumerate(sorted_today):
            if self.preview_mode:
                app_name, minutes, time_text = entry
            else:
                app_name, minutes = entry
                time_text = format_minutes(minutes)

            app_item = QTableWidgetItem(app_name)
            app_item.setForeground(QBrush(QColor(255, 255, 255)))
            self.today_table.setItem(row, 0, app_item)
            
            time_item = QTableWidgetItem(time_text)
            time_item.setForeground(QBrush(QColor(255, 255, 255)))
            self.today_table.setItem(row, 1, time_item)
        
        # Gesamtzeit
        alltime_stats = self.main_window.storage_manager.get_all_time_stats()
        if self.preview_mode:
            sorted_alltime = create_usage_preview_rows(alltime_stats, max_rows=3)
        else:
            sorted_alltime = sorted(alltime_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        
        self.alltime_table.setRowCount(len(sorted_alltime))
        for row, entry in enumerate(sorted_alltime):
            if self.preview_mode:
                app_name, minutes, time_text = entry
            else:
                app_name, minutes = entry
                time_text = format_minutes(minutes)

            app_item = QTableWidgetItem(app_name)
            app_item.setForeground(QBrush(QColor(255, 255, 255)))
            self.alltime_table.setItem(row, 0, app_item)
            
            time_item = QTableWidgetItem(time_text)
            time_item.setForeground(QBrush(QColor(255, 255, 255)))
            self.alltime_table.setItem(row, 1, time_item)
    
    def _open_full_window(self):
        """Öffnet das Hauptfenster."""
        self.main_window.showNormal()
        self.main_window.activateWindow()
        self.main_window.tabs.setCurrentIndex(2)  # Statistiken-Tab
        self.hide()
    
    def showEvent(self, event):
        """Wird aufgerufen wenn Fenster sichtbar wird."""
        super().showEvent(event)
        self._move_to_bottom_right()
        self._refresh_stats()
    
    def closeEvent(self, event):
        """Wird aufgerufen wenn Fenster geschlossen wird."""
        self.update_timer.stop()
        super().closeEvent(event)
