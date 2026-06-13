"""
DDay Controls ASCII Chart Icon Generator
-----------------------------------------
Run this script to produce DDay_ASCII_Chart.png and DDay_ASCII_Chart.ico.
Tweak the constants below to adjust colors, sizes, or layout.
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
# Radial gradient — centre lit, corners dark (matches converter & FANUC icons)
BG_CENTER      = QColor("#263626")   # lighter green at gradient centre
BG_EDGE        = QColor("#0e180e")   # near-black green at corners
BAR_COLOR      = QColor("#0b140b")   # bottom bar — same dark tone as corners
ORANGE         = QColor("#c86428")   # burnt orange — main accent
ORANGE_DIM     = QColor("#a0501e")   # dimmer orange for the '65' subscript
BAR_TEXT_COLOR = QColor("#d8d0c4")   # warm off-white for bottom bar labels

HERO_TEXT      = "'A'"               # main character displayed
HERO_SCALE     = 0.56                # hero text height as fraction of icon size
SUB_TEXT       = "65"                # subscript below the hero
SUB_SCALE      = 0.16                # subscript text height fraction
BAR_TEXT       = "HEX    DEC    BIN    OCT"
BAR_SCALE      = 0.085               # bar label text height fraction
BAR_HEIGHT     = 0.225               # bottom bar height as fraction of icon size
CORNER_RADIUS  = 0.085               # rounded corner radius fraction
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

    # Bottom bar (clipped to rounded background)
    bar_h = BAR_HEIGHT * size
    bar_rect = QRectF(0, size - bar_h, size, bar_h)
    bar_path = QPainterPath()
    bar_path.addRect(bar_rect)
    p.fillPath(bg_path.intersected(bar_path), QBrush(BAR_COLOR))

    # Hero text  'A'
    font_hero = QFont(FONT_FAMILY, 1, QFont.Bold)
    font_hero.setPixelSize(max(1, int(HERO_SCALE * size)))
    p.setFont(font_hero)
    p.setPen(ORANGE)
    hero_area = QRect(0, int(size * 0.01), size, int(size * 0.68))
    p.drawText(hero_area, Qt.AlignHCenter | Qt.AlignVCenter, HERO_TEXT)

    # Subscript  65
    font_sub = QFont(FONT_FAMILY, 1)
    font_sub.setPixelSize(max(1, int(SUB_SCALE * size)))
    p.setFont(font_sub)
    p.setPen(ORANGE_DIM)
    sub_area = QRect(0, int(size * 0.60), size, int(size * 0.18))
    p.drawText(sub_area, Qt.AlignHCenter | Qt.AlignVCenter, SUB_TEXT)

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
png_path = os.path.join(out_dir, "DDay_ASCII_Chart.png")
render(512).save(png_path)
print(f"Saved: {png_path}")

# ICO — multi-size, requires Pillow  (pip install pillow)
ico_path = os.path.join(out_dir, "DDay_ASCII_Chart.ico")
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

print("\nDone. To use the icon, set in dday_controls_common.py TOOL_REGISTRY:")
print('    "ascii_chart": { ..., "icon_png": "DDay_ASCII_Chart.png" }')
