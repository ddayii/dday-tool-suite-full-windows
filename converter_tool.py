"""
DDay Controls Conversion Tool - Qt Edition (PySide6)
===================================================
Launcher module for the standalone Conversion Tool.
"""


from __future__ import annotations

import sys
import os

from dday_controls_common import *



# ******************************************************************************
#
# CONVERSION TOOL WINDOW
#
# ******************************************************************************


class ConversionTool(QMainWindow):


    # --------------------------------------------------------------------------
    # WINDOW INITIALIZATION
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Initialize the window and build its controls
    def __init__(self) -> None:
        super().__init__()
        register_tool_window("conversion_tool", self)
        self.theme_name = resolve_theme(get_saved_theme_pref())
        self.scalar_busy = False
        self.stream_busy = False
        self.unit_busy = False
        self.setWindowTitle(APP_NAME)
        icon = QIcon(resource_path(ICON_ICO)) if os.path.exists(resource_path(ICON_ICO)) else QIcon(resource_path(ICON_PNG))
        self.setWindowIcon(icon)
        self.resize(600, 560)
        self.setMinimumSize(600, 560)
        self._build_actions()
        self._build_ui()
        self.apply_theme(self.theme_name)
        update_owner_status(self, "Ready. DDay Controls Conversion Tool Loaded.")


    # --------------------------------------------------------------------------
    # MENU ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build main window menu actions
    def _build_actions(self) -> None:
        menu_bar = self.menuBar()

        add_file_menu(menu_bar, self)

        add_edit_menu(menu_bar, self, copy_formatted_callback=self.copy_formatted_from_menu,
            copy_formatted_available=self.copy_formatted_available,
        )

        tools_menu = menu_bar.addMenu("Tools")
        add_available_tool_actions(tools_menu, self, "conversion_tool")

        options_menu = menu_bar.addMenu("Options")
        add_theme_submenu(options_menu, self)
        add_copy_format_editor_action(options_menu, self)
        add_header_tool_selector_action(options_menu, self, "conversion_tool")

        add_help_menu(menu_bar, self, APP_NAME)


    # --------------------------------------------------------------------------
    # MAIN WINDOW LAYOUT
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build main window layout and tabs
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 10, 14, 4)
        root.setSpacing(6)
        
        header_button, header_callback = companion_header_button(self, "conversion_tool")
        
        root.addLayout(
            build_header(
                APP_NAME,
                "Unit, Scalar, Byte Stream & ASCII Conversion Utility",
                header_button,
                header_callback,
                logo_size=48,
            )
        )

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self.units_tab = QWidget()
        self.scalar_tab = QWidget()
        self.stream_tab = QWidget()
        self.tabs.addTab(self.units_tab, "Unit Converter")
        self.tabs.addTab(self.scalar_tab, "Scalar Converter")
        self.tabs.addTab(self.stream_tab, "Byte Stream")
        self._build_units_tab()
        self._build_scalar_tab()
        self._build_stream_tab()

        status = QStatusBar()
        self.setStatusBar(status)
        self.status_label = QLabel()
        self.version_label = QLabel(f"{COMPANY_NAME}  |  {APP_VERSION}")
        status.addWidget(self.status_label, 1)
        status.addPermanentWidget(self.version_label)


    # --------------------------------------------------------------------------
    # SHARED FORM FIELD HELPERS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Add labeled form row with optional copy button
    def row(
        self,
        parent: QGridLayout,
        row: int,
        label: str,
        edit: QLineEdit,
        copy_name: str | None = None,
        use_scalar_format: bool = False,
        label_width: int | None = None,
    ) -> None:
        add_labeled_entry_row(
            self,
            parent,
            row,
            label,
            edit,
            copy_name,
            self.format_scalar_copy if use_scalar_format else None,
            label_width,
        )

    # --------------------------------------------------------------------------
    # EDIT MENU COPY FORMAT ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Copy current value using selected copy format
    def copy_formatted_from_menu(self) -> None:
        if self.tabs.currentWidget() != self.scalar_tab:
            return

        edit = focused_line_edit()
        valid_fields = [
            self.s_dec, self.s_hex, self.s_bin, self.s_oct,
            self.le, self.be, self.char, self.le_ascii, self.be_ascii
        ]

        if edit not in valid_fields:
            return

        self.copy_value(self.format_scalar_copy(edit.text()), "")

    # ------------------------------------------------------------------------------
    # Return whether formatted copy is currently available
    def copy_formatted_available(self) -> bool:
        if self.tabs.currentWidget() != self.scalar_tab:
            return False

        edit = focused_line_edit()
        return edit in [
            self.s_dec, self.s_hex, self.s_bin, self.s_oct,
            self.le, self.be, self.char, self.le_ascii, self.be_ascii
        ]


    # --------------------------------------------------------------------------
    # UNIT CONVERTER TAB LAYOUT
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Unit Converter tab layout
    def _build_units_tab(self) -> None:
        layout = QGridLayout(self.units_tab)
        layout.setColumnStretch(1, 1)
        self.category_combo = QComboBox()
        self.category_combo.addItems(list(UNIT_CONVERSIONS.keys()))
        self.unit_input = QLineEdit()
        self.from_combo = QComboBox()
        self.to_combo = QComboBox()
        self.unit_result = QLineEdit()
        self.unit_result.setReadOnly(True)
        layout.addWidget(form_label("Category",55), 0, 0)
        layout.addWidget(self.category_combo, 0, 1, 1, 5)
        layout.addWidget(form_label("Input",55), 1, 0)
        layout.addWidget(self.unit_input, 1, 1, 1, 5)
        layout.addWidget(form_label("From",55), 2, 0)
        layout.addWidget(self.from_combo, 2, 1, 1, 5)
        layout.addWidget(form_label("To",55), 3, 0)
        layout.addWidget(self.to_combo, 3, 1, 1, 5)
        layout.addWidget(form_label("Result",55), 4, 0)
        layout.addWidget(self.unit_result, 4, 1, 1, 5)
        convert = QPushButton("Convert")
        swap = QPushButton("Swap")
        copy = QPushButton("Copy Result")
        clear = QPushButton("Clear")
        convert.setFixedWidth(CONVERT_BUTTON_WIDTH)
        swap.setFixedWidth(SWAP_BUTTON_WIDTH)
        copy.setFixedWidth(COPY_RESULT_WIDTH)
        clear.setFixedWidth(CLEAR_BUTTON_WIDTH)
        layout.addWidget(convert, 5, 1, Qt.AlignLeft)
        layout.setColumnStretch(2, 1)
        layout.addWidget(swap, 5, 4, Qt.AlignRight)
        layout.addWidget(copy, 5, 5, Qt.AlignRight)
        layout.addWidget(clear, 6, 5, Qt.AlignBottom | Qt.AlignRight)
        layout.setRowStretch(6, 1)
        self.category_combo.currentTextChanged.connect(self.update_unit_lists)
        self.unit_input.textChanged.connect(self.update_unit_conversion)
        self.from_combo.currentTextChanged.connect(self.update_unit_conversion)
        self.to_combo.currentTextChanged.connect(self.update_unit_conversion)
        convert.clicked.connect(self.update_unit_conversion)
        swap.clicked.connect(self.swap_units)
        copy.clicked.connect(lambda: self.copy_value(self.unit_result.text()))
        clear.clicked.connect(self.clear_units)
        self.update_unit_lists()


    # --------------------------------------------------------------------------
    # SCALAR COPY FORMAT CONTROLS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Apply selected scalar copy format to a value
    def format_scalar_copy(self, value: str) -> str:
        return format_copy_value(
            value,
            self.scalar_copy_format,
            self.scalar_copy_prefix,
            self.scalar_copy_suffix,
        )

    # ------------------------------------------------------------------------------
    # Refresh this window's copy-format combo while preserving selection
    def refresh_copy_format_options(self) -> None:
        refresh_copy_format_combo(
            self.scalar_copy_format,
            self.scalar_copy_prefix,
            self.scalar_copy_suffix
        )


    # --------------------------------------------------------------------------
    # SCALAR CONVERTER TAB LAYOUT
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Scalar Converter tab layout
    def _build_scalar_tab(self) -> None:
        main = QGridLayout(self.scalar_tab)
        main.setColumnStretch(0, 1)
        main.setColumnStretch(1, 1)

        main.setRowStretch(0, 0)
        main.setRowStretch(1, 0)
        main.setRowStretch(2, 1)

        config = QGroupBox("Configuration")
        cfg = QGridLayout(config)
        cfg.setHorizontalSpacing(10)
        cfg.setVerticalSpacing(8)

        self.width_combo = QComboBox()
        self.width_combo.addItems(["8-bit", "16-bit", "32-bit"])
        self.width_combo.setCurrentText("16-bit")
        self.width_combo.setFixedWidth(150)

        self.signed_check = QCheckBox("Signed")
        self.signed_check.setChecked(False)

        self.range_label = QLabel()
        self.range_label.setMinimumWidth(145)

        self.scalar_copy_format = QComboBox()
        self.scalar_copy_format.addItems(list(COPY_FORMATS.keys()))
        self.scalar_copy_format.setCurrentText("None")
        self.scalar_copy_format.setFixedWidth(150)

        self.scalar_copy_prefix = QLineEdit()
        self.scalar_copy_prefix.setFixedWidth(80)
        self.scalar_copy_prefix.setObjectName("LockedDisplayLineEdit")

        self.scalar_copy_suffix = QLineEdit()
        self.scalar_copy_suffix.setFixedWidth(80)
        self.scalar_copy_suffix.setObjectName("LockedDisplayLineEdit")

        cfg.addWidget(form_label("Width", 75), 0, 0)
        cfg.addWidget(self.width_combo, 0, 1, Qt.AlignLeft)
        cfg.addWidget(self.signed_check, 0, 3, Qt.AlignLeft)
        cfg.addWidget(self.range_label, 0, 4, 1,2, Qt.AlignLeft)

        cfg.addWidget(form_label("Copy Format", 75), 1, 0)
        cfg.addWidget(self.scalar_copy_format, 1, 1, Qt.AlignLeft)
        cfg.addWidget(form_label("Prefix", 40), 1, 2)
        cfg.addWidget(self.scalar_copy_prefix, 1, 3, Qt.AlignLeft)
        cfg.addWidget(form_label("Suffix", 40), 1, 4)
        cfg.addWidget(self.scalar_copy_suffix, 1, 5, Qt.AlignLeft)

        # Only the final blank column stretches; the actual controls remain anchored.
        for col in range(6):
            cfg.setColumnStretch(col, 0)
        cfg.setColumnStretch(6, 1)

        connect_copy_format_controls(self.scalar_copy_format, self.scalar_copy_prefix, self.scalar_copy_suffix)

        main.addWidget(config, 0, 0, 1, 2)

        values = QGroupBox("Values")
        values.setMinimumHeight(172)
        val = QGridLayout(values)
        val.setColumnStretch(1, 1)
        val.setVerticalSpacing(6)
        val.setHorizontalSpacing(8)
        for r in range(4):
            val.setRowMinimumHeight(r, 42)
            val.setRowStretch(r, 0)
        val.setRowStretch(4, 1)

        self.s_dec = make_entry()
        self.s_hex = make_entry()
        self.s_bin = make_entry()
        self.s_oct = make_entry()
        self.row(val, 0, "DEC", self.s_dec, "DEC", use_scalar_format=True, label_width=30)
        self.row(val, 1, "HEX", self.s_hex, "HEX", use_scalar_format=True, label_width=30)
        self.row(val, 2, "BIN", self.s_bin, "BIN", use_scalar_format=True, label_width=30)
        self.row(val, 3, "OCT", self.s_oct, "OCT", use_scalar_format=True, label_width=30)
        main.addWidget(values, 1, 0)

        bytes_box = QGroupBox("Bytes  /  ASCII")
        bytes_box.setMinimumHeight(277)
        by = QGridLayout(bytes_box)
        by.setColumnStretch(1, 1)
        by.setVerticalSpacing(6)
        by.setHorizontalSpacing(8)
        for r in range(5):
            by.setRowMinimumHeight(r, 42)
            by.setRowStretch(r, 0)
        #by.setRowStretch(5, 1)

        self.le = make_entry(True)
        self.be = make_entry(True)
        self.char = make_entry(True)
        self.le_ascii = make_entry(True)
        self.be_ascii = make_entry(True)
        self.row(by, 0, "Little Endian", self.le, "Little Endian", use_scalar_format=True, label_width=70)
        self.row(by, 1, "Big Endian", self.be, "Big Endian", use_scalar_format=True, label_width=70)
        self.row(by, 2, "8-bit Char", self.char, "8-bit Char", use_scalar_format=True, label_width=70)
        self.row(by, 3, "LE ASCII", self.le_ascii, "LE ASCII", use_scalar_format=True, label_width=70)
        self.row(by, 4, "BE ASCII", self.be_ascii, "BE ASCII", use_scalar_format=True, label_width=70)
        main.addWidget(bytes_box, 1, 1)

        clear = QPushButton("Clear")
        clear.clicked.connect(self.clear_scalar)
        clear.setFixedWidth(CLEAR_BUTTON_WIDTH)
        main.addWidget(clear, 2, 0, Qt.AlignBottom | Qt.AlignLeft)

        self.width_combo.currentTextChanged.connect(self.refresh_scalar_from_existing)
        self.signed_check.stateChanged.connect(self.refresh_scalar_from_existing)
        self.s_dec.textChanged.connect(lambda: self.update_scalar_from_source("DEC"))
        self.s_hex.textChanged.connect(lambda: self.update_scalar_from_source("HEX"))
        self.s_bin.textChanged.connect(lambda: self.update_scalar_from_source("BIN"))
        self.s_oct.textChanged.connect(lambda: self.update_scalar_from_source("OCT"))
        self.update_scalar_range()


    # --------------------------------------------------------------------------
    # BYTE STREAM TAB LAYOUT
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Byte Stream tab layout
    def _build_stream_tab(self) -> None:
        layout = QGridLayout(self.stream_tab)
        layout.setColumnStretch(1, 1)
        layout.addWidget(QLabel("Type or paste into any field. Other formats update automatically."), 0, 0, 1, 3)
        self.ascii_e = make_entry()
        self.hex_e = make_entry()
        self.dec_e = make_entry()
        self.bin_e = make_entry()
        self.oct_e = make_entry()
        rows = [("ASCII", self.ascii_e), ("HEX", self.hex_e), ("DEC", self.dec_e), ("BIN", self.bin_e), ("OCT", self.oct_e)]
        for r, (label, edit) in enumerate(rows, 1):
            self.row(layout, r, label, edit, label, label_width=35)
        clear = QPushButton("Clear")
        clear.clicked.connect(self.clear_stream)
        clear.setFixedWidth(CLEAR_BUTTON_WIDTH)
        layout.addWidget(clear, 6, 2, Qt.AlignBottom | Qt.AlignRight)
        layout.setRowStretch(6, 1)
        self.ascii_e.textChanged.connect(lambda: self.update_stream_from_source("ASCII"))
        self.hex_e.textChanged.connect(lambda: self.update_stream_from_source("HEX"))
        self.dec_e.textChanged.connect(lambda: self.update_stream_from_source("DEC"))
        self.bin_e.textChanged.connect(lambda: self.update_stream_from_source("BIN"))
        self.oct_e.textChanged.connect(lambda: self.update_stream_from_source("OCT"))


    # --------------------------------------------------------------------------
    # SCALAR CONVERSION LOGIC
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Return current scalar bit width and signed mode
    def bits_signed(self) -> tuple[int, bool]:
        return get_bit_width(self.width_combo.currentText()), self.signed_check.isChecked()

    # ------------------------------------------------------------------------------
    # Update scalar range label from current width and signed mode
    def update_scalar_range(self) -> None:
        bits, signed = self.bits_signed()
        low, high = range_info(bits, signed)
        self.range_label.setText(f"Range: {low} to {high}")

    # ------------------------------------------------------------------------------
    # Recalculate scalar values from the currently populated field
    def refresh_scalar_from_existing(self) -> None:
        self.update_scalar_range()
        for fmt, edit in [("DEC", self.s_dec), ("HEX", self.s_hex), ("BIN", self.s_bin), ("OCT", self.s_oct)]:
            if edit.text().strip():
                self.update_scalar_from_source(fmt)
                return

    # ------------------------------------------------------------------------------
    # Update scalar values from the edited source field
    def update_scalar_from_source(self, source: str) -> None:
        if self.scalar_busy:
            return
        edit_map = {"DEC": self.s_dec, "HEX": self.s_hex, "BIN": self.s_bin, "OCT": self.s_oct}
        source_edit = edit_map[source]
        if not source_edit.hasFocus() and source_edit.text().strip() == "":
            return
        if source_edit.text().strip() == "":
            self.clear_scalar_outputs_only()
            return
        self.scalar_busy = True
        try:
            bits, signed = self.bits_signed()
            value = parse_integer_text(source, source_edit.text(), bits, signed)
            for fmt, edit in edit_map.items():
                if fmt != source:
                    edit.setText(format_integer_value(value, fmt, bits))
            little, big = endian_bytes(value, bits)
            self.le.setText(" ".join(little))
            self.be.setText(" ".join(big))
            self.char.setText(printable_char(unsigned_value(value, bits) & 0xFF) if bits == 8 else "")
            self.le_ascii.setText("".join(printable_char(int(x, 16)) for x in little))
            self.be_ascii.setText("".join(printable_char(int(x, 16)) for x in big))
            update_owner_status(self, "Scalar conversion ready.")
        except Exception as exc:
            self.clear_scalar_outputs_only(exclude=source)
            update_owner_status(self, str(exc))
        finally:
            self.scalar_busy = False

    # ------------------------------------------------------------------------------
    # Clear scalar output fields except the active source field
    def clear_scalar_outputs_only(self, exclude: str | None = None) -> None:
        scalar_edits = {"DEC": self.s_dec, "HEX": self.s_hex, "BIN": self.s_bin, "OCT": self.s_oct}
        clear_line_edits([edit for fmt, edit in scalar_edits.items() if fmt != exclude])
        clear_line_edits([self.le, self.be, self.char, self.le_ascii, self.be_ascii])

    # ------------------------------------------------------------------------------
    # Clear all Scalar Converter fields
    def clear_scalar(self) -> None:
        self.scalar_busy = True
        clear_line_edits([self.s_dec, self.s_hex, self.s_bin, self.s_oct, self.le, self.be, self.char, self.le_ascii, self.be_ascii])
        self.scalar_busy = False
        update_owner_status(self, "Scalar tab cleared.")

    # --------------------------------------------------------------------------
    # BYTE STREAM CONVERSION LOGIC
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Update byte stream fields from the edited source format
    def update_stream_from_source(self, source: str) -> None:
        if self.stream_busy:
            return
        edit_map = {"ASCII": self.ascii_e, "HEX": self.hex_e, "DEC": self.dec_e, "BIN": self.bin_e, "OCT": self.oct_e}
        source_edit = edit_map[source]
        if not source_edit.hasFocus() and source_edit.text().strip() == "":
            return
        self.stream_busy = True
        try:
            data = parse_byte_stream(source, source_edit.text())
            for fmt, edit in edit_map.items():
                if fmt != source:
                    edit.setText(format_byte_stream(data, fmt))
            update_owner_status(self, "Byte stream conversion ready.")
        except Exception as exc:
            update_owner_status(self, str(exc))
        finally:
            self.stream_busy = False

    # ------------------------------------------------------------------------------
    # Clear all Byte Stream fields
    def clear_stream(self) -> None:
        self.stream_busy = True
        clear_line_edits([self.ascii_e, self.hex_e, self.dec_e, self.bin_e, self.oct_e])
        self.stream_busy = False
        update_owner_status(self, "Byte stream tab cleared.")


    # --------------------------------------------------------------------------
    # UNIT CONVERSION LOGIC
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Refresh unit list choices for selected category
    def update_unit_lists(self) -> None:
        category = self.category_combo.currentText()
        units = list(UNIT_CONVERSIONS[category].keys())

        replace_combo_items_preserve(self.from_combo, units, 0)
        replace_combo_items_preserve(self.to_combo, units, 1)

        self.update_unit_conversion()

    # ------------------------------------------------------------------------------
    # Update unit conversion result from current input
    def update_unit_conversion(self) -> None:
        if self.unit_busy:
            return
        text = self.unit_input.text().strip()
        if not text:
            self.unit_result.clear()
            return
        try:
            value = float(text)
            result = convert_unit(value, self.category_combo.currentText(), self.from_combo.currentText(), self.to_combo.currentText())
            self.unit_result.setText(format_unit_number(result))
            update_owner_status(self, "Unit conversion ready.")
        except Exception as exc:
            self.unit_result.clear()
            update_owner_status(self, str(exc))

    # ------------------------------------------------------------------------------
    # Swap unit conversion source and destination units
    def swap_units(self) -> None:
        a, b = self.from_combo.currentText(), self.to_combo.currentText()
        self.from_combo.setCurrentText(b)
        self.to_combo.setCurrentText(a)
        self.update_unit_conversion()

    # ------------------------------------------------------------------------------
    # Clear Unit Converter input and result fields
    def clear_units(self) -> None:
        clear_line_edits([self.unit_input, self.unit_result])
        update_owner_status(self, "Unit tab cleared.")


    # --------------------------------------------------------------------------
    # GENERAL ACTIONS AND STATUS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Clear fields on the active converter tab
    def clear_current_tab(self) -> None:
        idx = self.tabs.currentIndex()
        if idx == 0:
            self.clear_units()
        elif idx == 1:
            self.clear_scalar()
        else:
            self.clear_stream()

    # ------------------------------------------------------------------------------
    # Copy a conversion value through the shared clipboard helper
    def copy_value(self, value: str, name: str = "") -> None:
        copy_to_clipboard(self, value)

    # ------------------------------------------------------------------------------
    # Open or focus the ASCII Chart through the common tool director
    def show_ascii_chart(self) -> None:
        """Open or focus the ASCII Chart through the common tool director."""
        open_registered_tool(self, "ascii_chart")


    # ------------------------------------------------------------------------------
    # Set main window status text
    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    # ------------------------------------------------------------------------------
    # Apply selected application theme to this window
    def apply_theme(self, theme: str) -> None:
        self.theme_name = theme
        apply_app_theme(theme)


# ******************************************************************************
#
# RUNTIME ENTRY POINT
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Initialize Qt application runtime and open the Conversion Tool
def main() -> None:
    """Initialize Qt and open the standalone Conversion Tool window."""
    set_windows_app_user_model_id("DDayControls.ConversionTool.Qt")
    app = QApplication(sys.argv)
    apply_app_theme(resolve_theme(get_saved_theme_pref()))

    app.setApplicationName(APP_NAME)
    app.setOrganizationName(COMPANY_NAME)

    icon_path = resource_path(ICON_ICO)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = ConversionTool()
    window.show()
    sys.exit(app.exec())


# Script execution gateway wrapper
if __name__ == "__main__":
    main()
