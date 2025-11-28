from PIL import Image, ImageDraw, ImageFont
import random
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'cards')
os.makedirs(OUT_DIR, exist_ok=True)

TEMPLATES = [
    # Basic cards
    ('Goblin', 1, 2),
    ('Archer', 2, 3),
    ('Knight', 3, 5),
    ('Mage', 4, 7),
    ('Golem', 5, 9),
    ('Slingshot', 1, 1),
    # Cards with Furia
    ('Berserker', 3, 4),
    ('Wolf', 2, 2),
    # Cards with Volar
    ('Dragon', 5, 6),
    ('Eagle', 2, 2),
    ('Bat', 1, 1),
    # Cards with Taunt
    ('Guardian', 3, 3),
    ('Wall', 2, 1),
    # Cards with Invocar Aliado
    ('Necromancer', 4, 3),
    ('Shaman', 3, 2),
]

CARD_SIZE = (200, 300)
ICON_SIZE = (48, 72)
FONT = ImageFont.load_default()


def random_color():
    return tuple(random.randint(40, 220) for _ in range(3))


def make_card_image(name, cost, dmg, idx):
    img = Image.new('RGB', CARD_SIZE, color=random_color())
    draw = ImageDraw.Draw(img)
    # Draw border
    draw.rectangle([5, 5, CARD_SIZE[0]-6, CARD_SIZE[1]-6], outline=(0,0,0), width=2)
    # Title
    draw.text((12, 12), name, fill=(255,255,255), font=FONT)
    # Cost circle
    draw.ellipse([12, 36, 52, 76], fill=(255,255,255))
    draw.text((22, 44), str(cost), fill=(0,0,0), font=FONT)
    # Damage at bottom
    draw.text((12, CARD_SIZE[1]-30), f'Dmg: {dmg}', fill=(255,255,255), font=FONT)
    path = os.path.join(OUT_DIR, f'{name.lower()}_{idx}.png')
    img.save(path)
    # also save a small icon variant for rest/mini views
    icon = img.resize(ICON_SIZE)
    icon_path = os.path.join(OUT_DIR, f'{name.lower()}_{idx}_icon.png')
    icon.save(icon_path)
    return path


def make_back():
    img = Image.new('RGB', CARD_SIZE, color=(40, 40, 120))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, CARD_SIZE[0]-11, CARD_SIZE[1]-11], outline=(255,255,255), width=3)
    draw.text((40, CARD_SIZE[1]//2-10), 'CARD BACK', fill=(255,255,255), font=FONT)
    path = os.path.join(OUT_DIR, 'card_back.png')
    img.save(path)
    # small back
    icon = img.resize(ICON_SIZE)
    icon_path = os.path.join(OUT_DIR, 'card_back_icon.png')
    icon.save(icon_path)
    return path


def generate(n=10):
    print(f'Generating {n} placeholder card images into {OUT_DIR}')
    # ensure at least one image of each template
    idxes = {}
    for name, cost, dmg in TEMPLATES:
        idxes.setdefault(name, 0)
        make_card_image(name, cost, dmg, idxes[name])
        idxes[name] += 1
    # generate remaining random images up to n
    remaining = max(0, n - len(TEMPLATES))
    for i in range(remaining):
        name, cost, dmg = random.choice(TEMPLATES)
        idxes.setdefault(name, 0)
        make_card_image(name, cost, dmg, idxes[name])
        idxes[name] += 1
    make_back()
    print('Done.')


if __name__ == '__main__':
    generate(10)
