"""
Generate spell card assets with distinct visual style from troops.
Spells have a different frame/border and magical effects.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_spell_card(name: str, cost: int, effect_desc: str, color_theme: tuple):
    """Create a spell card with magical styling."""
    width, height = 200, 300
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background with gradient effect (darker to lighter)
    for y in range(height):
        darkness = int(255 * (y / height) * 0.4)
        color = tuple(min(255, c + darkness) for c in color_theme)
        draw.rectangle([10, y, width-10, y+1], fill=color)
    
    # Magical border with glow effect
    border_color = (255, 215, 0, 200)  # Gold
    for i in range(4):
        draw.rectangle([5-i, 5-i, width-5+i, height-5+i], outline=border_color, width=2)
    
    # Inner decorative frame
    draw.rectangle([15, 15, width-15, height-15], outline=(200, 180, 255, 150), width=3)
    
    # Title area with spell symbol background
    draw.ellipse([width//2-40, 30, width//2+40, 110], fill=(100, 50, 150, 180))
    draw.ellipse([width//2-35, 35, width//2+35, 105], fill=(150, 100, 200, 200))
    
    # Magical symbol (star)
    center_x, center_y = width//2, 70
    points = []
    for i in range(10):
        angle = i * 36 * 3.14159 / 180
        radius = 25 if i % 2 == 0 else 12
        x = center_x + int(radius * __import__('math').cos(angle - 3.14159/2))
        y = center_y + int(radius * __import__('math').sin(angle - 3.14159/2))
        points.append((x, y))
    draw.polygon(points, fill=(255, 255, 100, 220))
    
    # Try to load font
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        cost_font = ImageFont.truetype("arialbd.ttf", 32)
        desc_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        cost_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
    
    # Card name
    name_bbox = draw.textbbox((0, 0), name, font=title_font)
    name_width = name_bbox[2] - name_bbox[0]
    draw.text((width//2 - name_width//2, 130), name, fill=(255, 255, 255), font=title_font)
    
    # Cost circle (top left)
    draw.ellipse([15, 15, 55, 55], fill=(80, 40, 120), outline=(200, 150, 255), width=3)
    cost_text = str(cost)
    cost_bbox = draw.textbbox((0, 0), cost_text, font=cost_font)
    cost_width = cost_bbox[2] - cost_bbox[0]
    cost_height = cost_bbox[3] - cost_bbox[1]
    draw.text((35 - cost_width//2, 35 - cost_height//2), cost_text, fill=(255, 255, 100), font=cost_font)
    
    # Effect description area
    effect_y = 170
    words = effect_desc.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=desc_font)
        if bbox[2] - bbox[0] < width - 40:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=desc_font)
        line_width = bbox[2] - bbox[0]
        draw.text((width//2 - line_width//2, effect_y + i*20), line, fill=(255, 255, 200), font=desc_font)
    
    # Type indicator at bottom
    draw.text((width//2-30, height-35), "⚡ SPELL", fill=(255, 215, 0), font=desc_font)
    
    return img


# Spell definitions with color themes
spells = [
    # Damage spells - Red/Orange theme
    ('Rayo', 2, 'Hace 3 de daño', (180, 50, 50)),
    ('Bola de Fuego', 3, 'Hace 4 de daño', (200, 80, 30)),
    ('Descarga Electrica', 1, 'Hace 2 de daño', (150, 150, 200)),
    ('Rafaga de Flechas', 3, '1 daño a todos', (160, 100, 60)),
    ('Tormenta de Fuego', 5, '2 daño a todos', (220, 60, 40)),
    
    # Healing spells - Green/White theme
    ('Curación', 1, 'Restaura 3 HP', (80, 180, 100)),
    ('Curación Mayor', 3, 'Restaura 7 HP', (100, 200, 120)),
    
    # Destruction - Purple/Dark theme
    ('Destierro', 4, 'Destruye 1 tropa', (100, 50, 120)),
    ('Aniquilar', 2, 'Destruye dañada', (120, 60, 140)),
    
    # Utility - Blue theme
    ('Dibujar Cartas', 2, 'Roba 2 cartas', (60, 100, 180)),
]

# Create assets directory
os.makedirs('assets/cards', exist_ok=True)

# Generate all spell cards
for name, cost, desc, color in spells:
    img = create_spell_card(name, cost, desc, color)
    # Save with transparent background - use same name as card for easy matching
    filename = f'{name}.png'
    img.save(f'assets/cards/{filename}', 'PNG')
    print(f'Generated: {filename}')

print(f'\n✨ Generated {len(spells)} spell card assets!')
