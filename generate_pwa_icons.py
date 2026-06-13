"""
DDay Controls PWA Icon Generator
----------------------------------
Copies and resizes existing tool PNGs into pwa/icons/ at the sizes
needed by manifest.json and the HTML pages.

Run from the project directory:
    python generate_pwa_icons.py
"""

from __future__ import annotations
import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import Qt

app = QApplication.instance() or QApplication(sys.argv)

src_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(src_dir, "pwa", "icons")
os.makedirs(out_dir, exist_ok=True)


def scale_to_square(src_path: str, dest_path: str, size: int) -> None:
    img = QImage(src_path)
    if img.isNull():
        print(f"  WARNING: could not load {src_path}")
        return
    scaled = img.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    out = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    out.fill(0)
    p = QPainter(out)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    p.drawImage(x, y, scaled)
    p.end()
    out.save(dest_path)
    print(f"  Saved: {dest_path}")


tasks = [
    # (source_filename,             dest_filename,         size)
    ("DDay Logo.png",              "icon-192.png",         192),
    ("DDay Logo.png",              "icon-512.png",         512),
    ("DDay_Converter.png",         "converter-icon.png",   256),
    ("DDay_ASCII_Chart.png",       "ascii-icon.png",       256),
]

for src_name, dest_name, size in tasks:
    src = os.path.join(src_dir, src_name)
    dest = os.path.join(out_dir, dest_name)
    if not os.path.exists(src):
        print(f"  SKIP (not found): {src_name}")
        continue
    scale_to_square(src, dest, size)

print("\nDone. Icons are in pwa/icons/")
