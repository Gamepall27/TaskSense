"""Produkt- und Editionskonfiguration für TaskSense."""
from dataclasses import dataclass
import os
from typing import Optional


EDITION_ENV_VAR = "TASKSENSE_EDITION"
DEFAULT_EDITION = "pro"


@dataclass(frozen=True)
class ProductConfig:
    """Beschreibt eine baubare Produktedition."""

    edition: str
    display_name: str
    exe_name: str
    entry_script: str
    msix_base_name: str
    manifest_identity_name: str
    manifest_description: str
    max_rules: Optional[int]
    statistics_preview_locked: bool

    @property
    def is_pro(self) -> bool:
        """Gibt zurück, ob es sich um die Pro-Edition handelt."""
        return self.edition == "pro"

    @property
    def upgrade_product_name(self) -> str:
        """Name der kaufbaren Vollversion."""
        return "TaskSense Pro Lifetime"

    @property
    def upgrade_pitch(self) -> str:
        """Kurzer Upgrade-Hinweis für Lite."""
        return (
            f"{self.upgrade_product_name} schaltet unbegrenzte Regeln und "
            "vollständige Statistiken frei."
        )

    @property
    def rule_limit_banner(self) -> str:
        """Info-Text für das Regel-Limit in Lite."""
        if self.max_rules is None:
            return ""
        return (
            f"{self.display_name} enthält bis zu {self.max_rules} Regeln. "
            f"{self.upgrade_pitch}"
        )

    @property
    def stats_preview_message(self) -> str:
        """Overlay-Text für die Statistik-Vorschau."""
        return (
            "Sie sehen nur eine anonymisierte Vorschau. "
            f"{self.upgrade_pitch}"
        )


def resolve_edition(raw_value: Optional[str]) -> str:
    """Normalisiert die gewünschte Edition."""
    edition = (raw_value or DEFAULT_EDITION).strip().lower()
    return edition if edition in {"lite", "pro"} else DEFAULT_EDITION


def get_product_config(edition: Optional[str] = None) -> ProductConfig:
    """Gibt die Produktkonfiguration für die Edition zurück."""
    resolved = resolve_edition(edition or os.getenv(EDITION_ENV_VAR))

    if resolved == "lite":
        return ProductConfig(
            edition="lite",
            display_name="TaskSense Lite",
            exe_name="TaskSenseLite",
            entry_script="main_lite.py",
            msix_base_name="TaskSense-Lite",
            manifest_identity_name="Orphelia.TaskSenseLite",
            manifest_description=(
                "Kostenlose Vorschau auf das intelligente Reminder- und Fokus-Tool"
            ),
            max_rules=3,
            statistics_preview_locked=True,
        )

    return ProductConfig(
        edition="pro",
        display_name="TaskSense Pro",
        exe_name="TaskSensePro",
        entry_script="main_pro.py",
        msix_base_name="TaskSense-Pro",
        manifest_identity_name="Orphelia.TaskSensePro",
        manifest_description="Intelligentes Windows Reminder- und Fokus-Tool",
        max_rules=None,
        statistics_preview_locked=False,
    )


PRODUCT = get_product_config()
