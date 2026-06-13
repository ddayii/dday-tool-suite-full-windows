"""
DDay Controls ASCII Chart - Qt Edition (PySide6)
===============================================
Launcher module for the standalone ASCII Chart.
"""


from __future__ import annotations

import sys
import os

from dday_controls_common import *



# ******************************************************************************
#
# ASCII CHART WINDOW
#
# ******************************************************************************


class AsciiDialog(QDialog):


    # --------------------------------------------------------------------------
    # WINDOW INITIALIZATION
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Initialize the window and build its controls
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        register_tool_window("ascii_chart", self)
        self.theme_name = resolve_theme(get_saved_theme_pref())
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.parent_tool = parent
        self.setWindowTitle("DDay Controls ASCII Chart")
        self.last_copy_column = 0
        for icon_name in ("DDay_ASCII_Chart.ico", "DDay_ASCII_Chart.png"):
            icon_path = resource_path(icon_name)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
        else:
            if parent is not None:
                self.setWindowIcon(parent.windowIcon())
        self.resize(400, 300)
        layout = QVBoxLayout(self)

        menubar = QMenuBar()
        layout.setMenuBar(menubar)

        add_file_menu(menubar, self)

        add_edit_menu(menubar, self, self.copy_current_cell_from_menu, self.copy_current_cell_available,
            self.copy_formatted_from_menu, self.copy_formatted_available,
        )

        tools_menu = menubar.addMenu("Tools")
        add_available_tool_actions(tools_menu, self, "ascii_chart")

        options_menu = menubar.addMenu("Options")

        self.show_extended_action = QAction("Show Extended", self)
        self.show_extended_action.setCheckable(True)
        self.show_extended_action.toggled.connect(self.set_extended_from_menu)
        options_menu.addAction(self.show_extended_action)

        self.always_on_top_action = QAction("Always On Top", self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.toggled.connect(self.toggle_always_on_top)
        options_menu.addAction(self.always_on_top_action)

        options_menu.addSeparator()
        add_theme_submenu(options_menu, self, self.populate)
        add_copy_format_editor_action(options_menu, self)
        add_header_tool_selector_action(options_menu, self, "ascii_chart")

        add_help_menu(menubar, self, "DDay Controls ASCII Chart")

        header_button, header_callback = companion_header_button(self, "ascii_chart")
        
        layout.addLayout(
            build_header(
                "DDay Controls ASCII Chart",
                "Select a row, then click a column header to copy that value",
                header_button,
                header_callback,
                logo_file="DDay_ASCII_Chart.png",
                logo_size=48,
            )
        )

        format_row = QHBoxLayout()
        format_row.addStretch(1)

        format_row.addWidget(form_label("Copy Format",75))

        self.copy_format = QComboBox()
        self.copy_format.addItems(list(COPY_FORMATS.keys()))
        self.copy_format.setCurrentText("None")
        self.copy_format.setFixedWidth(150)
        format_row.addWidget(self.copy_format)

        format_row.addWidget(form_label("Prefix", 40))
        self.copy_prefix = QLineEdit()
        self.copy_prefix.setFixedWidth(80)
        self.copy_prefix.setObjectName("LockedDisplayLineEdit")
        format_row.addWidget(self.copy_prefix)

        format_row.addWidget(form_label("Suffix", 40))
        self.copy_suffix = QLineEdit()
        self.copy_suffix.setFixedWidth(80)
        self.copy_suffix.setObjectName("LockedDisplayLineEdit")
        format_row.addWidget(self.copy_suffix)

        layout.addLayout(format_row)

        connect_copy_format_controls(self.copy_format, self.copy_prefix, self.copy_suffix)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Char", "Dec", "Hex", "Oct", "Bin", "Name"])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().sectionClicked.connect(self.copy_selected_column)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        bottom = QHBoxLayout()
        self.dialog_status = QLabel("Ready.")
        self.dialog_status.setObjectName("SubTitle")

        self.extended = QCheckBox("Show Extended 128-255")
        self.extended.setObjectName("SubTitle")
        self.extended.stateChanged.connect(self.populate)
        self.extended.stateChanged.connect(
            lambda state: set_checkable_state_silent(self.show_extended_action, bool(state))
        )

        self.always_on_top_toggle = QCheckBox("Always On Top")
        self.always_on_top_toggle.setObjectName("SubTitle")
        self.always_on_top_toggle.toggled.connect(self.toggle_always_on_top)

        version = QLabel(f"DDay Controls | {APP_VERSION}")
        version.setObjectName("SubTitle")
        bottom.addWidget(self.dialog_status)
        bottom.addStretch(1)
        bottom.addWidget(self.extended)
        bottom.addSpacing(16)
        bottom.addWidget(self.always_on_top_toggle)
        bottom.addStretch(1)
        bottom.addWidget(version)
        layout.addLayout(bottom)
        self.populate()



    # --------------------------------------------------------------------------
    # EDIT MENU COPY ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Copy current ASCII table cell from the Edit menu
    def copy_current_cell_from_menu(self) -> None:
        copy_table_cell(self, self.table)


    # ------------------------------------------------------------------------------
    # Return whether current ASCII table cell can be copied
    def copy_current_cell_available(self) -> bool:
        return table_cell_copy_available(self.table)


    # ------------------------------------------------------------------------------
    # Copy current value using selected copy format
    def copy_formatted_from_menu(self) -> None:
        copy_table_cell_formatted(
            self,
            self.table,
            self.copy_format,
            self.copy_prefix,
            self.copy_suffix,
        )


    # ------------------------------------------------------------------------------
    # Return whether formatted copy is currently available
    def copy_formatted_available(self) -> bool:
        return table_cell_copy_available(self.table)


    # --------------------------------------------------------------------------
    # WINDOW MANAGEMENT ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Open or focus the Conversion Tool through the common tool director
    def show_conversion_tool(self) -> None:
        """Open or focus the Conversion Tool through the common tool director."""
        open_registered_tool(self, "conversion_tool")


    # --------------------------------------------------------------------------
    # OPTION ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Toggle ASCII Chart always-on-top window state
    def toggle_always_on_top(self, checked: bool) -> None:
        self.setWindowFlag(Qt.WindowStaysOnTopHint, checked)

        if hasattr(self, "always_on_top_toggle"):
            set_checkable_state_silent(self.always_on_top_toggle, checked)

        if hasattr(self, "always_on_top_action"):
            set_checkable_state_silent(self.always_on_top_action, checked)

        self.show()

    # ------------------------------------------------------------------------------
    # Synchronize extended ASCII menu action to checkbox state
    def set_extended_from_menu(self, checked: bool) -> None:
        set_checkable_state_silent(self.extended, checked)
        self.populate()


    # --------------------------------------------------------------------------
    # COPY FORMAT CONTROLS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Refresh this window's copy-format combo while preserving selection
    def refresh_copy_format_options(self) -> None:
        refresh_copy_format_combo(self.copy_format, self.copy_prefix, self.copy_suffix)

    # ------------------------------------------------------------------------------
    # Reset copy-format selection to None
    def reset_copy_format(self) -> None:
        self.copy_format.setCurrentText("None")
        self.copy_prefix.clear()
        self.copy_suffix.clear()
        update_owner_status(self, "Copy format reset.")
        if self.parent_tool is not None:
            update_owner_status(self.parent_tool, "ASCII Chart copy format reset.")


    # --------------------------------------------------------------------------
    # HELP AND REFERENCE ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Show ASCII chart usage reference dialog
    def show_ascii_reference(self) -> None:
        QMessageBox.information(
            self,
            "ASCII Reference",
            "Select a row, then click a column header to copy that value.\n\n"
            "Columns available for copy: Dec, Hex, Bin, Oct, Char, and Name.\n\n"
            "Use Copy Format to automatically add prefixes or suffixes such as Siemens L#, B#16#, W#16#, 0x, or custom text."
        )


    # --------------------------------------------------------------------------
    # TABLE POPULATION AND COPY LOGIC
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Populate the ASCII chart table rows
    def populate(self) -> None:
        max_code = 255 if self.extended.isChecked() else 127
        self.table.setRowCount(max_code + 1)

        for code in range(max_code + 1):
            row = [
                ascii_char_display(code),
                str(code),
                f"{code:02X}",
                f"{code:03o}",
                f"{code:08b}",
                ASCII_NAMES.get(code, "")
            ]

            for col, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)

                # Slight highlight for ASCII Char column only
                if col == 0:
                    item.setBackground(QColor(THEMES[self.theme_name]["char_col"]))

                self.table.setItem(code, col, item)

        self.table.selectRow(0)


    # ------------------------------------------------------------------------------
    # Copy selected ASCII row value from clicked column header
    def copy_selected_column(self, column: int) -> None:
        self.last_copy_column = column

        copy_table_current_row_column(
            self,
            self.table,
            column,
            formatted=True,
            combo=self.copy_format,
            prefix_box=self.copy_prefix,
            suffix_box=self.copy_suffix,
        )


# ******************************************************************************
#
# RUNTIME ENTRY POINT
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Initialize Qt application runtime and open the ASCII Chart
def main() -> None:
    """Initialize Qt and open the standalone ASCII Chart window."""
    set_windows_app_user_model_id("DDayControls.ASCIIChart.Qt")
    app = QApplication(sys.argv)
    apply_app_theme(resolve_theme(get_saved_theme_pref()))

    app.setApplicationName("DDay Controls ASCII Chart")
    app.setOrganizationName(COMPANY_NAME)

    icon_path = resource_path(ICON_ICO)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = AsciiDialog(None)
    window.show()
    sys.exit(app.exec())


# Script execution gateway wrapper
if __name__ == "__main__":
    main()
