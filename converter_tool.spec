# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None
project_dir = Path.cwd()

datas = []
for icon_name in ("DDay_Converter.ico", "DDay_Converter.png"):
    icon_path = project_dir / icon_name
    if icon_path.exists():
        datas.append((str(icon_path), "."))

hiddenimports = [
    "ascii_chart",
    "copy_format_editor",
    "dday_controls_common",
    "fanuc_io_tool",
    "fanuc_io_parser",
    "fanuc_template",
    "fanuc_csv_generator",
    "fanuc_karel_generator",
    "openpyxl",
]

a = Analysis(
    ["converter_tool.py"],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DDay Controls Conversion Tool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="DDay_Converter.ico" if (project_dir / "DDay_Converter.ico").exists() else None,
)
