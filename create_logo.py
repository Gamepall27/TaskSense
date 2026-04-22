#!/usr/bin/env python3
"""
Logo Generator für TaskSense
Erstellt ein professionelles Logo für das Projekt in verschiedenen Größen.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_logo():
    """Erstellt das TaskSense Logo."""
    
    project_root = Path(__file__).parent
    assets_dir = project_root / "Assets"
    assets_dir.mkdir(exist_ok=True)
    
    print("🎨 Erstelle TaskSense Logo...\n")
    
    # Hauptlogo: Großes Design für SplashScreen
    create_splash_screen(assets_dir)
    
    # Verschiedene Icon-Größen
    icon_sizes = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
    }
    
    for filename, size in icon_sizes.items():
        create_icon(assets_dir, filename, size)
    
    print("\n✅ Alle Logo-Dateien erstellt!")
    print(f"📁 Speicherort: {assets_dir}/")
    

def create_splash_screen(assets_dir: Path):
    """Erstellt den SplashScreen (620x300)."""
    width, height = 620, 300
    
    # Erstelle Hintergrund mit Gradient (blau zu dunkelblau)
    img = Image.new('RGB', (width, height), color=(33, 150, 243))
    
    # Farbige Bereiche
    pixels = img.load()
    for y in range(height):
        # Gradient von oben nach unten
        ratio = y / height
        r = int(33 + (10 - 33) * ratio)
        g = int(150 + (100 - 150) * ratio)
        b = int(243 + (200 - 243) * ratio)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    # Zeichne Geometrische Formen
    draw = ImageDraw.Draw(img)
    
    # Weiße Kreis-Elemente links
    draw.ellipse([20, 50, 120, 150], fill=(255, 255, 255), outline=(200, 200, 200), width=2)
    draw.ellipse([70, 100, 150, 180], fill=(76, 175, 80), outline=(56, 155, 60), width=2)
    
    # "T" Symbol (Task-Tracking)
    draw.rectangle([180, 60, 220, 200], fill=(255, 255, 255), outline=(200, 200, 200), width=2)
    draw.rectangle([140, 60, 260, 100], fill=(76, 175, 80), outline=(56, 155, 60), width=2)
    
    # Text
    try:
        # Versuche eine größere Font zu laden
        title_font = ImageFont.truetype("arial.ttf", 48)
        subtitle_font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback auf default Font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Titel
    draw.text((280, 80), "TaskSense", fill=(255, 255, 255), font=title_font)
    
    # Untertitel
    draw.text((280, 150), "Focus & Tracking", fill=(200, 230, 255), font=subtitle_font)
    
    img.save(assets_dir / "SplashScreen.png")
    print("✓ SplashScreen erstellt: SplashScreen.png (620x300)")


def create_icon(assets_dir: Path, filename: str, size: tuple):
    """Erstellt ein Icon in der angegebenen Größe."""
    
    width, height = size
    
    # Erstelle Icon mit Gradient
    img = Image.new('RGB', (width, height), color=(33, 150, 243))
    
    # Farbige Gradient-Bereiche
    pixels = img.load()
    for y in range(height):
        ratio = y / height
        r = int(33 + (10 - 33) * ratio)
        g = int(150 + (100 - 150) * ratio)
        b = int(243 + (200 - 243) * ratio)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    draw = ImageDraw.Draw(img)
    
    # Zeichne "T" Symbol für Task
    margin = width // 5
    rect_left = margin
    rect_top = margin
    rect_right = width - margin
    rect_bottom = height - margin
    
    # Vertikaler Balken
    draw.rectangle(
        [rect_left + width // 6, rect_top, rect_right - width // 6, rect_bottom],
        fill=(76, 175, 80),
        outline=(255, 255, 255),
        width=1
    )
    
    # Horizontaler Balken oben
    draw.rectangle(
        [rect_left, rect_top, rect_right, rect_top + height // 4],
        fill=(255, 193, 7),
        outline=(255, 255, 255),
        width=1
    )
    
    img.save(assets_dir / filename)
    print(f"✓ Icon erstellt: {filename} ({width}x{height})")


if __name__ == "__main__":
    create_logo()
