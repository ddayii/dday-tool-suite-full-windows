"""
DDay Controls Tool Suite Launcher
==================================
Single entry point that opens any registered DDay Controls tool.
Adding a new tool only requires a new entry in TOOL_REGISTRY in
dday_controls_common.py — this launcher needs no changes.
"""

from __future__ import annotations

import os
import sys

from dday_controls_common import *

LAUNCHER_TITLE = "DDay Controls Tool Suite"
LAUNCHER_SUBTITLE = "Select a tool to open"
LAUNCHER_APP_ID = "DDayControls.ToolSuiteLauncher.Qt"
LAUNCHER_ICON_ICO = "DDay Logo.ico"
LAUNCHER_ICON_PNG = "DDay Logo.png"

_TILE_ICON_SIZE = 80
_TILE_WIDTH = 120
_GRID_COLS = 3


class LauncherWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(LAUNCHER_TITLE)
        self._build_ui()
        apply_app_theme(resolve_theme(get_saved_theme_pref()))

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 12, 20, 6)
        root.setSpacing(10)

        root.addLayout(
            build_header(
                LAUNCHER_TITLE,
                LAUNCHER_SUBTITLE,
                logo_file=LAUNCHER_ICON_PNG,
                logo_size=48,
            )
        )

        visible = sorted(
            [(k, t) for k, t in TOOL_REGISTRY.items() if tool_available(k)],
            key=lambda x: x[1]["display_name"]
        )

        if not visible:
            lbl = QLabel("No tools are installed.\nRun the installer to add tools.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setObjectName("SubTitle")
            root.addWidget(lbl)
        else:
            grid_widget = QWidget()
            grid = QGridLayout(grid_widget)
            grid.setSpacing(8)
            grid.setContentsMargins(0, 4, 0, 4)

            for i, (tool_key, tool) in enumerate(visible):
                btn = QToolButton()
                btn.setText(tool["display_name"])
                btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                btn.setIconSize(QSize(_TILE_ICON_SIZE, _TILE_ICON_SIZE))
                btn.setFixedWidth(_TILE_WIDTH)

                icon_file = resource_path(tool.get("icon_png", ICON_PNG))
                if os.path.exists(icon_file):
                    btn.setIcon(QIcon(icon_file))

                btn.clicked.connect(
                    lambda _=False, key=tool_key: open_registered_tool(self, key)
                )
                grid.addWidget(btn, i // _GRID_COLS, i % _GRID_COLS)

            root.addWidget(grid_widget, 0, Qt.AlignHCenter)

        root.addStretch(1)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self.status_label = QLabel("Select a tool to open.")
        self.version_label = QLabel(f"{COMPANY_NAME}  |  {APP_VERSION}")
        status_bar.addWidget(self.status_label, 1)
        status_bar.addPermanentWidget(self.version_label)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)


def main() -> None:
    set_windows_app_user_model_id(LAUNCHER_APP_ID)
    app = QApplication.instance() or QApplication(sys.argv)
    apply_app_theme(resolve_theme(get_saved_theme_pref()))

    app.setApplicationName(LAUNCHER_TITLE)
    app.setOrganizationName(COMPANY_NAME)

    ico = resource_path(LAUNCHER_ICON_ICO)
    png = resource_path(LAUNCHER_ICON_PNG)
    if os.path.exists(ico):
        app.setWindowIcon(QIcon(ico))
    elif os.path.exists(png):
        app.setWindowIcon(QIcon(png))

    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
