"""Render docs/demo.gif — an animated terminal capture of `make demo`.

Runs the real demo, captures its real output, and renders it as a
typewriter-style terminal animation. No mocking: every frame's text is the
pipeline's actual stdout from this run.

Dev-time only (requires Pillow). Run from repo root:
    python3 scripts/render_demo_gif.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow required (dev-time only): pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)

# ---- capture real output ----------------------------------------------------
proc = subprocess.run(
    [sys.executable, "-m", "stowaway.cli", "audit", "--replay"],
    cwd=ROOT, capture_output=True, text=True, check=True,
)
lines = ["$ make demo"] + proc.stdout.rstrip().splitlines()

# ---- render -----------------------------------------------------------------
W, PAD, LH, FS = 860, 22, 22, 15
H = PAD * 2 + LH * (len(lines) + 1)
BG, FG = (16, 20, 26), (210, 215, 220)
ACCENT = {"⚓": (120, 200, 255), "💸": (140, 230, 150), "$": (140, 230, 150)}


def find_mono(size: int):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


FONT = find_mono(FS)


def frame(n_lines: int, cursor: bool) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # window chrome
    d.rounded_rectangle([(6, 2), (W - 6, H - 4)], radius=10, outline=(60, 66, 74), width=1)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([(20 + i * 22, 12), (32 + i * 22, 24)], fill=c)
    y = PAD + 22
    for line in lines[:n_lines]:
        color = FG
        for key, c in ACCENT.items():
            if key in line:
                color = c
                break
        if line.startswith("$"):
            color = (255, 220, 130)
        d.text((PAD + 8, y), line[:110], font=FONT, fill=color)
        y += LH
    if cursor and n_lines < len(lines):
        d.rectangle([(PAD + 8, y + 3), (PAD + 18, y + LH - 4)], fill=(140, 200, 120))
    return img


frames, durations = [], []
for i in range(1, len(lines) + 1):
    frames.append(frame(i, cursor=True))
    durations.append(420 if i <= 2 else 160)
frames.append(frame(len(lines), cursor=False))
durations.append(4000)  # hold the final state

frames[0].save(
    OUT / "demo.gif", save_all=True, append_images=frames[1:],
    duration=durations, loop=0, optimize=True,
)
print(f"wrote {OUT / 'demo.gif'} ({(OUT / 'demo.gif').stat().st_size // 1024} KB, "
      f"{len(frames)} frames, real output)")
