"""
generate_test_images.py — Crea 4 immagini sintetiche per i test 2-5.
Rettangoli colorati con testo che Moondream può descrivere.
Crea file JPEG 512x512 in validation/images/.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

OUT_DIR = Path(__file__).resolve().parent.parent / "validation" / "images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Definizione immagini: (filename, colore_sfondo, colore_testo, label_inciale, descrizione)
# La "descrizione" è solo per noi; l'immagine mostra label_inciale + descrizione come testo.
IMAGES = [
    {
        "name": "caso_002.jpg",
        "bg": (180, 180, 190),        # grigio
        "fg": (30, 30, 40),
        "label": "COMPLETO LANA",
        "desc": "Giacca grigia in lana\nclassica sartoriale\nper l'inverno",
    },
    {
        "name": "caso_003.jpg",
        "bg": (90, 70, 40),           # marrone scuro
        "fg": (240, 220, 200),
        "label": "SCARPE TREKKING",
        "desc": "Stivali marroni\ntacchette spesse\nper montagna",
    },
    {
        "name": "caso_004.jpg",
        "bg": (40, 50, 90),           # blu scuro
        "fg": (220, 220, 240),
        "label": "MAGLIONE LANA",
        "desc": "Maglione blu in lana\npolsi a costine\nper sere fresche",
    },
    {
        "name": "caso_005.jpg",
        "bg": (250, 250, 250),        # bianco
        "fg": (200, 50, 50),
        "label": "COSTUME A POIS",
        "desc": "Costume da bagno\nrosso a pois bianchi\nper estate",
    },
]


def get_font(size: int):
    # Prova font di sistema comuni
    for name in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Tahoma.ttf",
        "/Library/Fonts/Arial.ttf",
    ]:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def make_image(spec: dict):
    img = Image.new("RGB", (512, 512), spec["bg"])
    draw = ImageDraw.Draw(img)

    # Bordo
    draw.rectangle([10, 10, 502, 502], outline=spec["fg"], width=3)

    # Label grande in alto
    f_label = get_font(42)
    label = spec["label"]
    bbox = draw.textbbox((0, 0), label, font=f_label)
    w = bbox[2] - bbox[0]
    draw.text(((512 - w) // 2, 60), label, fill=spec["fg"], font=f_label)

    # Linea separatrice
    draw.line([80, 130, 432, 130], fill=spec["fg"], width=2)

    # Descrizione centrale
    f_desc = get_font(28)
    lines = spec["desc"].split("\n")
    y = 180
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f_desc)
        w = bbox[2] - bbox[0]
        draw.text(((512 - w) // 2, y), line, fill=spec["fg"], font=f_desc)
        y += 40

    # Footer
    f_small = get_font(18)
    footer = "ICHS synthetic test image"
    bbox = draw.textbbox((0, 0), footer, font=f_small)
    w = bbox[2] - bbox[0]
    draw.text(((512 - w) // 2, 470), footer, fill=spec["fg"], font=f_small)

    out_path = OUT_DIR / spec["name"]
    img.save(out_path, "JPEG", quality=85)
    return out_path


def main():
    print(f"🎨 Genero {len(IMAGES)} immagini sintetiche in {OUT_DIR}...\n")
    for spec in IMAGES:
        p = make_image(spec)
        print(f"  ✓ {p.name} ({p.stat().st_size} bytes) — {spec['label']}")
    print(f"\n✅ Tutte le immagini create in {OUT_DIR}")


if __name__ == "__main__":
    main()
