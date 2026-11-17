# Einheitliches Kanal-Cover (Pflicht für jedes Reel)
# Aufruf: python3 cover.py <hintergrund.png|jpg> "ZEILE 1" "ZEILE 2" <out.jpg> [akzentfarbe_hex]
# - Hintergrund: Hook-Frame oder Bild aus toolkit/bilder (wird 9:16 zugeschnitten, abgedunkelt)
# - Titel: max. 2 Zeilen, je max. ca. 14 Zeichen, GROSS. Zeile 2 in Akzentfarbe (Standard Gelb).
# - Alles Wichtige liegt in der Mitte (y 560-1360), damit es im Profilraster (3:4-Ausschnitt) sichtbar ist.
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1080, 1920
FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FM = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

def fit(d, t, size, maxw):
    f = ImageFont.truetype(FB, size)
    while d.textlength(t, font=f) > maxw:
        size -= 4; f = ImageFont.truetype(FB, size)
    return f

def make(bg, l1, l2, out, accent="FFD60A"):
    acc = tuple(int(accent[i:i+2], 16) for i in (0, 2, 4))
    im = Image.open(bg).convert("RGB")
    r = max(W / im.width, H / im.height); im = im.resize((int(im.width*r)+1, int(im.height*r)+1), Image.LANCZOS)
    x = (im.width - W)//2; y = (im.height - H)//2; im = im.crop((x, y, x+W, y+H))
    im = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(3))).enhance(0.45)
    d = ImageDraw.Draw(im)
    # Akzentbalken + Titel
    d.rectangle([90, 640, 240, 660], fill=acc)
    f1 = fit(d, l1, 150, W-160); f2 = fit(d, l2, 150, W-160)
    d.text((90, 690), l1, font=f1, fill=(255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
    d.text((90, 690+f1.size+30), l2, font=f2, fill=acc, stroke_width=8, stroke_fill=(0, 0, 0))
    # Kanal-Marke + KI-Hinweis
    d.text((90, 1300), "GAMING FACTS & NEWS", font=ImageFont.truetype(FB, 44), fill=(255, 255, 255))
    d.rounded_rectangle([W-300, 1295, W-90, 1355], 30, fill=(0, 0, 0))
    d.text((W-195, 1325), "KI-generiert", font=ImageFont.truetype(FM, 32), fill=(220, 220, 220), anchor="mm")
    im.save(out, quality=92)

if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], *(sys.argv[5:6]))
