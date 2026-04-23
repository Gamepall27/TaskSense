"""Windows-spezifische Funktionen zum Trackengon des aktiven Fensters."""
import ctypes
from ctypes import wintypes
from typing import Tuple, Optional
import psutil


class WindowTracker:
    """Trackt das aktuelle aktive Fenster unter Windows."""
    
    # Windows API Konstanten
    WM_GETTEXT = 13
    
    def __init__(self):
        """Initialisiert den WindowTracker."""
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def get_active_window(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Gibt den aktuell aktiven Prozess und Fenstertitel zurück.
        
        Returns:
            Tuple[app_name, process_name, window_title]
            - app_name: Vereinfachter Name (z.B. 'Chrome', 'VS Code')
            - process_name: Exakter Prozessname (z.B. 'chrome.exe')
            - window_title: Fenstertitel
        """
        try:
            # Hole Fenster-Handle
            hwnd = self.user32.GetForegroundWindow()
            if hwnd == 0:
                return None, None, None
            
            # Hole Prozess-ID vom Fenster
            pid = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Hole Prozessinformationen
            try:
                process = psutil.Process(pid.value)
                process_name = process.name()
                app_name = self._extract_app_name(process_name)
                
                # Hole Fenstertitel
                window_title = self._get_window_title(hwnd)
                
                return app_name, process_name, window_title
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None, None, None
                
        except Exception as e:
            print(f"Fehler beim Auslesen des aktiven Fensters: {e}")
            return None, None, None

    def get_active_window_info(self) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[int]]:
        """
        Gibt die aktive App inklusive Fenster-Handle zurück.

        Returns:
            Tuple[app_name, process_name, window_title, hwnd]
        """
        try:
            hwnd = self.user32.GetForegroundWindow()
            if hwnd == 0:
                return None, None, None, None

            pid = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            try:
                process = psutil.Process(pid.value)
                process_name = process.name()
                app_name = self._extract_app_name(process_name)
                window_title = self._get_window_title(hwnd)
                return app_name, process_name, window_title, int(hwnd)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None, None, None, None

        except Exception as e:
            print(f"Fehler beim Auslesen des aktiven Fensters: {e}")
            return None, None, None, None

    def is_window_valid(self, hwnd: Optional[int]) -> bool:
        """Prüft, ob ein Fenster-Handle noch gültig ist."""
        if not hwnd:
            return False

        try:
            return bool(self.user32.IsWindow(hwnd))
        except Exception:
            return False
    
    def _extract_app_name(self, process_name: str) -> str:
        """
        Extrahiert einen vereinfachten App-Namen aus dem Prozessnamen.
        
        Args:
            process_name: Prozessname (z.B. 'chrome.exe')
            
        Returns:
            Vereinfachter Name (z.B. 'Chrome')
        """
        if not process_name:
            return "Unknown"
        
        # Entferne .exe
        name = process_name.replace('.exe', '').replace('.app', '')
        
        # Normalisiere bekannte App-Namen
        name_lower = name.lower()
        
        app_mappings = {
            'chrome': 'Chrome',
            'firefox': 'Firefox',
            'msedge': 'Edge',
            'code': 'VS Code',
            'excel': 'Excel',
            'winword': 'Word',
            'powerpnt': 'PowerPoint',
            'outlook': 'Outlook',
            'slack': 'Slack',
            'teams': 'Teams',
            'zoom': 'Zoom',
            'vlc': 'VLC',
            'spotify': 'Spotify',
            'discord': 'Discord',
            'telegram': 'Telegram',
            'notion': 'Notion',
        }
        
        for key, display_name in app_mappings.items():
            if key in name_lower:
                return display_name
        
        return name.title()
    
    def _get_window_title(self, hwnd: int) -> str:
        """Hole den Fenstertitel."""
        try:
            length = self.user32.GetWindowTextLength(hwnd)
            if length == 0:
                return ""
            
            buf = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value
        except Exception:
            return ""
    
    def get_active_monitor_info(self) -> dict:
        """
        Gibt kurze Informationen über den aktuellen Status zurück.
        
        Returns:
            Dict mit aktuellen Informationen
        """
        app_name, process_name, window_title = self.get_active_window()
        
        return {
            'app_name': app_name,
            'process_name': process_name,
            'window_title': window_title,
            'timestamp': None,
        }
