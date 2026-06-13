"""
DDay Controls Common Module - Qt Edition (PySide6)
===================================================
Shared module for:
    - converter_tool.py
    - ascii_chart.py

Install/build instructions are in the launcher files.
"""


from __future__ import annotations

import ctypes
import json
import math
import os
import platform
import re
import sys
import importlib
import subprocess
from collections import OrderedDict

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QActionGroup, QIcon, QPixmap, QColor
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMenuBar, QMessageBox,
    QFileDialog, QInputDialog, QPushButton, QScrollArea, QSizePolicy, QStatusBar, QTableWidget,
    QTableWidgetItem, QTabWidget, QTextEdit, QToolButton, QVBoxLayout, QWidget, QFrame
)


# ******************************************************************************
#
# GLOBALS & CONFIGURATION CONSTANTS
#
# ******************************************************************************


APP_NAME = "DDay Controls Conversion Tool"
APP_VERSION = "2.1.1"
COMPANY_NAME = "DDay Controls"
ICON_ICO = "DDay_Converter.ico"
ICON_PNG = "DDay_Converter.png"

# UI Layout Element Widths
COPY_BUTTON_WIDTH = 80
CLEAR_BUTTON_WIDTH = 90
SWAP_BUTTON_WIDTH = 90
COPY_RESULT_WIDTH = 110
CONVERT_BUTTON_WIDTH = 110

# Theme color definitions.
# "System" is handled by resolve_theme() and maps to Dark or Light.
THEMES = {
    "Dark": {
        "main_bg": "#20242b",
        "panel_bg": "#252b34",
        "input_bg": "#323842",

        "text": "#ebeff4",
        "title": "#ffffff",
        "subtitle": "#dce8ff",

        "button_bg": "#2c313c",
        "button_hover": "#3a4150",
        "button_pressed": "#262b35",

        "border": "#d9d9d9",
        "input_border": "#6e7888",
        "accent": "#5f7394",

        "menu_selected": "#344257",

        "group_title_bg": "#20242b",

        "tab_selected": "#303746",

        "table_header": "#303746",
        "table_bg": "#252b34",
        "table_alt": "#2b313b",
        "table_selected": "#506b8d",
        "table_selected_active": "#4a6484",
        "char_col": "#303746",

        "locked_text": "#dce8ff",
        "disabled_text": "#6e7888",
    },

    "Light": {
        "main_bg": "#f0f4fa",
        "panel_bg": "#f8f9fb",
        "input_bg": "#ffffff",

        "text": "#121822",
        "title": "#121822",
        "subtitle": "#4b586c",

        "button_bg": "#c9d4e2",
        "button_hover": "#b7c7da",
        "button_pressed": "#a8bbd1",

        "border": "#9ca8b8",
        "input_border": "#9ca8b8",
        "accent": "#6f96d1",

        "menu_selected": "#dcecff",

        "group_title_bg": "#f0f4fa",

        "tab_selected": "#dce8f7",

        "table_header": "#e6edf7",
        "table_bg": "#f3f6fa",
        "table_alt": "#dde5f0",
        "table_selected": "#8db8f2",
        "table_selected_active": "#80b0ec",
        "char_col": "#d4deeb",

        "locked_text": "#4b586c",
        "disabled_text": "#9ca8b8",
    },
}

# Core copy formats
CORE_COPY_FORMATS = OrderedDict({
    "None": ("", ""),
    "Custom": (None, None),
})

# Default copy format groups
DEFAULT_COPY_FORMAT_GROUPS = OrderedDict({
    "Siemens PLC": [
        {"name": "Siemens DINT", "prefix": "L#", "suffix": ""},
        {"name": "Siemens HEX Byte", "prefix": "B#16#", "suffix": ""},
        {"name": "Siemens HEX Word", "prefix": "W#16#", "suffix": ""},
        {"name": "Siemens HEX DWord", "prefix": "DW#16#", "suffix": ""},
        {"name": "Siemens Binary", "prefix": "2#", "suffix": ""},
        {"name": "Siemens Time", "prefix": "T#", "suffix": ""},
        {"name": "Siemens S5Time", "prefix": "S5T#", "suffix": ""},
    ],
    "Allen-Bradley PLC": [
        {"name": "AB Hex", "prefix": "16#", "suffix": ""},
        {"name": "AB Binary", "prefix": "2#", "suffix": ""},
    ],
    "Mitsubishi PLC": [
        {"name": "Mitsubishi Hex", "prefix": "H", "suffix": ""},
        {"name": "Mitsubishi Binary", "prefix": "B", "suffix": ""},
    ],
    "FANUC Robot": [
        {"name": "FANUC Register", "prefix": "R[", "suffix": "]"},
        {"name": "FANUC Position Register", "prefix": "PR[", "suffix": "]"},
        {"name": "FANUC Digital Input", "prefix": "DI[", "suffix": "]"},
        {"name": "FANUC Digital Output", "prefix": "DO[", "suffix": "]"},
        {"name": "FANUC Group Input", "prefix": "GI[", "suffix": "]"},
        {"name": "FANUC Group Output", "prefix": "GO[", "suffix": "]"},
        {"name": "FANUC Flag", "prefix": "F[", "suffix": "]"},
    ],
    "Python": [
        {"name": "Python HEX", "prefix": "0x", "suffix": ""},
        {"name": "Python Binary", "prefix": "0b", "suffix": ""},
        {"name": "Python Octal", "prefix": "0o", "suffix": ""},
        {"name": "Python String", "prefix": "\"", "suffix": "\""},
        {"name": "Python Byte String", "prefix": "b\"", "suffix": "\""},
    ],
    "C / C++": [
        {"name": "C HEX", "prefix": "0x", "suffix": ""},
        {"name": "C Unsigned", "prefix": "", "suffix": "U"},
        {"name": "C Long", "prefix": "", "suffix": "L"},
        {"name": "C Unsigned Long", "prefix": "", "suffix": "UL"},
        {"name": "C Float", "prefix": "", "suffix": "f"},
    ],
    "Java": [
        {"name": "Java HEX", "prefix": "0x", "suffix": ""},
        {"name": "Java Binary", "prefix": "0b", "suffix": ""},
        {"name": "Java Long", "prefix": "", "suffix": "L"},
    ],
    "JavaScript": [
        {"name": "JavaScript HEX", "prefix": "0x", "suffix": ""},
        {"name": "JavaScript Binary", "prefix": "0b", "suffix": ""},
        {"name": "JavaScript Octal", "prefix": "0o", "suffix": ""},
    ],
    "Generic Text": [
        {"name": "Quoted", "prefix": "\"", "suffix": "\""},
        {"name": "Single Quoted", "prefix": "'", "suffix": "'"},
        {"name": "Parentheses", "prefix": "(", "suffix": ")"},
        {"name": "Brackets", "prefix": "[", "suffix": "]"},
        {"name": "Braces", "prefix": "{", "suffix": "}"},
        {"name": "Angle Brackets", "prefix": "<", "suffix": ">"},
    ],
})

# ------------------------------------------------------------------------------
# Build active copy-format dropdown list from enabled groups
def build_copy_formats_from_groups(
    groups: dict,
    enabled_groups: list[str],
) -> OrderedDict[str, tuple[str | None, str | None]]:
    """Build active dropdown copy formats from enabled grouped presets."""

    formats: OrderedDict[str, tuple[str | None, str | None]] = OrderedDict()
    formats["None"] = ("", "")

    for group_name in enabled_groups:
        for item in groups.get(group_name, []):
            name = str(item.get("name", "")).strip()
            if not name or name in formats:
                continue

            formats[name] = (
                str(item.get("prefix", "")),
                str(item.get("suffix", "")),
            )

    formats["Custom"] = (None, None)

    return formats


