"""
DDay Controls — Static data tables.

Pure-Python module: no Qt, no I/O.  Imported by dday_prefs and
dday_controls_common; re-exported from dday_controls_common so all
tool files that do ``from dday_controls_common import *`` get everything.
"""

from __future__ import annotations

from collections import OrderedDict


# ******************************************************************************
#
# THEME PALETTE TABLES
#
# ******************************************************************************

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


# ******************************************************************************
#
# COPY FORMAT DATA
#
# ******************************************************************************

CORE_COPY_FORMATS = OrderedDict({
    "None": ("", ""),
    "Custom": (None, None),
})

DEFAULT_COPY_FORMAT_GROUPS = OrderedDict({
    "Siemens PLC": [
        {"name": "Siemens DINT",       "prefix": "L#",    "suffix": ""},
        {"name": "Siemens HEX Byte",   "prefix": "B#16#", "suffix": ""},
        {"name": "Siemens HEX Word",   "prefix": "W#16#", "suffix": ""},
        {"name": "Siemens HEX DWord",  "prefix": "DW#16#","suffix": ""},
        {"name": "Siemens Binary",     "prefix": "2#",    "suffix": ""},
        {"name": "Siemens Time",       "prefix": "T#",    "suffix": ""},
        {"name": "Siemens S5Time",     "prefix": "S5T#",  "suffix": ""},
    ],
    "Allen-Bradley PLC": [
        {"name": "AB Hex",    "prefix": "16#", "suffix": ""},
        {"name": "AB Binary", "prefix": "2#",  "suffix": ""},
    ],
    "Mitsubishi PLC": [
        {"name": "Mitsubishi Hex",    "prefix": "H", "suffix": ""},
        {"name": "Mitsubishi Binary", "prefix": "B", "suffix": ""},
    ],
    "FANUC Robot": [
        {"name": "FANUC Register",          "prefix": "R[",  "suffix": "]"},
        {"name": "FANUC Position Register",  "prefix": "PR[", "suffix": "]"},
        {"name": "FANUC Digital Input",      "prefix": "DI[", "suffix": "]"},
        {"name": "FANUC Digital Output",     "prefix": "DO[", "suffix": "]"},
        {"name": "FANUC Group Input",        "prefix": "GI[", "suffix": "]"},
        {"name": "FANUC Group Output",       "prefix": "GO[", "suffix": "]"},
        {"name": "FANUC Flag",               "prefix": "F[",  "suffix": "]"},
    ],
    "Python": [
        {"name": "Python HEX",         "prefix": "0x",  "suffix": ""},
        {"name": "Python Binary",      "prefix": "0b",  "suffix": ""},
        {"name": "Python Octal",       "prefix": "0o",  "suffix": ""},
        {"name": "Python String",      "prefix": "\"",  "suffix": "\""},
        {"name": "Python Byte String", "prefix": "b\"", "suffix": "\""},
    ],
    "C / C++": [
        {"name": "C HEX",           "prefix": "0x", "suffix": ""},
        {"name": "C Unsigned",      "prefix": "",   "suffix": "U"},
        {"name": "C Long",          "prefix": "",   "suffix": "L"},
        {"name": "C Unsigned Long", "prefix": "",   "suffix": "UL"},
        {"name": "C Float",         "prefix": "",   "suffix": "f"},
    ],
    "Java": [
        {"name": "Java HEX",    "prefix": "0x", "suffix": ""},
        {"name": "Java Binary", "prefix": "0b", "suffix": ""},
        {"name": "Java Long",   "prefix": "",   "suffix": "L"},
    ],
    "JavaScript": [
        {"name": "JavaScript HEX",    "prefix": "0x", "suffix": ""},
        {"name": "JavaScript Binary", "prefix": "0b", "suffix": ""},
        {"name": "JavaScript Octal",  "prefix": "0o", "suffix": ""},
    ],
    "Generic Text": [
        {"name": "Quoted",         "prefix": "\"", "suffix": "\""},
        {"name": "Single Quoted",  "prefix": "'",  "suffix": "'"},
        {"name": "Parentheses",    "prefix": "(",  "suffix": ")"},
        {"name": "Brackets",       "prefix": "[",  "suffix": "]"},
        {"name": "Braces",         "prefix": "{",  "suffix": "}"},
        {"name": "Angle Brackets", "prefix": "<",  "suffix": ">"},
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


# ******************************************************************************
#
# UNIT CONVERSION TABLES
#
# ******************************************************************************

UNIT_CONVERSIONS: OrderedDict[str, OrderedDict[str, float]] = OrderedDict({
    "Length": OrderedDict({
        "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
        "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
    }),
    "Speed": OrderedDict({
        "mm/s": 0.001, "mm/min": 0.0000166666666666667,
        "m/s": 1.0, "m/min": 0.0166666666666667, "kph": 0.277777777777778,
        "in/s": 0.0254, "in/min": 0.000423333333333333,
        "ft/s": 0.3048, "ft/min": 0.00508, "mph": 0.44704,
    }),
    "Pressure": OrderedDict({
        "psi": 6894.757293168, "bar": 100000.0, "mbar": 100.0,
        "kPa": 1000.0, "MPa": 1000000.0, "Pa": 1.0,
        "atm": 101325.0, "inHg": 3386.389, "mmHg": 133.322387415,
    }),
    "Torque": OrderedDict({
        "N*m": 1.0, "N*cm": 0.01,
        "lbf*in": 0.1129848290276167, "lbf*ft": 1.3558179483314004,
        "ozf*in": 0.007061551814226,
    }),
    "Force": OrderedDict({
        "N": 1.0, "kN": 1000.0,
        "lbf": 4.4482216152605, "kgf": 9.80665, "ozf": 0.278013850953781,
    }),
    "Mass": OrderedDict({
        "mg": 0.000001, "g": 0.001, "kg": 1.0,
        "oz": 0.028349523125, "lb": 0.45359237,
    }),
    "Temperature": OrderedDict({"deg F": 1.0, "deg C": 1.0, "K": 1.0}),
    "Volume": OrderedDict({
        "mL": 0.001, "L": 1.0, "cm^3": 0.001,
        "in^3": 0.016387064, "ft^3": 28.316846592, "gal US": 3.785411784,
    }),
    "Area": OrderedDict({
        "mm^2": 0.000001, "cm^2": 0.0001, "m^2": 1.0,
        "in^2": 0.00064516, "ft^2": 0.09290304, "acre": 4046.8564224,
    }),
})


# ******************************************************************************
#
# ASCII CONTROL-CHARACTER NAMES
#
# ******************************************************************************

ASCII_NAMES = {
    0: "NUL",  1: "SOH",  2: "STX",  3: "ETX",  4: "EOT",  5: "ENQ",
    6: "ACK",  7: "BEL",  8: "BS",   9: "TAB", 10: "LF",  11: "VT",
    12: "FF",  13: "CR",  14: "SO",  15: "SI",  16: "DLE", 17: "DC1",
    18: "DC2", 19: "DC3", 20: "DC4", 21: "NAK", 22: "SYN", 23: "ETB",
    24: "CAN", 25: "EM",  26: "SUB", 27: "ESC", 28: "FS",  29: "GS",
    30: "RS",  31: "US",  127: "DEL",
}
