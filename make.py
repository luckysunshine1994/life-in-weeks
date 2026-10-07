import colorsys, math, random
from datetime import date
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BIRTH = date(1994, 10, 19)
TODAY = date.today()
YEARS = 85
W, H = 1179, 2556
S = 3  # supersample for smooth dots

BG = (0, 0, 0)
random.seed(19101994)


def age_and_week(d):
    age = d.year - BIRTH.year - ((d.month, d.day) < (BIRTH.month, BIRTH.day))
    last_bd = BIRTH.replace(year=BIRTH.year + age)
    return age, min((d - last_bd).days // 7, 51)


def hsv(h, s, v):
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h % 1, s, v))


age, wk = age_and_week(TODAY)
big = Image.new("RGB", (W * S, H * S), BG)
dr = ImageDraw.Draw(big)

margin_x, cols, top = 100, 52, 660
cell = (W - 2 * margin_x) / cols
gap = cell * 0.6


def centre(y, x):
    return (margin_x + cell * (x + 0.5),
            top + cell * (y + 0.5) + (y // 10) * gap)


def hue(y, x):
    # rainbow runs down the years, with a gentle diagonal swirl across each row
    return 0.92 - (y / YEARS) * 0.95 + 0.06 * math.sin(x / cols * math.pi * 2 + y * 0.3)


for y in range(YEARS):
    for x in range(cols):
        cx, cy = centre(y, x)
        h = hue(y, x)
        if (y, x) < (age, wk):
            c = hsv(h, 0.62, 0.98)
            r = cell * random.uniform(0.27, 0.36)
        elif (y, x) == (age, wk):
            continue
        else:
            c = hsv(h, 0.35, 0.36)
            r = cell * 0.22
        dr.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=c)

img = big.resize((W, H), Image.LANCZOS)

# current week: glowing four-point sparkle
cx, cy = centre(age, wk)
glow = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
for rr, a in [(cell * 1.6, 70), (cell * 0.9, 140)]:
    gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(a, int(a * 0.85), int(a * 0.5)))
glow = glow.filter(ImageFilter.GaussianBlur(cell * 0.6))
img = Image.composite(img, img, Image.new("L", (W, H), 255))
from PIL import ImageChops
img = ImageChops.add(img, glow)

star = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
sd = ImageDraw.Draw(star)
R, r_in = cell * 0.95, cell * 0.2
pts = []
for i in range(8):
    ang = -math.pi / 2 + i * math.pi / 4
    rad = R if i % 2 == 0 else r_in
    pts.append(((cx + rad * math.cos(ang)) * S, (cy + rad * math.sin(ang)) * S))
sd.polygon(pts, fill=(255, 246, 214, 255))
star = star.resize((W, H), Image.LANCZOS)
img.paste(star, (0, 0), star)

# label in rainbow letters
font = ImageFont.truetype("InterDisplay-Medium.otf", 32)
lived = age * 52 + wk
label = f"week {lived + 1:,} of {YEARS * 52:,}"
d2 = ImageDraw.Draw(img)
total_w = d2.textlength(label, font=font)
x0 = (W - total_w) / 2
ty = top + cell * YEARS + 8 * gap + 50
for i, ch in enumerate(label):
    col = hsv(0.92 - i / len(label) * 0.95, 0.45, 0.95)
    d2.text((x0, ty), ch, font=font, fill=col)
    x0 += d2.textlength(ch, font=font)

img.save("wallpaper.png")
print("ok")
