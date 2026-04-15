"""Logging-Hilfsfunktionen für SmartCue."""
import logging
import os
from datetime import datetime


def setup_logging(log_dir: str = "data", log_level: str = "INFO") -> logging.Logger:
    """
    Setzt Logging auf.
    
    Args:
        log_dir: Verzeichnis für Log-Dateien
        log_level: Logging Level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger-Instanz
    """
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger("SmartCue")
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    log_file = os.path.join(log_dir, f"smartcue_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Nur Warnungen in Konsole
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info("Logging initialized")
    
    return logger


def get_logger() -> logging.Logger:
    """Gibt die Logger-Instanz für SmartCue zurück."""
    return logging.getLogger("SmartCue")