# ------------------------------------------------------------------------------
# Return copy-format groups with the user custom group guaranteed
def copy_format_groups_with_user_group(groups: dict | None = None) -> OrderedDict:
    """Return copy-format groups with User Custom available."""
    source = groups if groups is not None else PREFERENCES.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS)
    ordered = OrderedDict(source)
    if "User Custom" not in ordered:
        ordered["User Custom"] = []
    return ordered


# ------------------------------------------------------------------------------
# Return copy-format group display order
def copy_format_group_order(groups: dict | None = None, preferences: dict | None = None) -> list[str]:
    """Return copy-format group order with missing groups appended."""
    prefs = preferences if preferences is not None else PREFERENCES
    active_groups = copy_format_groups_with_user_group(
        groups if groups is not None else prefs.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS)
    )

    saved_order = list(prefs.get("copy_format_group_order", []))
    ordered = [name for name in saved_order if name in active_groups]

    for name in active_groups.keys():
        if name not in ordered:
            ordered.append(name)

    return ordered


# ------------------------------------------------------------------------------
# Return enabled copy-format groups in display order
def ordered_enabled_copy_format_groups(preferences: dict | None = None) -> list[str]:
    """Return enabled copy-format groups in saved display order."""
    prefs = preferences if preferences is not None else PREFERENCES
    groups = copy_format_groups_with_user_group(prefs.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS))
    enabled = set(prefs.get("enabled_copy_format_groups", list(groups.keys())))

    return [
        name
        for name in copy_format_group_order(groups, prefs)
        if name in enabled and name in groups
    ]


# ------------------------------------------------------------------------------
# Save copy-format groups and enabled group order to preferences
def set_copy_format_group_preferences(groups: OrderedDict, enabled_groups: list[str], group_order: list[str]) -> None:
    """Save group definitions, enabled state, and display order to preferences."""
    PREFERENCES["copy_format_groups"] = copy_format_groups_with_user_group(groups)
    PREFERENCES["copy_format_group_order"] = [
        name
        for name in group_order
        if name in PREFERENCES["copy_format_groups"]
    ]
    PREFERENCES["enabled_copy_format_groups"] = [
        name
        for name in group_order
        if name in enabled_groups and name in PREFERENCES["copy_format_groups"]
    ]


# ------------------------------------------------------------------------------
# Rebuild global copy-format lookup from preferences
def rebuild_global_copy_formats() -> None:
    """Rebuild the active global copy-format lookup from saved preferences."""
    global COPY_FORMATS

    COPY_FORMATS = build_copy_formats_from_groups(
        PREFERENCES["copy_format_groups"],
        ordered_enabled_copy_format_groups(PREFERENCES),
    )
    PREFERENCES["copy_formats"] = COPY_FORMATS

# Default preferences
DEFAULT_PREFERENCES = {
    "theme": "System",
    "copy_format_group_order": [
        "Siemens PLC",
        "Allen-Bradley PLC",
        "Mitsubishi PLC",
        "FANUC Robot",
        "Python",
        "C / C++",
        "Java",
        "JavaScript",
        "Generic Text",
        "User Custom",
    ],
    "enabled_copy_format_groups": [
        "Siemens PLC",
        "Allen-Bradley PLC",
        "Mitsubishi PLC",
        "FANUC Robot",
        "Python",
        "C / C++",
        "Java",
        "JavaScript",
        "Generic Text",
    ],
    "copy_format_groups": DEFAULT_COPY_FORMAT_GROUPS,
    "header_tool_by_tool": {},
}

COPY_FORMATS: OrderedDict[str, tuple[str | None, str | None]] = OrderedDict()

# ------------------------------------------------------------------------------
# Get the user-writable DDay Controls configuration folder
def app_config_dir() -> str:
    """Return the user-writable config folder for DDay Controls tools."""
    if platform.system() == "Windows":
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, COMPANY_NAME)
    return os.path.join(os.path.expanduser("~"), ".dday_controls")

# ------------------------------------------------------------------------------
# Get the shared preferences JSON file path
def preferences_path() -> str:
    """Return the shared preferences JSON file path."""
    return os.path.join(app_config_dir(), "converter_preferences.json")

# ------------------------------------------------------------------------------
# Build a fresh default preferences dict from the defaults
def _default_preferences(base: dict) -> dict:
    groups = copy_format_groups_with_user_group(DEFAULT_COPY_FORMAT_GROUPS)
    group_order = copy_format_group_order(groups, base)
    enabled = [name for name in group_order if name in DEFAULT_COPY_FORMAT_GROUPS]
    base["copy_format_groups"] = groups
    base["copy_format_group_order"] = group_order
    base["enabled_copy_format_groups"] = enabled
    base["copy_formats"] = build_copy_formats_from_groups(groups, enabled)
    base["header_tool_by_tool"] = {}
    return base

# ------------------------------------------------------------------------------
# Load shared application preferences from AppData
def load_preferences() -> dict:
    """Load all user preferences from AppData."""
    preferences = dict(DEFAULT_PREFERENCES)
    path = preferences_path()

    if not os.path.exists(path):
        return _default_preferences(preferences)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        theme = data.get("theme", "System")
        if theme not in ("System", "Light", "Dark"):
            theme = "System"

        groups = data.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS)
        enabled_groups = data.get(
            "enabled_copy_format_groups",
            list(DEFAULT_COPY_FORMAT_GROUPS.keys()),
        )

        # Backward compatibility for old flat-only preference files.
        if "copy_format_groups" not in data and "copy_formats" in data:
            groups = OrderedDict(DEFAULT_COPY_FORMAT_GROUPS)
            groups["User Custom"] = [
                {
                    "name": str(item.get("name", "")).strip(),
                    "prefix": str(item.get("prefix", "")),
                    "suffix": str(item.get("suffix", "")),
                }
                for item in data.get("copy_formats", [])
                if str(item.get("name", "")).strip() not in ("", "None", "Custom")
            ]
            enabled_groups = list(DEFAULT_COPY_FORMAT_GROUPS.keys()) + ["User Custom"]

        groups = copy_format_groups_with_user_group(groups)
        preferences["theme"] = theme
        preferences["copy_format_groups"] = groups
        preferences["copy_format_group_order"] = copy_format_group_order(groups, data)
        preferences["enabled_copy_format_groups"] = [
            name
            for name in preferences["copy_format_group_order"]
            if name in enabled_groups
        ]
        preferences["copy_formats"] = build_copy_formats_from_groups(
            groups,
            preferences["enabled_copy_format_groups"],
        )
        preferences["header_tool_by_tool"] = data.get("header_tool_by_tool", {})
        # Backward compatibility for the original comment-tool key.
        if "io_comment_tool" in preferences["header_tool_by_tool"] and "fanuc_io_tool" not in preferences["header_tool_by_tool"]:
            preferences["header_tool_by_tool"]["fanuc_io_tool"] = preferences["header_tool_by_tool"].pop("io_comment_tool")
        for key, value in list(preferences["header_tool_by_tool"].items()):
            if value == "io_comment_tool":
                preferences["header_tool_by_tool"][key] = "fanuc_io_tool"

        return preferences

    except Exception:
        return _default_preferences(preferences)

