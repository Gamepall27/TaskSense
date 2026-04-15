"""Service für Windows-Benachrichtigungen."""
import os
import sys
import subprocess
import threading
import ctypes
from typing import Optional, Callable


class NotificationService:
    """Zeigt Benachrichtigungen unter Windows an."""
    
    def __init__(self):
        """Initialisiert den NotificationService."""
        self.enabled = True
        self._toaster = None
        self._try_import_toaster()
    
    def _try_import_toaster(self):
        """Versucht, den ToastNotifier zu importieren."""
        try:
            from win10toast import ToastNotifier
            self._toaster = ToastNotifier()
        except ImportError:
            self._toaster = None
            print("Warnung: win10toast nicht installiert. Verwende Alternative Methoden.")
    
    def show_notification(self, title: str, message: str, 
                         timeout_ms: int = 5000,
                         on_click_callback: Optional[Callable] = None) -> bool:
        """
        Zeigt eine Windows-Benachrichtigung an.
        
        Args:
            title: Titel der Benachrichtigung
            message: Nachrichtentext
            timeout_ms: Anzeigedauer in Millisekunden
            on_click_callback: Callback wenn auf Benachrichtigung geklickt wird
            
        Returns:
            True wenn erfolgreich angezeigt
        """
        if not self.enabled:
            return False
        
        try:
            # Methode 1: Versuche win10toast zu verwenden
            if self._toaster:
                try:
                    self._toaster.show_toast(
                        title,
                        message,
                        duration=max(1, timeout_ms // 1000),
                        threaded=True
                    )
                    return True
                except Exception as e:
                    print(f"win10toast fehlgeschlagen: {e}")
            
            # Methode 2: Zeige MessageBox (garantiert zu funktionieren)
            self._show_via_messagebox(title, message)
            return True
            
        except Exception as e:
            print(f"Fehler beim Anzeigen der Benachrichtigung: {e}")
            return False
    
    def _show_via_messagebox(self, title: str, message: str):
        """
        Zeigt eine Benachrichtigung via ctypes MessageBox (native Win32 API).
        Dies funktioniert auf allen Windows-Versionen.
        """
        try:
            # Starte in separatem Thread, um GUI nicht zu blockieren
            def show_msgbox():
                try:
                    # MB_OK = 0, MB_ICONINFORMATION = 64
                    MB_OK = 0
                    MB_ICONINFORMATION = 64
                    MB_SYSTEMMODAL = 4096
                    
                    ctypes.windll.user32.MessageBoxW(
                        None,
                        message,
                        title,
                        MB_OK | MB_ICONINFORMATION | MB_SYSTEMMODAL
                    )
                except Exception as e:
                    print(f"MessageBox fehlgeschlagen: {e}")
            
            thread = threading.Thread(target=show_msgbox, daemon=True)
            thread.start()
        except Exception as e:
            print(f"Fehler bei MessageBox: {e}")
            self._show_via_winsound(title, message)
    
    def _show_via_winsound(self, title: str, message: str):
        """
        Fallback-Methode mit Sound.
        """
        try:
            import winsound
            # Spiele einen Sound ab
            winsound.Beep(1000, 200)  # 1000 Hz, 200 ms
        except Exception:
            pass
    
    def set_enabled(self, enabled: bool):
        """Aktiviert oder deaktiviert Benachrichtigungen."""
        self.enabled = enabled
    
    def is_enabled(self) -> bool:
        """Gibt an, ob Benachrichtigungen aktiviert sind."""
        return self.enabled
