"""
DDay Controls — Preferences and copy-format management.

Handles load/save of user preferences (AppData JSON), the active COPY_FORMATS
lookup, and theme-resolution helpers.  Imported by dday_controls_common and
re-exported from it, so tool files need no direct import of this module.
"""

from __future__ import annotations

import json
import os
import platform
from collections import OrderedDict

from dday_data import DEFAULT_COPY_FORMAT_GROUPS, build_copy_formats_from_groups


# ******************************************************************************
#
# COPY-FORMAT GROUP HELPERS
#
# ******************************************************************************

# ------------------------------------------------------------------------------
# Return copy-format groups with the user custom group guaranteed
def copy_format_groups_with_user_group(groups: dict | None = None) -> OrderedDict:
    source = groups if groups is not None else PREFERENCES.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS)
    ordered = OrderedDict(source)
    if "User Custom" not in ordered:
        ordered["User Custom"] = []
    return ordered


# ------------------------------------------------------------------------------
# Return copy-format group display order
def copy_format_group_order(groups: dict | None = None, preferences: dict | None = None) -> list[str]:
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
# Rebuild global copy-format lookup from preferences (mutates in place)
def rebuild_global_copy_formats() -> None:
    new = build_copy_formats_from_groups(
        PREFERENCES["copy_format_groups"],
        ordered_enabled_copy_format_groups(PREFERENCES),
    )
    COPY_FORMATS.clear()
    COPY_FORMATS.update(new)
    PREFERENCES["copy_formats"] = COPY_FORMATS


# ******************************************************************************
#
# PREFERENCES LOAD / SAVE
#
# ******************************************************************************

DEFAULT_PREFERENCES = {
    "theme": "System",
    "copy_format_group_order": [
        "Siemens PLC", "Allen-Bradley PLC", "Mitsubishi PLC", "FANUC Robot",
        "Python", "C / C++", "Java", "JavaScript", "Generic Text", "User Custom",
    ],
    "enabled_copy_format_groups": [
        "Siemens PLC", "Allen-Bradley PLC", "Mitsubishi PLC", "FANUC Robot",
        "Python", "C / C++", "Java", "JavaScript", "Generic Text",
    ],
    "copy_format_groups": DEFAULT_COPY_FORMAT_GROUPS,
    "header_tool_by_tool": {},
}

COPY_FORMATS: OrderedDict[str, tuple[str | None, str | None]] = OrderedDict()


# ------------------------------------------------------------------------------
# Get the user-writable DDay Controls configuration folder
def app_config_dir() -> str:
    if platform.system() == "Windows":
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "DDay Controls")
    return os.path.join(os.path.expanduser("~"), ".dday_controls")


# ------------------------------------------------------------------------------
# Get the shared preferences JSON file path
def preferences_path() -> str:
    return os.path.join(app_config_dir(), "converter_preferences.json")


# ------------------------------------------------------------------------------
# Build a fresh default preferences dict
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


# Module-level initialization: load prefs and populate COPY_FORMATS.
PREFERENCES = load_preferences()
rebuild_global_copy_formats()


# ******************************************************************************
#
# THEME HELPERS
#
# ******************************************************************************

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
# Get saved theme preference
def get_saved_theme_pref() -> str:
    return PREFERENCES.get("theme", "System")


# ------------------------------------------------------------------------------
# Resolve System theme preference to Light or Dark
def resolve_theme(theme_pref: str) -> str:
    return get_windows_app_theme() if theme_pref == "System" else theme_pref


# ------------------------------------------------------------------------------
# Save selected theme preference
def set_saved_theme_pref(theme_pref: str) -> None:
    PREFERENCES["theme"] = theme_pref
    save_preferences(PREFERENCES)