# ------------------------------------------------------------------------------
# Save shared application preferences to AppData
def save_preferences(preferences: dict) -> None:
    """Save all user preferences to AppData."""
    os.makedirs(app_config_dir(), exist_ok=True)

    groups = copy_format_groups_with_user_group(preferences.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS))
    group_order = copy_format_group_order(groups, preferences)
    enabled_groups = [
        name
        for name in group_order
        if name in preferences.get("enabled_copy_format_groups", list(DEFAULT_COPY_FORMAT_GROUPS.keys()))
    ]

    active_formats = build_copy_formats_from_groups(groups, enabled_groups)

    data = {
        "theme": preferences.get("theme", "System"),
        "copy_format_group_order": group_order,
        "enabled_copy_format_groups": enabled_groups,
        "copy_format_groups": groups,

        "header_tool_by_tool": preferences.get("header_tool_by_tool", {}),

        # Compatibility/export view only. The grouped list above is the source of truth.
        "copy_formats": [
            {
                "name": name,
                "prefix": "" if prefix is None else prefix,
                "suffix": "" if suffix is None else suffix,
            }
            for name, (prefix, suffix) in active_formats.items()
        ],
    }

    with open(preferences_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


PREFERENCES = load_preferences()
rebuild_global_copy_formats()

# ------------------------------------------------------------------------------
# Get saved theme preference
def get_saved_theme_pref() -> str:
    """Return saved theme preference: System, Light, or Dark."""
    return PREFERENCES.get("theme", "System")

# ------------------------------------------------------------------------------
# Resolve System theme preference to Light or Dark
def resolve_theme(theme_pref: str) -> str:
    """Resolve System theme preference to an actual Light/Dark theme."""
    return get_windows_app_theme() if theme_pref == "System" else theme_pref

# ------------------------------------------------------------------------------
# Save selected theme preference
def set_saved_theme_pref(theme_pref: str) -> None:
    """Save selected theme preference."""
    PREFERENCES["theme"] = theme_pref
    save_preferences(PREFERENCES)


# Unit conversion lookup mapping tables (Area, Length, etc.)
UNIT_CONVERSIONS: OrderedDict[str, OrderedDict[str, float]] = OrderedDict({
    "Length": OrderedDict({
        "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
        "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344}
    ),

    "Speed": OrderedDict({
        "mm/s": 0.001, "mm/min": 0.0000166666666666667, "m/s": 1.0, "m/min": 0.0166666666666667, "kph": 0.277777777777778,
        "in/s": 0.0254, "in/min": 0.000423333333333333, "ft/s": 0.3048, "ft/min": 0.00508, "mph": 0.44704}
    ),

    "Pressure": OrderedDict({
        "psi": 6894.757293168, "bar": 100000.0, "mbar": 100.0,
        "kPa": 1000.0, "MPa": 1000000.0, "Pa": 1.0,
        "atm": 101325.0, "inHg": 3386.389, "mmHg": 133.322387415}
    ),

    "Torque": OrderedDict({"N*m": 1.0, "N*cm": 0.01, "lbf*in": 0.1129848290276167, "lbf*ft": 1.3558179483314004, "ozf*in": 0.007061551814226}
    ),

    "Force": OrderedDict({"N": 1.0, "kN": 1000.0, "lbf": 4.4482216152605, "kgf": 9.80665, "ozf": 0.278013850953781}),
    "Mass": OrderedDict({"mg": 0.000001, "g": 0.001, "kg": 1.0, "oz": 0.028349523125, "lb": 0.45359237}),
    "Temperature": OrderedDict({"deg F": 1.0, "deg C": 1.0, "K": 1.0}),
    "Volume": OrderedDict({"mL": 0.001, "L": 1.0, "cm^3": 0.001, "in^3": 0.016387064, "ft^3": 28.316846592, "gal US": 3.785411784}),
    "Area": OrderedDict({"mm^2": 0.000001, "cm^2": 0.0001, "m^2": 1.0, "in^2": 0.00064516, "ft^2": 0.09290304, "acre": 4046.8564224}),
})

# Mapping table providing short names for non-printable ASCII control characters
ASCII_NAMES = {
    0: "NUL", 1: "SOH", 2: "STX", 3: "ETX", 4: "EOT", 5: "ENQ", 6: "ACK", 7: "BEL",
    8: "BS", 9: "TAB", 10: "LF", 11: "VT", 12: "FF", 13: "CR", 14: "SO", 15: "SI",
    16: "DLE", 17: "DC1", 18: "DC2", 19: "DC3", 20: "DC4", 21: "NAK", 22: "SYN", 23: "ETB",
    24: "CAN", 25: "EM", 26: "SUB", 27: "ESC", 28: "FS", 29: "GS", 30: "RS", 31: "US", 127: "DEL",
}

# ------------------------------------------------------------------------------
# Get the focused QLineEdit when it is usable for the requested action
def focused_line_edit(allow_read_only: bool = False) -> QLineEdit | None:
    widget = QApplication.focusWidget()

    if isinstance(widget, QLineEdit):
        if allow_read_only or not widget.isReadOnly():
            return widget

    return None
    
# ------------------------------------------------------------------------------
# Raise an existing Windows top-level window by exact title
def raise_existing_window_by_title(window_title: str) -> bool:
    """Return True if an existing window was found and raised."""
    if platform.system() != "Windows":
        return False

    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, window_title)

    if not hwnd:
        return False

    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    return True


# ******************************************************************************
#
# UI HELPER FUNCTIONS
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Build shared logo, title, subtitle, and optional action button header
def build_header(
    title_text: str,
    subtitle_text: str,
    button_text: str | None = None,
    button_callback=None,
    logo_size: int = 48,
    logo_file: str | None = None,
) -> QHBoxLayout:
    """Build a standard DDay Controls header row.

    logo_file defaults to the shared converter header logo. Individual tools can
    pass a different PNG, such as DDay_FANUC_Suite_Icon.png, while keeping the same layout.
    """

    header = QHBoxLayout()

    logo = QLabel()
    pix = QPixmap(resource_path(logo_file or ICON_PNG))
    if not pix.isNull():
        logo.setPixmap(
            pix.scaled(
                logo_size,
                logo_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    logo.setFixedSize(logo_size + 6, logo_size + 6)
    header.addWidget(logo)

    title_col = QVBoxLayout()
    title_col.setSpacing(2)

    title = QLabel(title_text)
    title.setObjectName("AppTitle" if logo_size >= 48 else "DialogTitle")

    subtitle = QLabel(subtitle_text)
    subtitle.setObjectName("SubTitle")

    title_col.addWidget(title)
    title_col.addWidget(subtitle)

    header.addLayout(title_col)
    header.addStretch(1)

    if button_text and button_callback is not None:
        button = QPushButton(button_text)
        button.setObjectName("HeaderToolButton")
        button.setProperty("headerToolButton", True)
        button.setMinimumWidth(110)
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        button.clicked.connect(button_callback)
        header.addWidget(button)

    return header

# ------------------------------------------------------------------------------
# Create a standard right-aligned form label
def form_label(text: str, width: int = 80) -> QLabel:
    """Create a right-aligned fixed-width label for form/grid rows."""
    lbl = QLabel(f"{text}:")
    lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    lbl.setFixedWidth(width)
    return lbl

# ------------------------------------------------------------------------------
# Refresh a widget after dynamic property or style changes
def refresh_widget_style(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

# ------------------------------------------------------------------------------
# Apply locked-display styling to a disabled button
def lock_button_display(button: QPushButton, tooltip: str = "") -> None:
    """Disable a button and apply the shared locked-display visual state."""
    button.setEnabled(False)
    button.setProperty("lockedDisplay", True)
    if tooltip:
        button.setToolTip(tooltip)
    refresh_widget_style(button)

# ------------------------------------------------------------------------------
# Tool director registry used by all DDay Controls tools
TOOL_REGISTRY = OrderedDict({
    "conversion_tool": {
        "display_name": "Conversion Tool",
        "window_title": "DDay Controls Conversion Tool",
        "exe_name": "DDay Controls Conversion Tool.exe",
        "py_name": "converter_tool.py",
        "module_name": "converter_tool",
        "class_name": "ConversionTool",
        "icon_png": "DDay_Converter.png",
    },
    "ascii_chart": {
        "display_name": "ASCII Chart",
        "window_title": "DDay Controls ASCII Chart",
        "exe_name": "DDay Controls ASCII Chart.exe",
        "py_name": "ascii_chart.py",
        "module_name": "ascii_chart",
        "class_name": "AsciiDialog",
        "icon_png": "DDay_ASCII_Chart.png",
    },
    "fanuc_io_tool": {
        "display_name": "FANUC I/O Tool",
        "window_title": "DDay Controls FANUC I/O Tool",
        "exe_name": "DDay Controls FANUC IO Tool.exe",
        "py_name": "fanuc_io_tool.py",
        "module_name": "fanuc_io_tool",
        "class_name": "FanucIOTool",
        "icon_png": "DDay_FANUC_Suite_Icon.png",
    },
})

OPEN_TOOL_WINDOWS: dict[str, QWidget] = {}

# ------------------------------------------------------------------------------
# Return the folder used to locate companion tools
def tool_runtime_dir() -> str:
    """Return EXE folder in packaged mode or source folder in dev mode."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------------------
# Return full path for a registered tool file
def tool_file_path(tool_key: str, file_kind: str) -> str:
    """Return the path to a registered tool exe_name or py_name."""
    tool = TOOL_REGISTRY[tool_key]
    return os.path.join(tool_runtime_dir(), tool[file_kind])

# ------------------------------------------------------------------------------
# Return whether a registered tool is available
def tool_available(tool_key: str) -> bool:
    """Return True when the registered tool is available to launch."""
    if tool_key not in TOOL_REGISTRY:
        return False

    if getattr(sys, "frozen", False):
        return os.path.exists(tool_file_path(tool_key, "exe_name"))

    return os.path.exists(tool_file_path(tool_key, "py_name"))

# ------------------------------------------------------------------------------
# Register an open tool window with the common director
def register_tool_window(tool_key: str, window: QWidget) -> None:
    """Register an open tool window so other tools can raise it instead of duplicating it."""
    if tool_key in TOOL_REGISTRY:
        OPEN_TOOL_WINDOWS[tool_key] = window

# ------------------------------------------------------------------------------
# Return available tool keys sorted by display name
def available_tool_keys(current_tool_key: str | None = None) -> list[str]:
    """Return available registered tools, excluding the current tool, sorted alphabetically."""
    keys = [
        tool_key
        for tool_key in TOOL_REGISTRY
        if tool_key != current_tool_key and tool_available(tool_key)
    ]
    return sorted(keys, key=lambda key: TOOL_REGISTRY[key]["display_name"].lower())

# ------------------------------------------------------------------------------
# Return the first available companion tool key
def first_available_tool_key(current_tool_key: str | None = None) -> str | None:
    """Return the first alphabetically available tool other than the current one."""
    keys = available_tool_keys(current_tool_key)
    return keys[0] if keys else None

# ------------------------------------------------------------------------------
# Return display text for a registered tool
def tool_display_name(tool_key: str) -> str:
    """Return the menu/header display name for a registered tool."""
    return TOOL_REGISTRY[tool_key]["display_name"]

# ------------------------------------------------------------------------------
# Open, raise, or launch a registered tool
def open_registered_tool(owner, tool_key: str):
    """Open, raise, or launch a registered DDay Controls tool without cross-importing launchers."""
    if tool_key not in TOOL_REGISTRY:
        update_owner_status(owner, f"Unknown tool: {tool_key}")
        return None

    existing = OPEN_TOOL_WINDOWS.get(tool_key)
    if existing is not None:
        try:
            show_raise_activate(existing)
            return existing
        except RuntimeError:
            OPEN_TOOL_WINDOWS.pop(tool_key, None)

    tool = TOOL_REGISTRY[tool_key]

    if getattr(sys, "frozen", False):
        if raise_existing_window_by_title(tool.get("window_title", tool["display_name"])):
            return None
    
        exe_path = tool_file_path(tool_key, "exe_name")
        if os.path.exists(exe_path):
            subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
        else:
            update_owner_status(owner, f"{tool['display_name']} is not installed.")
        return None

    py_path = tool_file_path(tool_key, "py_name")
    if not os.path.exists(py_path):
        update_owner_status(owner, f"{tool['display_name']} source file was not found.")
        return None

    module = importlib.import_module(tool["module_name"])
    window_class = getattr(module, tool["class_name"])
    window = window_class()
    register_tool_window(tool_key, window)
    show_raise_activate(window)
    return window

# ------------------------------------------------------------------------------
# Add all available companion tools to a Tools menu
def add_available_tool_actions(tools_menu, owner, current_tool_key: str | None = None) -> int:
    """Add installed companion tools to a Tools menu and return the number added."""
    added = 0

    for tool_key in available_tool_keys(current_tool_key):
        tool = TOOL_REGISTRY[tool_key]

        action = QAction(tool["display_name"], owner)
        action.triggered.connect(lambda _=False, key=tool_key: open_registered_tool(owner, key))
        tools_menu.addAction(action)
        added += 1

    return added

# ------------------------------------------------------------------------------
# Return saved header button target for this tool
def header_tool_key_for(current_tool_key: str | None = None) -> str | None:
    """Return configured header-button tool key, falling back to the first available tool."""
    if current_tool_key is None:
        return first_available_tool_key(current_tool_key)

    saved = PREFERENCES.get("header_tool_by_tool", {}).get(current_tool_key)
    if saved and saved != current_tool_key and tool_available(saved):
        return saved

    return first_available_tool_key(current_tool_key)

# ------------------------------------------------------------------------------
# Save header button target for this tool
def set_header_tool_key_for(current_tool_key: str, target_tool_key: str) -> None:
    """Save the header-button tool target for a specific DDay Controls tool."""
    if "header_tool_by_tool" not in PREFERENCES:
        PREFERENCES["header_tool_by_tool"] = {}

    PREFERENCES["header_tool_by_tool"][current_tool_key] = target_tool_key
    save_preferences(PREFERENCES)

# ------------------------------------------------------------------------------
# Return header button text and callback for the configured companion tool
def companion_header_button(owner, current_tool_key: str | None = None):
    """Return button text/callback for the configured companion tool."""
    tool_key = header_tool_key_for(current_tool_key)
    if tool_key is None:
        return None, None

    return tool_display_name(tool_key), (lambda _=False, key=tool_key: open_registered_tool(owner, key))

# ------------------------------------------------------------------------------
# Refresh an existing standard header tool button
def refresh_header_tool_button(owner, current_tool_key: str | None = None) -> None:
    """Refresh the shared header companion-tool button after preference changes."""
    button = owner.findChild(QPushButton, "HeaderToolButton")
    if button is None:
        return

    text, callback = companion_header_button(owner, current_tool_key)
    if text is None or callback is None:
        button.hide()
        return

    button.show()
    button.setText(text)
    try:
        button.clicked.disconnect()
    except Exception:
        pass
    button.clicked.connect(callback)

# ------------------------------------------------------------------------------
# Add menu action to choose which tool appears on the header button
def add_header_tool_selector_action(tools_menu, owner, current_tool_key: str | None = None) -> None:
    """Add a Tools menu action for selecting the shared header-button target."""
    action = QAction("Set Header Button...", owner)

    def choose_header_tool() -> None:
        keys = available_tool_keys(current_tool_key)
        if not keys:
            QMessageBox.information(owner, "Header Button", "No companion tools are available.")
            return

        dialog = QDialog(owner)
        dialog.setWindowTitle("Set Header Button")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Select the tool assigned to the header button:"))

        combo = QComboBox()
        for key in keys:
            combo.addItem(tool_display_name(key), key)

        current = header_tool_key_for(current_tool_key)
        if current in keys:
            combo.setCurrentIndex(keys.index(current))

        layout.addWidget(combo)

        row = QHBoxLayout()
        row.addStretch(1)
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        row.addWidget(ok)
        row.addWidget(cancel)
        layout.addLayout(row)

        ok.clicked.connect(dialog.accept)
        cancel.clicked.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return

        selected_key = combo.currentData()
        if current_tool_key is not None and selected_key:
            set_header_tool_key_for(current_tool_key, selected_key)
            refresh_header_tool_button(owner, current_tool_key)
            update_owner_status(owner, f"Header button set to {tool_display_name(selected_key)}.")

    action.triggered.connect(choose_header_tool)
    tools_menu.addAction(action)
    
# ------------------------------------------------------------------------------
# Create a standard QLineEdit field
def make_entry(read_only: bool = False) -> QLineEdit:
    """Create a standard QLineEdit field."""
    edit = QLineEdit()
    edit.setReadOnly(read_only)
    return edit

# ------------------------------------------------------------------------------
# Clear a list of line-edit fields
def clear_line_edits(fields: list[QLineEdit]) -> None:
    """Clear all QLineEdit fields in the supplied list."""
    for field in fields:
        field.clear()


# ------------------------------------------------------------------------------
# Preserve and refresh combo-box values
def replace_combo_items_preserve(combo: QComboBox, items: list[str], default_index: int = 0) -> None:
    """Replace combo-box items while preserving current text when possible."""
    current = combo.currentText()

    combo.blockSignals(True)
    combo.clear()
    combo.addItems(items)

    if current in items:
        combo.setCurrentText(current)
    elif items:
        combo.setCurrentIndex(min(default_index, len(items) - 1))

    combo.blockSignals(False)


# ------------------------------------------------------------------------------
# Synchronize a checkbox to a checkable action without signal feedback
def set_checkable_state_silent(widget, checked: bool) -> None:
    """Set checked state on a checkbox/action without emitting its signals."""
    widget.blockSignals(True)
    widget.setChecked(checked)
    widget.blockSignals(False)


# ------------------------------------------------------------------------------
# Show, raise, and activate a window
def show_raise_activate(window: QWidget) -> None:
    """Show a window and bring it to the foreground."""
    window.show()
    window.raise_()
    window.activateWindow()


# ------------------------------------------------------------------------------
# Add labeled entry row with optional copy button
def add_labeled_entry_row(
    owner,
    parent: QGridLayout,
    row: int,
    label: str,
    edit: QLineEdit,
    copy_name: str | None = None,
    copy_transform=None,
    label_width: int | None = None,
) -> None:
    """Add a standard form row with an optional copy button."""
    parent.addWidget(form_label(label, label_width or 80), row, 0)
    parent.addWidget(edit, row, 1)

    if copy_name:
        btn = QPushButton("Copy")
        btn.setFixedWidth(COPY_BUTTON_WIDTH)
        btn.clicked.connect(
            lambda _=False, e=edit: copy_to_clipboard(
                owner,
                copy_transform(e.text()) if copy_transform is not None else e.text(),
            )
        )
        parent.addWidget(btn, row, 2)


# ------------------------------------------------------------------------------
# Apply selected copy-format prefix and suffix state
def apply_copy_format_state(combo: QComboBox, prefix_box: QLineEdit, suffix_box: QLineEdit) -> None:
    selected = combo.currentText()
    prefix, suffix = COPY_FORMATS.get(selected, ("", ""))
    custom = selected == "Custom"

    if not custom:
        prefix_box.setText(prefix)
        suffix_box.setText(suffix)

    prefix_box.setReadOnly(not custom)
    suffix_box.setReadOnly(not custom)

    for box in (prefix_box, suffix_box):
        box.setProperty("lockedDisplay", not custom)
        refresh_widget_style(box)

# ------------------------------------------------------------------------------
# Format a value using selected copy-format controls
def format_copy_value(value: str, combo: QComboBox, prefix_box: QLineEdit, suffix_box: QLineEdit) -> str:
    """Return value with the selected copy-format prefix and suffix applied."""
    selected = combo.currentText()

    if selected == "Custom":
        prefix = prefix_box.text()
        suffix = suffix_box.text()
    else:
        prefix, suffix = COPY_FORMATS.get(selected, ("", ""))

    return f"{prefix}{value}{suffix}"

# ------------------------------------------------------------------------------
# Copy text to clipboard and show consistent status text
def copy_to_clipboard(owner, value: str) -> None:
    """Copy text to clipboard and show a consistent copied status."""
    QApplication.clipboard().setText(value)
    update_owner_status(owner, f"Copied: {value}")

# ------------------------------------------------------------------------------
# Get text from the currently selected table cell
def selected_table_cell_text(table: QTableWidget) -> str | None:
    row = table.currentRow()
    col = table.currentColumn()

    if row < 0 or col < 0:
        return None

    item = table.item(row, col)
    return item.text() if item is not None else None


# ------------------------------------------------------------------------------
# Return whether the table has a current selected cell
def table_has_current_cell(table: QTableWidget) -> bool:
    """Return True when a table has a current row and column selected."""
    return table.currentRow() >= 0 and table.currentColumn() >= 0


# ------------------------------------------------------------------------------
# Return whether a focused table cell is available for copy
def table_cell_copy_available(table: QTableWidget) -> bool:
    """Return True when the focused widget is a table with a selected cell."""
    return QApplication.focusWidget() is table and table_has_current_cell(table)


# ------------------------------------------------------------------------------
# Copy the currently selected table cell without formatting
def copy_table_cell_raw(owner, table: QTableWidget) -> None:
    """Copy the selected table cell exactly as displayed."""
    value = selected_table_cell_text(table)
    if value is not None:
        copy_to_clipboard(owner, value)


# ------------------------------------------------------------------------------
# Copy the currently selected table cell with prefix and suffix formatting
def copy_table_cell_formatted(
    owner,
    table: QTableWidget,
    combo: QComboBox,
    prefix_box: QLineEdit,
    suffix_box: QLineEdit,
) -> None:
    """Copy the selected table cell with the selected copy-format applied."""
    value = selected_table_cell_text(table)
    if value is not None:
        copy_to_clipboard(owner, format_copy_value(value, combo, prefix_box, suffix_box))


# ------------------------------------------------------------------------------
# Copy a table cell from the current row and requested column
def copy_table_current_row_column(
    owner,
    table: QTableWidget,
    column: int,
    formatted: bool = False,
    combo: QComboBox | None = None,
    prefix_box: QLineEdit | None = None,
    suffix_box: QLineEdit | None = None,
) -> None:
    """Select and copy a table value from the current row and requested column."""
    row = table.currentRow()

    if row < 0:
        return

    table.setCurrentCell(row, column)

    if formatted:
        if combo is None or prefix_box is None or suffix_box is None:
            return

        copy_table_cell_formatted(owner, table, combo, prefix_box, suffix_box)
    else:
        copy_table_cell_raw(owner, table)


# ------------------------------------------------------------------------------
# Backward-compatible alias for raw table-cell copy
def copy_table_cell(owner, table: QTableWidget) -> None:
    """Copy the selected table cell exactly as displayed."""
    copy_table_cell_raw(owner, table)

# ------------------------------------------------------------------------------
# Connect copy-format controls and initialize prefix/suffix fields
def connect_copy_format_controls(combo: QComboBox, prefix_box: QLineEdit, suffix_box: QLineEdit) -> None:
    combo.currentTextChanged.connect(lambda: apply_copy_format_state(combo, prefix_box, suffix_box))
    apply_copy_format_state(combo, prefix_box, suffix_box)

# ------------------------------------------------------------------------------
# Add a standard status bar to a dialog-style window
def add_dialog_status_bar(layout: QVBoxLayout, owner, initial: str = "Ready.") -> QLabel:
    """Add a standard DDay Controls status bar to a dialog layout and return its status label."""
    status_bar = QStatusBar()
    status_label = QLabel(initial)
    version_label = QLabel(f"{COMPANY_NAME}  |  {APP_VERSION}")

    status_bar.addWidget(status_label, 1)
    status_bar.addPermanentWidget(version_label)

    owner.status_bar = status_bar
    owner.status = status_label
    owner.version_label = version_label

    layout.addWidget(status_bar)
    return status_label

# ------------------------------------------------------------------------------
# Update owner status label when a supported status target exists
def update_owner_status(owner, message: str) -> None:
    if hasattr(owner, "set_status"):
        owner.set_status(message)
    elif hasattr(owner, "dialog_status"):
        owner.dialog_status.setText(message)
    elif hasattr(owner, "status") and hasattr(owner.status, "setText"):
        owner.status.setText(message)
    elif hasattr(owner, "status_label") and hasattr(owner.status_label, "setText"):
        owner.status_label.setText(message)

# ------------------------------------------------------------------------------
# Refresh copy-format controls on a window when supported
def refresh_owner_copy_formats(owner) -> None:
    """Refresh copy-format controls on a window when the window supports it."""
    if hasattr(owner, "refresh_copy_format_options"):
        owner.refresh_copy_format_options()

# ------------------------------------------------------------------------------
# Refresh related windows after copy-format preference changes
def notify_copy_formats_updated(owner) -> None:
    """Refresh copy-format controls and status text across related windows."""
    refresh_owner_copy_formats(owner)
    update_owner_status(owner, "Copy formats updated.")

    ascii_dialog = getattr(owner, "ascii_dialog", None)
    if ascii_dialog is not None:
        refresh_owner_copy_formats(ascii_dialog)
        update_owner_status(ascii_dialog, "Copy formats updated.")

    parent_tool = getattr(owner, "parent_tool", None)
    if parent_tool is not None:
        refresh_owner_copy_formats(parent_tool)
        update_owner_status(parent_tool, "Copy formats updated.")

# ------------------------------------------------------------------------------
# Open the shared copy-format editor
def edit_copy_formats(parent: QWidget | None = None) -> bool:
    global COPY_FORMATS
    from copy_format_editor import CopyFormatEditorDialog

    dialog = CopyFormatEditorDialog(parent)
    if dialog.exec() != QDialog.Accepted:
        return False

    rebuild_global_copy_formats()
    save_preferences(PREFERENCES)
    return True

# ------------------------------------------------------------------------------
# Refresh a copy-format combo while preserving current selection
def refresh_copy_format_combo(combo: QComboBox, prefix_box: QLineEdit, suffix_box: QLineEdit) -> None:
    current = combo.currentText()
    combo.blockSignals(True)
    combo.clear()
    combo.addItems(list(COPY_FORMATS.keys()))
    combo.setCurrentText(current if current in COPY_FORMATS else "None")
    combo.blockSignals(False)
    apply_copy_format_state(combo, prefix_box, suffix_box)

# ------------------------------------------------------------------------------
# Add the shared File menu
def add_file_menu(menu_bar: QMenuBar, owner) -> None:
    """Add a shared File menu."""

    file_menu = menu_bar.addMenu("File")

    exit_action = QAction("Exit", owner)
    exit_action.triggered.connect(owner.close)
    file_menu.addAction(exit_action)

# ------------------------------------------------------------------------------
# Add the shared Edit menu
def add_edit_menu(menu_bar: QMenuBar, owner, copy_callback=None, copy_available=None,
    copy_formatted_callback=None, copy_formatted_available=None,
    ) -> None:
    """Add a shared Edit menu for focused editable fields."""

    # ------------------------------------------------------------------------------
    # Refresh enabled state for Edit menu actions before display
    def refresh_edit_menu_state() -> None:
        editable = focused_line_edit()
        copyable = focused_line_edit(allow_read_only=True)

        cut_action.setEnabled(editable is not None)
        paste_action.setEnabled(editable is not None)
        clear_action.setEnabled(editable is not None)
        select_all_action.setEnabled(copyable is not None)
        copy_action.setEnabled(
            copyable is not None or
            (copy_available is not None and copy_available())
        )

        if copy_formatted_callback is None:
            copy_formatted_action.setEnabled(False)
        elif copy_formatted_available is not None:
            copy_formatted_action.setEnabled(copy_formatted_available())
        else:
            copy_formatted_action.setEnabled(True)

    # ------------------------------------------------------------------------------
    # Cut text from the focused editable field
    def run_cut() -> None:
        edit = focused_line_edit()
        if edit is not None:
            edit.cut()

    # ------------------------------------------------------------------------------
    # Copy focused text or owner-specific selected content
    def run_copy() -> None:
        if copy_callback is not None and (copy_available is None or copy_available()):
            copy_callback()
            return

        edit = focused_line_edit(allow_read_only=True)
        if edit is not None:
            copied = edit.selectedText() or edit.text()
            copy_to_clipboard(owner, copied)

    # ------------------------------------------------------------------------------
    # Paste clipboard text into the focused editable field
    def run_paste() -> None:
        edit = focused_line_edit()
        if edit is not None:
            edit.paste()

    # ------------------------------------------------------------------------------
    # Select all text in the focused editable field
    def run_select_all() -> None:
        edit = focused_line_edit()
        if edit is not None:
            edit.selectAll()

    # ------------------------------------------------------------------------------
    # Clear text from the focused editable field
    def run_clear_selected() -> None:
        edit = focused_line_edit()
        if edit is not None:
            edit.clear()

            update_owner_status(owner, "Selected field cleared.")

    edit_menu = menu_bar.addMenu("Edit")

    cut_action = QAction("Cut          ", owner)
    cut_action.setShortcut("Ctrl+X")
    cut_action.triggered.connect(run_cut)
    edit_menu.addAction(cut_action)

    copy_action = QAction("Copy          ", owner)
    copy_action.setShortcut("Ctrl+C")
    copy_action.triggered.connect(run_copy)
    edit_menu.addAction(copy_action)

    copy_formatted_action = QAction("Copy Formatted", owner)
    copy_formatted_action.setShortcut("Ctrl+Shift+C")
    if copy_formatted_callback is not None:
        copy_formatted_action.triggered.connect(copy_formatted_callback)
    edit_menu.addAction(copy_formatted_action)

    paste_action = QAction("Paste          ", owner)
    paste_action.setShortcut("Ctrl+V")
    paste_action.triggered.connect(run_paste)
    edit_menu.addAction(paste_action)

    select_all_action = QAction("Select All          ", owner)
    select_all_action.setShortcut("Ctrl+A")
    select_all_action.triggered.connect(run_select_all)
    edit_menu.addAction(select_all_action)

    edit_menu.addSeparator()

    clear_action = QAction("Clear Selected Field          ", owner)
    clear_action.setShortcut("Ctrl+L")
    clear_action.triggered.connect(run_clear_selected)
    edit_menu.addAction(clear_action)

    edit_menu.aboutToShow.connect(refresh_edit_menu_state)

# ------------------------------------------------------------------------------
# Add the shared Theme submenu to an existing menu
def add_theme_submenu(parent_menu, owner, on_theme_changed=None) -> None:
    """Add the shared Theme submenu to an existing menu."""

    # ------------------------------------------------------------------------------
    # Apply selected theme preference and refresh open windows
    def apply_selected_theme(theme_pref: str) -> None:
        set_saved_theme_pref(theme_pref)
        theme_name = resolve_theme(theme_pref)

        if hasattr(owner, "theme_name"):
            owner.theme_name = theme_name

        if hasattr(owner, "ascii_dialog") and owner.ascii_dialog is not None:
            owner.ascii_dialog.theme_name = theme_name
            owner.ascii_dialog.populate()

        apply_app_theme(theme_name)

        if on_theme_changed is not None:
            on_theme_changed()

    theme_menu = parent_menu.addMenu("Theme")
    theme_group = QActionGroup(owner)
    theme_group.setExclusive(True)

    current_pref = get_saved_theme_pref()

    for label in ("System", "Light", "Dark"):
        action = QAction(label, owner)
        action.setCheckable(True)
        action.setChecked(current_pref == label)
        action.triggered.connect(lambda checked=False, pref=label: apply_selected_theme(pref))
        theme_group.addAction(action)
        theme_menu.addAction(action)

# ------------------------------------------------------------------------------
# Add the shared Edit Copy Formats action to a Tools menu
def add_copy_format_editor_action(tools_menu, owner) -> None:
    """Add the shared Edit Copy Formats action to a Tools menu."""

    # ------------------------------------------------------------------------------
    # Open copy-format editor and refresh affected windows
    def run_editor() -> None:
        if edit_copy_formats(owner):
            notify_copy_formats_updated(owner)

    action = QAction("Edit Copy Formats...", owner)
    action.triggered.connect(run_editor)
    tools_menu.addAction(action)

# ------------------------------------------------------------------------------
# Open the shared copy-format group manager
def customize_copy_format_groups(parent: QWidget | None = None) -> bool:
    """Open the shared copy-format group manager."""
    from copy_format_editor import CopyFormatGroupManagerDialog

    dialog = CopyFormatGroupManagerDialog(parent)
    if dialog.exec() != QDialog.Accepted:
        return False

    rebuild_global_copy_formats()
    save_preferences(PREFERENCES)
    return True


# ------------------------------------------------------------------------------
# Add the shared Customize Copy Format Groups action to a menu
def add_copy_format_group_manager_action(tools_menu, owner) -> None:
    """Add the shared Customize Copy Format Groups action to a menu."""

    # ------------------------------------------------------------------------------
    # Open group manager and refresh affected windows
    def run_group_manager() -> None:
        if customize_copy_format_groups(owner):
            notify_copy_formats_updated(owner)

    action = QAction("Manage Copy Formats...", owner)
    action.triggered.connect(run_group_manager)
    tools_menu.addAction(action)


# ------------------------------------------------------------------------------
# Open the shared copy-format group item editor
def edit_copy_format_group_items(parent: QWidget | None = None) -> bool:
    """Open the shared editor for copy-format items inside a selected group."""
    from copy_format_editor import CopyFormatGroupItemEditorDialog

    dialog = CopyFormatGroupItemEditorDialog(parent)
    if dialog.exec() != QDialog.Accepted:
        return False

    rebuild_global_copy_formats()
    save_preferences(PREFERENCES)
    return True


# ------------------------------------------------------------------------------
# Add the shared Edit Group Items action to a menu
def add_copy_format_group_item_editor_action(tools_menu, owner) -> None:
    """Add the shared Edit Group Items action to a menu."""

    # ------------------------------------------------------------------------------
    # Open group item editor and refresh affected windows
    def run_group_item_editor() -> None:
        if edit_copy_format_group_items(owner):
            notify_copy_formats_updated(owner)

    action = QAction("Edit Group Items...", owner)
    action.triggered.connect(run_group_item_editor)
    tools_menu.addAction(action)


# ------------------------------------------------------------------------------
# Add the shared Help menu
def add_help_menu(menu_bar: QMenuBar, owner, app_name: str) -> None:
    """Add a shared Help menu with a standard About dialog."""

    # ------------------------------------------------------------------------------
    # Show the standard About dialog
    def show_about() -> None:
        QMessageBox.information(
            owner,
            "About",
            f"\n{app_name}\n\nVersion: {APP_VERSION}\n\n{COMPANY_NAME}"
        )

    help_menu = menu_bar.addMenu("Help")
    about_action = QAction("About", owner)
    about_action.triggered.connect(show_about)
    help_menu.addAction(about_action)


# ******************************************************************************
#
# SYSTEM & UTILITY HELPERS
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Resolve resource path for local execution or PyInstaller bundle
def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# ------------------------------------------------------------------------------
# Register the Windows AppUserModelID for clean taskbar grouping
def set_windows_app_user_model_id(app_id: str = "DDayControls.ConversionTool.Qt") -> None:
    """Register a Windows AppUserModelID for clean taskbar grouping.

    Pass a different app_id from each standalone launcher so the two packaged
    EXEs can group independently when launched directly, while child windows
    opened from an already-running tool stay grouped with that parent process.
    """
    if platform.system() != "Windows":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

# ------------------------------------------------------------------------------
# Detect the active Windows application theme
def get_windows_app_theme() -> str:
    if platform.system() != "Windows":
        return "Light"
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "Light" if int(value) else "Dark"
    except Exception:
        return "Light"

# ------------------------------------------------------------------------------
# Apply the global Qt stylesheet for the selected theme
def apply_app_theme(theme: str) -> None:
    t = THEMES["Dark" if theme == "Dark" else "Light"]

    qss = f"""
    QMainWindow, QWidget {{background: {t['main_bg']}; color: {t['text']}; font-family: Segoe UI; font-size: 9pt; }}
    QMenuBar, QMenu {{background: {t['panel_bg']}; color: {t['text']}; }}
    QMenuBar::item:selected, QMenu::item:selected {{background: {t['accent']}; }}
    QMenu::item:disabled {{color: {t['disabled_text']}; }}
    QTabWidget::pane {{border: 1px solid {t['border']}; }}
    QGroupBox {{border: 1px solid {t['border']}; margin-top: 12px; padding-top: 10px; }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 4px;
        background: {t['group_title_bg']};
        color: {t['title']};
    }}
    QTabBar::tab {{background: {t['panel_bg']}; color: {t['text']}; border: 1px solid {t['border']}; padding: 6px 12px; }}
    QTabBar::tab:selected {{background: {t['tab_selected']}; font-weight: bold; }}
    QTabBar::tab:!selected {{background: {t['panel_bg']}; }}
    QLineEdit, QComboBox, QTableWidget {{
        background: {t['input_bg']};
        color: {t['text']};
        border: 1px solid {t['border']};
        padding: 3px;
    }}
    QPushButton {{
        background: {t['button_bg']};
        border: 1px solid {t['accent']};
        color: {t['text']};
        padding: 6px 12px;
        min-height: 24px;
    }}
    QPushButton:hover {{background: {t['button_hover']}; }}
    QPushButton:pressed {{background: {t['panel_bg']}; }}
    QToolButton {{
        background: transparent;
        border: 2px solid transparent;
        border-radius: 6px;
        color: {t['text']};
        padding: 8px;
    }}
    QToolButton:hover {{
        background: {t['button_hover']};
        border: 2px solid {t['accent']};
    }}
    QToolButton:pressed {{
        background: {t['button_pressed']};
    }}
    QHeaderView::section {{
        background: {t['table_header']};
        color: {t['text']};
        border: 1px solid {t['border']};
        padding: 4px;
    }}
    QStatusBar {{background: {t['main_bg']}; color: {t['subtitle']}; border-top: 1px solid {t['border']}; }}
    QLabel#AppTitle, QLabel#DialogTitle {{font-size: 16pt; font-weight: bold; color: {t['title']}; }}
    QLabel#SubTitle {{color: {t['subtitle']}; }}
    QTableWidget {{alternate-background-color: {t['table_alt']}; background-color: {t['table_bg']}; }}
    QTableWidget::item:selected {{background: {t['table_selected']}; color: {t['text']}; }}
    QTableWidget::item:selected:active {{background: {t['table_selected_active']}; }}
    QLineEdit[lockedDisplay="true"] {{background: {t['main_bg']}; border: 1px solid {t['main_bg']}; color: {t['locked_text']}; font-weight: bold; }}
    QPushButton[lockedDisplay="true"] {{color: {t['disabled_text']}; font-weight: normal; }}
    """

    QApplication.instance().setStyleSheet(qss)  # type: ignore[union-attr]


# ******************************************************************************
#
# BIT & MATHEMATICAL PROCESSING HELPERS
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Get integer bit width from the selected width label
def get_bit_width(text: str) -> int:
    return {"8-bit": 8, "16-bit": 16, "32-bit": 32}.get(text, 8)

# ------------------------------------------------------------------------------
# Calculate integer range limits for bit width and signed mode
def range_info(bits: int, signed: bool) -> tuple[int, int]:
    return (-(2 ** (bits - 1)), 2 ** (bits - 1) - 1) if signed else (0, 2 ** bits - 1)

# ------------------------------------------------------------------------------
# Convert signed integer value to unsigned bit-mask representation
def unsigned_value(value: int, bits: int) -> int:
    return value if value >= 0 else value + 2 ** bits

# ------------------------------------------------------------------------------
# Parse DEC, HEX, BIN, or OCT input into an integer value
def parse_integer_text(fmt: str, text: str, bits: int, signed: bool) -> int:
    if not text.strip():
        raise ValueError("No value entered.")
    t = text.strip()
    if fmt == "DEC":
        if not re.fullmatch(r"-?\d+", t):
            raise ValueError("DEC must be a whole number.")
        value = int(t)
    elif fmt == "HEX":
        clean = re.sub(r"(?i)0x", "", t)
        clean = re.sub(r"[\s,;:-]", "", clean)
        if not re.fullmatch(r"[0-9A-Fa-f]+", clean):
            raise ValueError("HEX must contain only hex digits.")
        u = int(clean, 16)
        value = u - 2 ** bits if signed and u >= 2 ** (bits - 1) else u
    elif fmt == "BIN":
        clean = re.sub(r"(?i)0b", "", t)
        clean = re.sub(r"[\s,;:-]", "", clean)
        if not re.fullmatch(r"[01]+", clean):
            raise ValueError("BIN must contain only 0 and 1.")
        u = int(clean, 2)
        value = u - 2 ** bits if signed and u >= 2 ** (bits - 1) else u
    elif fmt == "OCT":
        clean = re.sub(r"(?i)0o", "", t)
        if re.search(r"[\s,;:-]", clean):
            tokens = [x for x in re.split(r"[\s,;:-]+", clean) if x]
            if len(tokens) > bits // 8:
                raise ValueError(f"Grouped OCT byte input exceeds {bits}-bit scalar width.")
            u = 0
            for token in tokens:
                if not re.fullmatch(r"[0-7]{1,3}", token):
                    raise ValueError("OCT must contain only octal digits.")
                b = int(token, 8)
                if b > 255:
                    raise ValueError("Each OCT byte group must be 000-377.")
                u = (u << 8) | b
        else:
            if not re.fullmatch(r"[0-7]+", clean):
                raise ValueError("OCT must contain only octal digits.")
            u = int(clean, 8)
        value = u - 2 ** bits if signed and u >= 2 ** (bits - 1) else u
    else:
        raise ValueError("Unknown format.")
    low, high = range_info(bits, signed)
    if value < low or value > high:
        raise ValueError(f"Value out of range for {bits}-bit {'signed' if signed else 'unsigned'}.")
    return value

# ------------------------------------------------------------------------------
# Format an integer value as DEC, HEX, BIN, or OCT text
def format_integer_value(value: int, fmt: str, bits: int) -> str:
    u = unsigned_value(value, bits)
    if fmt == "DEC":
        return str(value)
    if fmt == "HEX":
        return f"{u:0{bits // 4}X}"
    if fmt == "BIN":
        b = f"{u:0{bits}b}"
        return " ".join(b[i:i+8] for i in range(0, len(b), 8)) if bits > 8 else b
    if fmt == "OCT":
        return format(u, "o")
    raise ValueError("Unknown format.")

# ------------------------------------------------------------------------------
# Split an integer value into little-endian and big-endian byte lists
def endian_bytes(value: int, bits: int) -> tuple[list[str], list[str]]:
    u = unsigned_value(value, bits)
    little = [f"{(u >> (8 * i)) & 0xFF:02X}" for i in range(bits // 8)]
    return little, list(reversed(little))


# ******************************************************************************
#
# DATA STREAM & CONVERSION HELPERS
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Convert a byte value to printable ASCII or dot placeholder
def printable_char(byte_value: int) -> str:
    return chr(byte_value) if 32 <= byte_value <= 126 else "."

# ------------------------------------------------------------------------------
# Split messy byte stream text into normalized tokens
def normalize_byte_tokens(text: str) -> list[str]:
    clean = text.strip()
    clean = re.sub(r"(?i)0x", "", clean)
    clean = re.sub(r"(?i)0b", "", clean)
    return [x for x in re.split(r"[,\s;\r\n\t]+", clean) if x]

# ------------------------------------------------------------------------------
# Parse formatted byte stream text into raw bytes
def parse_byte_stream(fmt: str, text: str) -> bytes:
    if fmt == "ASCII":
        return text.encode("ascii", errors="replace")
    out: list[int] = []
    for token in normalize_byte_tokens(text):
        if fmt == "HEX":
            if not re.fullmatch(r"[0-9A-Fa-f]{1,2}", token):
                raise ValueError(f"Invalid HEX token: {token}")
            value = int(token, 16)
        elif fmt == "DEC":
            if not re.fullmatch(r"\d{1,3}", token):
                raise ValueError(f"Invalid DEC token: {token}")
            value = int(token, 10)
        elif fmt == "BIN":
            if not re.fullmatch(r"[01]{1,8}", token):
                raise ValueError(f"Invalid BIN token: {token}")
            value = int(token, 2)
        elif fmt == "OCT":
            if not re.fullmatch(r"[0-7]{1,3}", token):
                raise ValueError(f"Invalid OCT token: {token}")
            value = int(token, 8)
        else:
            raise ValueError("Unknown stream format.")
        if not 0 <= value <= 255:
            raise ValueError(f"{fmt} token out of range: {token}")
        out.append(value)
    return bytes(out)

# ------------------------------------------------------------------------------
# Format raw bytes as ASCII, HEX, DEC, BIN, or OCT text
def format_byte_stream(data: bytes, fmt: str) -> str:
    if fmt == "ASCII":
        return data.decode("ascii", errors="replace")
    if fmt == "HEX":
        return " ".join(f"{b:02X}" for b in data)
    if fmt == "DEC":
        return " ".join(str(b) for b in data)
    if fmt == "BIN":
        return " ".join(f"{b:08b}" for b in data)
    if fmt == "OCT":
        return " ".join(f"{b:03o}" for b in data)
    raise ValueError("Unknown stream format.")

# ------------------------------------------------------------------------------
# Convert temperature values between Fahrenheit, Celsius, and Kelvin
def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == "deg F":
        c = (value - 32.0) * 5.0 / 9.0
    elif from_unit == "deg C":
        c = value
    elif from_unit == "K":
        c = value - 273.15
    else:
        raise ValueError("Unknown temperature unit.")
    if to_unit == "deg F":
        return c * 9.0 / 5.0 + 32.0
    if to_unit == "deg C":
        return c
    if to_unit == "K":
        return c + 273.15
    raise ValueError("Unknown temperature unit.")

# ------------------------------------------------------------------------------
# Convert unit values using category scaling tables
def convert_unit(value: float, category: str, from_unit: str, to_unit: str) -> float:
    if category == "Temperature":
        return convert_temperature(value, from_unit, to_unit)
    units = UNIT_CONVERSIONS[category]
    return (value * units[from_unit]) / units[to_unit]

# ------------------------------------------------------------------------------
# Format floating-point conversion result for compact display
def format_unit_number(value: float) -> str:
    if math.isnan(value) or math.isinf(value):
        return str(value)
    return f"{value:.12g}"

# ------------------------------------------------------------------------------
# Format ASCII code for display in the Char column
def ascii_char_display(code: int) -> str:
    if code in ASCII_NAMES:
        return f"<{ASCII_NAMES[code]}>"
    if code == 32:
        return "<SPACE>"
    if 33 <= code <= 126:
        return chr(code)
    return "."


# ******************************************************************************
#
# APPLICATION WINDOWS
#
# ******************************************************************************

# ******************************************************************************
#
# APPLICATION WINDOW CLASSES LIVE IN LAUNCHER/EDITOR MODULES
#
# ******************************************************************************

