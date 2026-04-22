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
    """Erstellt den SplashScreen (620x300) mit minimalem Design."""
    width, height = 620, 300
    
    # Tiefer Nacht-Hintergrund
    img = Image.new('RGB', (width, height), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # Linke Seite: Minimales Fokus-Symbol (konzentrische Kreise)
    center_x, center_y = 100, 150
    
    # Drei konzentrische Kreise (Fokus-Metapher)
    colors = [(100, 200, 255), (80, 180, 255), (60, 160, 255)]
    sizes = [70, 50, 30]
    
    for color, size in zip(colors, sizes):
        draw.ellipse(
            [center_x - size, center_y - size, center_x + size, center_y + size],
            outline=color,
            width=2
        )
    
    # Zentraler Punkt
    draw.ellipse(
        [center_x - 8, center_y - 8, center_x + 8, center_y + 8],
        fill=(100, 200, 255)
    )
    
    # Rechte Seite: Moderner Text
    try:
        title_font = ImageFont.truetype("arial.ttf", 52)
        subtitle_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # TaskSense
    draw.text((220, 100), "TaskSense", fill=(255, 255, 255), font=title_font)
    
    # Untertitel mit Akzentfarbe
    draw.text((220, 180), "Stay Focused", fill=(100, 200, 255), font=subtitle_font)
    
    img.save(assets_dir / "SplashScreen.png")
    print("✓ SplashScreen erstellt: SplashScreen.png (620x300)")


def create_icon(assets_dir: Path, filename: str, size: tuple):
    """Erstellt ein minimales Icon mit Fokus-Symbol."""
    
    width, height = size
    
    # Dunkler Hintergrund
    img = Image.new('RGB', (width, height), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = width // 2, height // 2
    
    # Drei konzentrische Kreise für Fokus
    line_widths = [max(1, width // 25), max(1, width // 30), max(1, width // 35)]
    radii = [width // 2 - 3, width // 3, width // 5]
    
    for line_width, radius in zip(line_widths, radii):
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=(100, 200, 255),
            width=line_width
        )
    
    # Zentraler Punkt
    point_size = max(1, width // 10)
    draw.ellipse(
        [center_x - point_size, center_y - point_size, center_x + point_size, center_y + point_size],
        fill=(100, 200, 255)
    )
    
    img.save(assets_dir / filename)
    print(f"✓ Icon erstellt: {filename} ({width}x{height})")


if __name__ == "__main__":
    create_logo()
