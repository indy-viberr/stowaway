"""Render synthetic POD scan images for every POD in data/pods.json.

These are the physical artifacts the vision model reads in live mode — fake
delivery receipts that look like dock-office scans: off-white paper, slight
rotation, scanner noise, a handwritten signature scrawl (or pointedly not).

Requires Pillow (dev-time only; the demo never needs these rendered).
Run from repo root:  python3 scripts/render_pods.py
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit("Pillow required: pip install pillow (dev-time only)")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "pod_scans"
OUT.mkdir(parents=True, exist_ok=True)

rng = random.Random(1979)

FONT_DIRS = ["/usr/share/fonts/truetype/lato", "/usr/share/fonts/truetype/dejavu",
             "/System/Library/Fonts", "C:/Windows/Fonts"]


def find_font(names: list[str], size: int) -> ImageFont.FreeTypeFont:
    for d in FONT_DIRS:
        for n in names:
            p = Path(d) / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


F_HEAD = find_font(["Lato-Bold.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"], 34)
F_BODY = find_font(["Lato-Regular.ttf", "DejaVuSans.ttf", "Arial.ttf"], 24)
F_SMALL = find_font(["Lato-Regular.ttf", "DejaVuSans.ttf", "Arial.ttf"], 19)
F_SCRAWL = find_font(["Lato-LightItalic.ttf", "Lato-Italic.ttf", "DejaVuSans-Oblique.ttf"], 30)


def scrawl_signature(draw: ImageDraw.ImageDraw, x: int, y: int, name: str, quality: float):
    """A fake pen signature: jittered cursive-ish polyline + initials."""
    pts = []
    px = x
    for i, ch in enumerate(name[:14]):
        amp = 14 + (1 - quality) * 10
        px += rng.randint(9, 16)
        py = y + int(math.sin(i * 1.7 + rng.random()) * amp) + rng.randint(-3, 3)
        pts.append((px, py))
    if len(pts) > 1:
        draw.line(pts, fill=(25, 25, 80), width=3)
    # flourish underline
    draw.line([(x, y + 26), (px + 18, y + 22 + rng.randint(-4, 4))], fill=(25, 25, 80), width=2)
    if quality > 0.45:  # legible enough to also write the name
        draw.text((x, y + 34), name, font=F_SCRAWL, fill=(35, 35, 90))


def render(load: dict, pod: dict) -> Image.Image:
    W, H = 820, 1060
    img = Image.new("RGB", (W, H), (246, 244, 238))
    d = ImageDraw.Draw(img)

    # header
    d.text((50, 42), "PROOF OF DELIVERY", font=F_HEAD, fill=(20, 20, 20))
    d.text((50, 88), "Straight Bill of Lading — non-negotiable", font=F_SMALL, fill=(90, 90, 90))
    d.line([(50, 120), (W - 50, 120)], fill=(60, 60, 60), width=3)

    rows = [
        ("LOAD / REF #", load["load_id"]),
        ("CARRIER", f"{load['carrier_name']}   MC {load['carrier_mc']}"),
        ("LANE", load["lane"]),
        ("PICKUP DATE", load["pickup_date"]),
        ("CONSIGNEE", pod.get("consignee_name", load["consignee"])),
        ("PIECES / WEIGHT", f"{rng.randint(4, 26)} pallets / {rng.randint(8, 44):,}00 lbs"),
        ("SEAL #", f"{rng.randint(100000, 999999)}"),
    ]
    y = 150
    for k, v in rows:
        d.text((50, y), k, font=F_SMALL, fill=(120, 120, 120))
        d.text((280, y - 4), str(v), font=F_BODY, fill=(25, 25, 25))
        y += 52

    d.line([(50, y + 8), (W - 50, y + 8)], fill=(150, 150, 150), width=1)
    d.text((50, y + 24), "Received in good condition except as noted:", font=F_SMALL, fill=(90, 90, 90))
    d.rectangle([(50, y + 52), (W - 50, y + 130)], outline=(170, 170, 170), width=1)
    if rng.random() < 0.25:
        d.text((62, y + 70), rng.choice(
            ["1 pallet shrinkwrap torn, contents OK", "arrived 14:5x, dock busy", ""]),
            font=F_SCRAWL, fill=(40, 40, 95))

    # signature block
    sy = y + 170
    d.text((50, sy), "RECEIVER SIGNATURE", font=F_SMALL, fill=(120, 120, 120))
    d.line([(50, sy + 64), (430, sy + 64)], fill=(80, 80, 80), width=2)
    d.text((470, sy), "DATE", font=F_SMALL, fill=(120, 120, 120))
    d.line([(470, sy + 64), (W - 50, sy + 64)], fill=(80, 80, 80), width=2)

    if pod.get("signature_present"):
        signer = rng.choice(
            ["Marisol", "DeShawn", "Priya", "Tomás", "Ingrid", "Khalil", "June"]
        ) + " " + rng.choice(
            ["Reyes", "Okafor", "Lindqvist", "Tran", "Maddox", "Iwu", "Calderon"])
        scrawl_signature(d, 70, sy + 28, signer, pod.get("signature_legibility", 0.8))
    if pod.get("date_legible", True):
        d.text((480, sy + 30), load["pickup_date"], font=F_SCRAWL, fill=(35, 35, 90))

    d.text((50, H - 60), "White: shipper · Yellow: carrier · Pink: consignee",
           font=F_SMALL, fill=(150, 150, 150))

    # scanner artifacts: rotate slightly, noise, soft blur, edge shadow
    angle = rng.uniform(-1.6, 1.6)
    img = img.rotate(angle, expand=True, fillcolor=(210, 208, 200))
    px = img.load()
    for _ in range(int(img.width * img.height * 0.004)):
        x_, y_ = rng.randrange(img.width), rng.randrange(img.height)
        g = rng.randint(120, 235)
        px[x_, y_] = (g, g, g)
    quality = pod.get("doc_quality", 0.8)
    if quality < 0.65:
        img = img.filter(ImageFilter.GaussianBlur(1.1))
    return img


def main() -> None:
    loads = {l["load_id"]: l for l in json.loads((ROOT / "data" / "loads.json").read_text())}
    pods = json.loads((ROOT / "data" / "pods.json").read_text())
    n = 0
    for pod in pods:
        if not pod.get("present"):
            continue  # the missing POD is missing — that's the point
        load = loads[pod["load_id"]]
        render(load, pod).save(OUT / f"{pod['load_id']}.png")
        n += 1
    print(f"rendered {n} POD scans -> {OUT}")


if __name__ == "__main__":
    main()
