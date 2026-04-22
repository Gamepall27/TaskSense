"""Gemeinsame Build-Helfer für Editionen und MSIX-Metadaten."""
import re
from pathlib import Path

from app.product import ProductConfig, get_product_config


def read_version_from_manifest(project_root: Path) -> str:
    """Liest die Version aus dem AppxManifest.xml."""
    manifest_path = project_root / "AppxManifest.xml"

    if not manifest_path.exists():
        return "1.0.0"

    try:
        content = manifest_path.read_text(encoding="utf-8")
        match = re.search(r'Version="([^"]+)"', content)
        if match:
            version = match.group(1)
            if version.endswith(".0") and version.count(".") == 3:
                version = version[:-2]
            return version
    except Exception:
        pass

    return "1.0.0"


def normalize_manifest_version(version: str) -> str:
    """Konvertiert Versionsnummern in das Windows-Format X.X.X.X."""
    if version.count(".") == 2:
        return f"{version}.0"
    return version


def get_product(edition: str) -> ProductConfig:
    """Gibt die Produktkonfiguration für Build-Skripte zurück."""
    return get_product_config(edition)


def get_msix_filename(product: ProductConfig, version: str) -> str:
    """Erzeugt den MSIX-Dateinamen inkl. Version."""
    return f"{product.msix_base_name}-{version}.msix"


def customize_manifest_content(content: str, product: ProductConfig, version: str) -> str:
    """Passt Manifest für Edition, Namen und Version an."""
    manifest_version = normalize_manifest_version(version)

    replacements = [
        (r'(<Identity[^>]*Name=")[^"]*(")', rf"\g<1>{product.manifest_identity_name}\2"),
        (r'(<Identity[^>]*Version=")[^"]*(")', rf"\g<1>{manifest_version}\2"),
        (r'(<DisplayName>).*?(</DisplayName>)', rf"\g<1>{product.display_name}\2"),
        (
            r'(<Application[^>]*Executable=")[^"]*(")',
            rf"\g<1>{product.exe_name}.exe\2",
        ),
        (
            r'(<uap:VisualElements[^>]*DisplayName=")[^"]*(")',
            rf"\g<1>{product.display_name}\2",
        ),
        (
            r'(<uap:VisualElements[^>]*Description=")[^"]*(")',
            rf"\g<1>{product.manifest_description}\2",
        ),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

    return content
