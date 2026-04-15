"""GUI-Module Init"""
from .main_window import MainWindow
from .dashboard import DashboardWidget
from .rules_manager import RulesManagerWidget
from .statistics import StatisticsWidget
from .settings import SettingsWidget

__all__ = [
    'MainWindow',
    'DashboardWidget',
    'RulesManagerWidget',
    'StatisticsWidget',
    'SettingsWidget',
]
