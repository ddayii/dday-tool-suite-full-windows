"""
DDay Controls Converter Icon Generator
---------------------------------------
Run this script to produce DDay_Converter.png and DDay_Converter.ico.
Matches the rendering style of generate_ascii_chart_icon.py exactly —
same radial gradient background, same bar colour, same font family.
"""

from __future__ import annotations
import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import (
    QImage, QPainter, QColor, QFont, QBrush, QPainterPath, QRadialGradient,
)
from PySide6.QtCore import Qt, QRect, QRectF, QPointF

app = QApplication.instance() or QApplication(sys.argv)

# ── Tweak these ──────────────────────────────────────────────────────────────
BG_CENTER      = QColor("#263626")   # lighter green at gradient centre
BG_EDGE        = QColor("#0e180e")   # near-black green at corners
BAR_COLOR      = QColor("#0b140b")   # bottom bar — same dark tone as ASCII icon
ORANGE         = QColor("#c86428")   # burnt orange — main accent
BAR_TEXT_COLOR = QColor("#d8d0c4")   # warm off-white for bottom bar labels

HERO_TEXT      = "0x"               # hex prefix — the tool's signature symbol
HERO_SCALE     = 0.50               # hero text height as fraction of icon size
ARROW_TEXT     = "→"               # conversion-direction indicator
ARROW_SCALE    = 0.195              # arrow text height fraction
BAR_TEXT       = "ASCII   HEX   DEC   OCT   BIN"
BAR_SCALE      = 0.076              # bar label text height fraction (5 items → slightly smaller)
BAR_HEIGHT     = 0.225              # bottom bar height as fraction of icon size
CORNER_RADIUS  = 0.085              # rounded corner radius fraction
FONT_FAMILY    = "Segoe UI"
# ─────────────────────────────────────────────────────────────────────────────


def render(size: int) -> QImage:
    img = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)

    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)

    r = CORNER_RADIUS * size

    # Rounded background with radial gradient (centre-lit, dark corners)
    bg_path = QPainterPath()
    bg_path.addRoundedRect(QRectF(0, 0, size, size), r, r)
    grad = QRadialGradient(QPointF(size * 0.5, size * 0.42), size * 0.65)
    grad.setColorAt(0.0, BG_CENTER)
    grad.setColorAt(1.0, BG_EDGE)
    p.fillPath(bg_path, QBrush(grad))

    # Bottom bar (clipped to rounded background — no seam)
    bar_h = BAR_HEIGHT * size
    bar_rect = QRectF(0, size - bar_h, size, bar_h)
    bar_path = QPainterPath()
    bar_path.addRect(bar_rect)
    p.fillPath(bg_path.intersected(bar_path), QBrush(BAR_COLOR))

    # Hero text  "0x"  — centred in the content area
    font_hero = QFont(FONT_FAMILY, 1, QFont.Bold)
    font_hero.setPixelSize(max(1, int(HERO_SCALE * size)))
    p.setFont(font_hero)
    p.setPen(ORANGE)
    hero_area = QRect(0, 0, size, int(size * 0.74))
    p.drawText(hero_area, Qt.AlignHCenter | Qt.AlignVCenter, HERO_TEXT)

    # Arrow  "→"  — upper-right, smaller, acts as a superscript decorator
    font_arrow = QFont(FONT_FAMILY, 1, QFont.Bold)
    font_arrow.setPixelSize(max(1, int(ARROW_SCALE * size)))
    p.setFont(font_arrow)
    p.setPen(ORANGE)
    arrow_area = QRect(int(size * 0.48), int(size * 0.04), int(size * 0.48), int(size * 0.32))
    p.drawText(arrow_area, Qt.AlignRight | Qt.AlignTop, ARROW_TEXT)

    # Bottom bar labels
    font_bar = QFont(FONT_FAMILY, 1, QFont.Bold)
    font_bar.setPixelSize(max(1, int(BAR_SCALE * size)))
    p.setFont(font_bar)
    p.setPen(BAR_TEXT_COLOR)
    bar_text_area = QRect(0, int(size - bar_h), size, int(bar_h))
    p.drawText(bar_text_area, Qt.AlignCenter, BAR_TEXT)

    p.end()
    return img


out_dir = os.path.dirname(os.path.abspath(__file__))

# PNG — full resolution
png_path = os.path.join(out_dir, "DDay_Converter.png")
render(512).save(png_path)
print(f"Saved: {png_path}")

# ICO — multi-size, requires Pillow  (pip install pillow)
ico_path = os.path.join(out_dir, "DDay_Converter.ico")
try:
    from PIL import Image as PILImage

    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    frames: list = []
    for s in ico_sizes:
        qimg = render(s).convertToFormat(QImage.Format_RGBA8888)
        raw = bytes(qimg.bits())
        pil = PILImage.frombytes("RGBA", (s, s), raw)
        frames.append(pil)

    frames[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=frames[1:],
    )
    print(f"Saved: {ico_path}")

except ImportError:
    print(
        "Pillow not found — .ico skipped.\n"
        "Install with:  pip install pillow\n"
        "The .png works for window icons; .ico is only needed for PyInstaller."
    )

print("\nDone.")
