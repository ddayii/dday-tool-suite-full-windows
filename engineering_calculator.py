"""
DDay Controls Engineering Calculator - Qt Edition (PySide6)
==========================================================
Launcher module for the standalone Engineering Calculator.

All arithmetic lives in dday_engineering.py, which is pure Python and
shared with the PWA build of the same tool.
"""


from __future__ import annotations

import os
import re
import sys

from dday_controls_common import *


CALC_APP_NAME = "DDay Controls Engineering Calculator"
CALC_ICON_ICO = "DDay_Engineering_Calculator.ico"
CALC_ICON_PNG = "DDay_Engineering_Calculator.png"

# The app-wide stylesheet puts 9pt Segoe UI on every widget, and a stylesheet
# beats setFont(), so the display's own stylesheet is what actually wins.
_DISPLAY_QSS = "font-family: Consolas, 'Courier New', monospace; font-size: 16pt; font-weight: bold;"
_MONO_QSS = "font-family: Consolas, 'Courier New', monospace;"

CALC_BASE_ORDER = ("HEX", "DEC", "OCT", "BIN")
CALC_DIGIT_ORDER = "0123456789ABCDEF"
CALC_BASE_DIGIT_COUNT = {"HEX": 16, "DEC": 10, "OCT": 8, "BIN": 2}

CALC_MEMORY_KEYS = ("MC", "MR", "MS", "M+", "M-")

CALC_BITWISE_KEYS = (
    ("AND", " & "), ("OR", " | "), ("XOR", " ^ "), ("NOT", "~"), ("MOD", " % "),
)

# Laid out like the Windows programmer keypad, so it reads as a calculator.
CALC_KEYPAD_ROWS = (
    (("A", "digit", "A"), ("\u00ab", "ins", " << "), ("\u00bb", "ins", " >> "),
     ("C", "act", "clear"), ("\u232b", "act", "back")),
    (("B", "digit", "B"), ("(", "ins", "("), (")", "ins", ")"),
     ("%", "ins", " % "), ("\u00f7", "ins", " / ")),
    (("C", "digit", "C"), ("7", "digit", "7"), ("8", "digit", "8"),
     ("9", "digit", "9"), ("\u00d7", "ins", " * ")),
    (("D", "digit", "D"), ("4", "digit", "4"), ("5", "digit", "5"),
     ("6", "digit", "6"), ("\u2212", "ins", " - ")),
    (("E", "digit", "E"), ("1", "digit", "1"), ("2", "digit", "2"),
     ("3", "digit", "3"), ("+", "ins", " + ")),
    (("F", "digit", "F"), ("\u00b1", "act", "negate"), ("0", "digit", "0"),
     (".", "off", "decimal"), ("=", "act", "equals")),
)

STANDARD_MEMORY_KEYS = ("MC", "MR", "MS", "M+", "M-")

# The Windows standard keypad, four columns wide.
STANDARD_KEYPAD_ROWS = (
    (("mod", "ins", " % "), ("\u221a", "act", "sqrt"),
     ("x\u00b2", "act", "square"), ("1/x", "act", "inverse")),
    (("CE", "act", "clearentry"), ("C", "act", "clear"),
     ("\u232b", "act", "back"), ("\u00f7", "ins", " / ")),
    (("7", "ins", "7"), ("8", "ins", "8"), ("9", "ins", "9"), ("\u00d7", "ins", " * ")),
    (("4", "ins", "4"), ("5", "ins", "5"), ("6", "ins", "6"), ("\u2212", "ins", " - ")),
    (("1", "ins", "1"), ("2", "ins", "2"), ("3", "ins", "3"), ("+", "ins", " + ")),
    (("\u00b1", "act", "negate"), ("0", "ins", "0"), (".", "ins", "."), ("=", "act", "equals")),
)

_STANDARD_RESULT_QSS = "font-family: Consolas, 'Courier New', monospace; font-size: 20pt; font-weight: bold;"
_STANDARD_ENTRY_QSS = "font-family: Consolas, 'Courier New', monospace; font-size: 12pt;"

_LABEL_WIDTH = 125
_FIELD_WIDTH = 150
_ROW_HEIGHT = 34



# ******************************************************************************
#
# ENGINEERING CALCULATOR WINDOW
#
# ******************************************************************************


class EngineeringCalculator(QMainWindow):


    # --------------------------------------------------------------------------
    # WINDOW INITIALIZATION
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Initialize the window and build its controls
    def __init__(self) -> None:
        super().__init__()
        register_tool_window("engineering_calculator", self)
        self.theme_name = resolve_theme(get_saved_theme_pref())
        self.calc_base = "HEX"
        self.calc_memory = 0
        self.calc_last_value = 0
        self.standard_memory = 0.0
        self.standard_last_value = 0.0
        self.setWindowTitle(CALC_APP_NAME)

        icon_ico = resource_path(CALC_ICON_ICO)
        icon_png = resource_path(CALC_ICON_PNG)
        if os.path.exists(icon_ico):
            self.setWindowIcon(QIcon(icon_ico))
        elif os.path.exists(icon_png):
            self.setWindowIcon(QIcon(icon_png))

        self.resize(780, 700)
        self.setMinimumSize(740, 560)
        self._build_actions()
        self._build_ui()
        self.apply_theme(self.theme_name)
        update_owner_status(self, "Ready. DDay Controls Engineering Calculator loaded.")


    # --------------------------------------------------------------------------
    # MENU ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build main window menu actions
    def _build_actions(self) -> None:
        menu_bar = self.menuBar()

        add_file_menu(menu_bar, self)

        add_edit_menu(
            menu_bar, self,
            copy_formatted_callback=self.copy_formatted_from_menu,
            copy_formatted_available=self.copy_formatted_available,
        )

        tools_menu = menu_bar.addMenu("Tools")
        add_available_tool_actions(tools_menu, self, "engineering_calculator")

        options_menu = menu_bar.addMenu("Options")
        add_theme_submenu(options_menu, self)
        add_copy_format_editor_action(options_menu, self)
        add_header_tool_selector_action(options_menu, self, "engineering_calculator")

        add_help_menu(menu_bar, self, CALC_APP_NAME)


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

        header_button, header_callback = companion_header_button(self, "engineering_calculator")

        root.addLayout(
            build_header(
                CALC_APP_NAME,
                "Standard, Programmer, Analog Scaling, Motor & Encoder Utility",
                header_button,
                header_callback,
                logo_file=CALC_ICON_PNG,
                logo_size=48,
            )
        )

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        self.standard_tab = QWidget()
        self.calc_tab = QWidget()
        self.analog_tab = QWidget()
        self.ohms_tab = QWidget()
        self.motor_tab = QWidget()
        self.encoder_tab = QWidget()

        self.tabs.addTab(self.standard_tab, "Standard")
        self.tabs.addTab(self.calc_tab, "Programmer")
        self.tabs.addTab(self.analog_tab, "Analog Scaling")
        self.tabs.addTab(self.ohms_tab, "Ohm's Law")
        self.tabs.addTab(self.motor_tab, "Motor && Drive")
        self.tabs.addTab(self.encoder_tab, "Encoder && Motion")

        self._build_standard_tab()
        self._build_calc_tab()
        self._build_analog_tab()
        self._build_ohms_tab()
        self._build_motor_tab()
        self._build_encoder_tab()

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
    # Give a tab a scrolling page and return the layout to build into
    def scrollable_page(self, tab: QWidget) -> QVBoxLayout:
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        layout = QVBoxLayout(page)
        layout.setSpacing(8)
        return layout

    # ------------------------------------------------------------------------------
    # Add a labeled input field and return it
    def input_row(
        self,
        grid: QGridLayout,
        row: int,
        label: str,
        placeholder: str = "",
        column: int = 0,
    ) -> QLineEdit:
        edit = make_entry()
        edit.setFixedWidth(_FIELD_WIDTH)
        if placeholder:
            edit.setPlaceholderText(placeholder)
        grid.addWidget(form_label(label, _LABEL_WIDTH), row, column)
        grid.addWidget(edit, row, column + 1, Qt.AlignLeft)
        grid.setRowMinimumHeight(row, _ROW_HEIGHT)
        return edit

    # ------------------------------------------------------------------------------
    # Add a labeled read-only output field with a copy button and return it
    def output_row(
        self,
        grid: QGridLayout,
        row: int,
        label: str,
        copy_name: str | None = None,
        formatted: bool = False,
        column_offset: int = 0,
    ) -> QLineEdit:
        edit = make_entry(read_only=True)
        add_labeled_entry_row(
            self,
            grid,
            row,
            label,
            edit,
            copy_name or label,
            self.format_calc_copy if formatted else None,
            _LABEL_WIDTH,
            column_offset,
        )
        grid.setRowMinimumHeight(row, _ROW_HEIGHT)
        return edit

    # ------------------------------------------------------------------------------
    # Add an error label used to report bad input on a tab
    def error_label(self) -> QLabel:
        label = QLabel()
        label.setObjectName("SubTitle")
        label.setWordWrap(True)
        return label

    # ------------------------------------------------------------------------------
    # Return a field's text as a float, or None when blank or unparseable
    @staticmethod
    def field_value(edit: QLineEdit) -> float | None:
        text = edit.text().strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    # ------------------------------------------------------------------------------
    # Return whether a field holds text that is not a usable number
    @classmethod
    def field_invalid(cls, edit: QLineEdit) -> bool:
        return edit.text().strip() != "" and cls.field_value(edit) is None

    # ------------------------------------------------------------------------------
    # Write formatted values into a list of read-only output fields
    @staticmethod
    def show_values(pairs: list[tuple[QLineEdit, float | None]]) -> None:
        for edit, value in pairs:
            edit.setText("" if value is None else format_engineering_number(value))

    # ------------------------------------------------------------------------------
    # Blank a list of output fields
    @staticmethod
    def clear_outputs(fields: list[QLineEdit]) -> None:
        for edit in fields:
            edit.clear()


    # --------------------------------------------------------------------------
    # EDIT MENU COPY FORMAT ACTIONS
    # --------------------------------------------------------------------------


    @property
    def _calc_output_fields(self) -> list[QLineEdit]:
        return [self.c_dec, self.c_hex, self.c_bin, self.c_oct]

    # ------------------------------------------------------------------------------
    # Apply selected copy format to a value
    def format_calc_copy(self, value: str) -> str:
        return format_copy_value(
            value,
            self.calc_copy_format,
            self.calc_copy_prefix,
            self.calc_copy_suffix,
        )

    # ------------------------------------------------------------------------------
    # Refresh this window's copy-format combo while preserving selection
    def refresh_copy_format_options(self) -> None:
        refresh_copy_format_combo(
            self.calc_copy_format,
            self.calc_copy_prefix,
            self.calc_copy_suffix,
        )

    # ------------------------------------------------------------------------------
    # Copy current value using selected copy format
    def copy_formatted_from_menu(self) -> None:
        if self.tabs.currentWidget() != self.calc_tab:
            return

        edit = focused_line_edit(allow_read_only=True)
        if edit not in self._calc_output_fields:
            return

        self.copy_value(self.format_calc_copy(edit.text()))

    # ------------------------------------------------------------------------------
    # Return whether formatted copy is currently available
    def copy_formatted_available(self) -> bool:
        if self.tabs.currentWidget() != self.calc_tab:
            return False

        return focused_line_edit(allow_read_only=True) in self._calc_output_fields


    # --------------------------------------------------------------------------
    # STANDARD TAB
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Standard tab layout
    def _build_standard_tab(self) -> None:
        layout = self.scrollable_page(self.standard_tab)

        display = QGroupBox("Value")
        column = QVBoxLayout(display)
        column.setSpacing(6)

        self.s_expr = make_entry()
        self.s_expr.setText("0")
        self.s_expr.setAlignment(Qt.AlignRight)
        self.s_expr.setStyleSheet(_STANDARD_ENTRY_QSS)
        self.s_expr.setMinimumHeight(38)
        column.addWidget(self.s_expr)

        self.s_result = QLabel("0")
        self.s_result.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.s_result.setStyleSheet(_STANDARD_RESULT_QSS)
        self.s_result.setMinimumHeight(48)
        self.s_result.setTextInteractionFlags(Qt.TextSelectableByMouse)
        column.addWidget(self.s_result)

        self.s_error = self.error_label()
        column.addWidget(self.s_error)

        copy_row = QHBoxLayout()
        copy_row.addStretch(1)
        copy_result = QPushButton("Copy Result")
        copy_result.setFixedWidth(COPY_RESULT_WIDTH)
        copy_result.clicked.connect(lambda: self.copy_value(self.s_result.text()))
        copy_row.addWidget(copy_result)
        column.addLayout(copy_row)

        layout.addWidget(display)
        layout.addWidget(self._build_standard_keypad())

        hint = QLabel(
            "Type into the display or use the keys. Parentheses, ^ for powers and sqrt() all "
            "work when typed. mod is the remainder after division. Results are rounded to 12 "
            "significant digits, so 0.1 + 0.2 reads as 0.3."
        )
        hint.setObjectName("SubTitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)

        self.s_expr.textChanged.connect(self.update_standard)
        self.s_expr.returnPressed.connect(lambda: self.standard_action("equals"))
        self.update_standard()

    # ------------------------------------------------------------------------------
    # Build the Standard memory row and keypad
    def _build_standard_keypad(self) -> QGroupBox:
        box = QGroupBox("Keypad")
        grid = QGridLayout(box)
        grid.setSpacing(5)
        self.s_keys: dict[str, QPushButton] = {}

        memory_row = QHBoxLayout()
        for name in STANDARD_MEMORY_KEYS:
            button = QPushButton(name)
            button.setMinimumHeight(30)
            button.clicked.connect(lambda _=False, a=name: self.standard_memory_action(a))
            memory_row.addWidget(button)
            self.s_keys[name] = button
        grid.addLayout(memory_row, 0, 0, 1, 4)

        for row, keys in enumerate(STANDARD_KEYPAD_ROWS, start=1):
            for column, (label, kind, payload) in enumerate(keys):
                button = QPushButton(label)
                button.setMinimumHeight(38)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                if kind == "ins":
                    button.clicked.connect(lambda _=False, t=payload: self.insert_standard(t))
                else:
                    button.clicked.connect(lambda _=False, a=payload: self.standard_action(a))

                grid.addWidget(button, row, column)
                self.s_keys[label] = button

        for column in range(4):
            grid.setColumnStretch(column, 1)

        return box

    # ------------------------------------------------------------------------------
    # Append text to the Standard display
    def insert_standard(self, text: str) -> None:
        # A lone leading zero is a placeholder, not something to build on -
        # except before a point, where "0." is exactly what is wanted.
        if self.s_expr.text() == "0" and (text[:1].isdigit() or text[:1] == "("):
            self.s_expr.setText("")

        self.s_expr.setText(self.s_expr.text() + text)

    # ------------------------------------------------------------------------------
    # Run a keypad action against the Standard display
    def standard_action(self, action: str) -> None:
        text = self.s_expr.text()

        if action == "clear":
            self.s_expr.setText("0")
        elif action == "clearentry":
            # CE drops the number being typed, leaving the rest of the sum.
            self.s_expr.setText(re.sub(r"[\d.]+\s*$", "", text).strip() or "0")
        elif action == "back":
            self.s_expr.setText(text[:-1].strip() or "0")
        elif action == "negate":
            wrapped = re.fullmatch(r"-\((.*)\)", text)
            self.s_expr.setText(wrapped.group(1) if wrapped else f"-({text})")
        elif action == "sqrt":
            self.s_expr.setText(f"sqrt({text})")
        elif action == "square":
            self.s_expr.setText(f"({text})^2")
        elif action == "inverse":
            self.s_expr.setText(f"1/({text})")
        elif action == "equals":
            try:
                self.s_expr.setText(format_decimal_result(evaluate_decimal(text)))
            except CalcError as error:
                self.s_error.setText(str(error))

    # ------------------------------------------------------------------------------
    # Run a memory key against the stored Standard value
    def standard_memory_action(self, action: str) -> None:
        if action == "MC":
            self.standard_memory = 0.0
            update_owner_status(self, "Memory cleared.")
            return

        if action == "MR":
            self.insert_standard(format_decimal_result(self.standard_memory))
            return

        if action == "MS":
            self.standard_memory = self.standard_last_value
        elif action == "M+":
            self.standard_memory += self.standard_last_value
        else:
            self.standard_memory -= self.standard_last_value

        update_owner_status(self, f"Memory {format_decimal_result(self.standard_memory)}.")

    # ------------------------------------------------------------------------------
    # Recalculate the Standard tab from the display
    def update_standard(self) -> None:
        text = self.s_expr.text()

        if not text.strip():
            self.s_result.setText("0")
            self.standard_last_value = 0.0
            self.s_error.setText("")
            return

        try:
            self.standard_last_value = evaluate_decimal(text)
        except CalcError as error:
            self.s_result.setText("—")
            self.s_error.setText(str(error))
            return

        self.s_result.setText(format_decimal_result(self.standard_last_value))
        self.s_error.setText("")


    # --------------------------------------------------------------------------
    # BASE MATH TAB
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Base Math tab layout
    def _build_calc_tab(self) -> None:
        layout = self.scrollable_page(self.calc_tab)

        layout.addWidget(self._build_calc_display())
        layout.addWidget(self._build_calc_config())
        layout.addWidget(self._build_calc_keypad())

        hint = QLabel(
            "Whole numbers only - bases and word sizes have no meaning for 2.5, so the decimal "
            "point is disabled here. Use the Standard tab for decimal arithmetic. Operators "
            "follow C precedence; division truncates toward zero and the remainder takes the "
            "sign of the dividend, matching structured text. Every step wraps to the word size."
        )
        hint.setObjectName("SubTitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)

        self.set_calc_base("HEX")

    # ------------------------------------------------------------------------------
    # Build the display and the live value in every base
    def _build_calc_display(self) -> QGroupBox:
        box = QGroupBox("Value")
        column = QVBoxLayout(box)
        column.setSpacing(8)

        self.c_expr = make_entry()
        self.c_expr.setText("0")
        self.c_expr.setAlignment(Qt.AlignRight)
        self.c_expr.setStyleSheet(_DISPLAY_QSS)
        self.c_expr.setMinimumHeight(52)
        column.addWidget(self.c_expr)

        rows = QGridLayout()
        rows.setColumnStretch(1, 1)
        rows.setVerticalSpacing(4)

        self.c_base_group = QButtonGroup(self)
        self.c_base_buttons: dict[str, QRadioButton] = {}
        self.c_value_fields: dict[str, QLineEdit] = {}

        for row, base in enumerate(CALC_BASE_ORDER):
            # A radio button is the honest control here: picking the base the
            # display is read in is exactly a one-of-four choice.
            selector = QRadioButton(base)
            selector.setFixedWidth(70)
            self.c_base_group.addButton(selector)
            self.c_base_buttons[base] = selector

            field = make_entry(read_only=True)
            field.setStyleSheet(_MONO_QSS)
            self.c_value_fields[base] = field

            copy = QPushButton("Copy")
            copy.setFixedWidth(COPY_BUTTON_WIDTH)
            copy.clicked.connect(
                lambda _=False, e=field: self.copy_value(self.format_calc_copy(e.text()))
            )

            rows.addWidget(selector, row, 0)
            rows.addWidget(field, row, 1)
            rows.addWidget(copy, row, 2)
            rows.setRowMinimumHeight(row, _ROW_HEIGHT)

            selector.clicked.connect(lambda _=False, b=base: self.set_calc_base(b))

        column.addLayout(rows)

        # Kept for the Edit menu's formatted-copy action.
        self.c_hex = self.c_value_fields["HEX"]
        self.c_dec = self.c_value_fields["DEC"]
        self.c_oct = self.c_value_fields["OCT"]
        self.c_bin = self.c_value_fields["BIN"]

        self.c_expr.textChanged.connect(self.update_calc)
        self.c_expr.returnPressed.connect(lambda: self.calc_action("equals"))
        return box

    # ------------------------------------------------------------------------------
    # Build the word size, signed mode and copy format controls
    def _build_calc_config(self) -> QGroupBox:
        box = QGroupBox("Word")
        grid = QGridLayout(box)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        self.c_width = QComboBox()
        self.c_width.addItems(list(CALC_WORD_SIZES.keys()))
        self.c_width.setCurrentText("WORD  (16-bit)")
        self.c_width.setFixedWidth(_FIELD_WIDTH)

        self.c_signed = QCheckBox("Signed")

        grid.addWidget(form_label("Word Size", _LABEL_WIDTH), 0, 0)
        grid.addWidget(self.c_width, 0, 1, Qt.AlignLeft)
        grid.addWidget(self.c_signed, 0, 2, Qt.AlignLeft)

        self.c_range = QLabel()
        self.c_range.setObjectName("SubTitle")
        grid.addWidget(self.c_range, 1, 1, 1, 2)

        self.c_error = self.error_label()
        grid.addWidget(self.c_error, 2, 0, 1, 4)

        self.calc_copy_format = QComboBox()
        self.calc_copy_format.addItems(list(COPY_FORMATS.keys()))
        self.calc_copy_format.setCurrentText("None")
        self.calc_copy_format.setFixedWidth(_FIELD_WIDTH)

        self.calc_copy_prefix = QLineEdit()
        self.calc_copy_prefix.setFixedWidth(80)
        self.calc_copy_prefix.setObjectName("LockedDisplayLineEdit")

        self.calc_copy_suffix = QLineEdit()
        self.calc_copy_suffix.setFixedWidth(80)
        self.calc_copy_suffix.setObjectName("LockedDisplayLineEdit")

        format_row = QHBoxLayout()
        format_row.addWidget(form_label("Copy Format", _LABEL_WIDTH))
        format_row.addWidget(self.calc_copy_format)
        format_row.addWidget(form_label("Prefix", 45))
        format_row.addWidget(self.calc_copy_prefix)
        format_row.addWidget(form_label("Suffix", 45))
        format_row.addWidget(self.calc_copy_suffix)
        format_row.addStretch(1)
        grid.addLayout(format_row, 3, 0, 1, 4)

        grid.setColumnStretch(3, 1)
        connect_copy_format_controls(self.calc_copy_format, self.calc_copy_prefix, self.calc_copy_suffix)

        self.c_width.currentTextChanged.connect(self.update_calc)
        self.c_signed.stateChanged.connect(self.update_calc)
        return box

    # ------------------------------------------------------------------------------
    # Build the memory, bitwise and main keypads
    def _build_calc_keypad(self) -> QGroupBox:
        box = QGroupBox("Keypad")
        grid = QGridLayout(box)
        grid.setSpacing(5)
        self.c_digit_buttons: dict[str, QPushButton] = {}

        def add(row: int, column: int, label: str, kind: str, payload: str, span: int = 1) -> None:
            button = QPushButton(label)
            button.setMinimumHeight(38)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            if kind == "off":
                # Shown but dead: whole numbers only in this mode, and saying
                # so beats leaving an unexplained hole in the keypad.
                button.setEnabled(False)
                button.setToolTip("Whole numbers only here - use the Standard tab for decimals")
            elif kind == "digit":
                self.c_digit_buttons[payload] = button
                button.clicked.connect(lambda _=False, t=payload: self.insert_calc(t))
            elif kind == "ins":
                button.clicked.connect(lambda _=False, t=payload: self.insert_calc(t))
            elif kind == "act":
                button.clicked.connect(lambda _=False, a=payload: self.calc_action(a))
            else:
                button.clicked.connect(lambda _=False, a=payload: self.calc_memory_action(a))

            grid.addWidget(button, row, column, 1, span)

        for column, name in enumerate(CALC_MEMORY_KEYS):
            add(0, column, name, "mem", name)

        for column, (label, text) in enumerate(CALC_BITWISE_KEYS):
            add(1, column, label, "ins", text)

        for row, keys in enumerate(CALC_KEYPAD_ROWS, start=2):
            for column, (label, kind, payload) in enumerate(keys):
                add(row, column, label, kind, payload)

        for column in range(5):
            grid.setColumnStretch(column, 1)

        return box

    # ------------------------------------------------------------------------------
    # Return the selected calculator word size and signed mode
    def calc_bits_signed(self) -> tuple[int, bool]:
        return calc_bit_width(self.c_width.currentText()), self.c_signed.isChecked()

    # ------------------------------------------------------------------------------
    # Switch the base the display is read in, carrying the value across
    def set_calc_base(self, base: str) -> None:
        bits, signed = self.calc_bits_signed()

        if base != getattr(self, "calc_base", None):
            # Convert rather than re-read the same characters in a base where
            # they may not even be digits — 1F is not a decimal number.
            try:
                value, _ = evaluate_expression(self.c_expr.text(), self.calc_base, bits, signed)
                self.c_expr.blockSignals(True)
                self.c_expr.setText(literal_in_base(value, base, bits))
                self.c_expr.blockSignals(False)
            except (CalcError, AttributeError):
                pass   # Text that does not parse is left alone for the user to fix.

        self.calc_base = base
        self.c_base_buttons[base].setChecked(True)

        # Grey out digits that do not exist in the base being entered.
        allowed = CALC_BASE_DIGIT_COUNT[base]
        for digit, button in self.c_digit_buttons.items():
            button.setEnabled(CALC_DIGIT_ORDER.index(digit) < allowed)

        self.update_calc()

    # ------------------------------------------------------------------------------
    # Append text to the display
    def insert_calc(self, text: str) -> None:
        # A lone leading zero is a placeholder, not something to build on.
        if self.c_expr.text() == "0" and (text[:1].isalnum() or text[:1] in "(~"):
            self.c_expr.setText("")

        self.c_expr.setText(self.c_expr.text() + text)

    # ------------------------------------------------------------------------------
    # Run a keypad action against the display
    def calc_action(self, action: str) -> None:
        text = self.c_expr.text()

        if action == "clear":
            self.c_expr.setText("0")
        elif action == "back":
            self.c_expr.setText(re.sub(r"\s*\S\s*$", "", text) or "0")
        elif action == "negate":
            # Wrap or unwrap, so pressing it twice returns the original text.
            wrapped = re.fullmatch(r"-\((.*)\)", text)
            self.c_expr.setText(wrapped.group(1) if wrapped else f"-({text})")
        elif action == "equals":
            bits, signed = self.calc_bits_signed()
            try:
                value, _ = evaluate_expression(text, self.calc_base, bits, signed)
            except CalcError as error:
                self.c_error.setText(str(error))
                return
            self.c_expr.setText(literal_in_base(value, self.calc_base, bits))

    # ------------------------------------------------------------------------------
    # Run a memory key against the stored value
    def calc_memory_action(self, action: str) -> None:
        bits, signed = self.calc_bits_signed()

        if action == "MC":
            self.calc_memory = 0
            update_owner_status(self, "Memory cleared.")
            return

        if action == "MR":
            self.insert_calc(literal_in_base(self.calc_memory, self.calc_base, bits))
            return

        if action == "MS":
            self.calc_memory = self.calc_last_value
        elif action == "M+":
            self.calc_memory = wrap_to_word(self.calc_memory + self.calc_last_value, bits, signed)
        else:
            self.calc_memory = wrap_to_word(self.calc_memory - self.calc_last_value, bits, signed)

        update_owner_status(self, f"Memory {self.calc_memory}.")

    # ------------------------------------------------------------------------------
    # Recalculate the Base Math tab from the display
    def update_calc(self) -> None:
        bits, signed = self.calc_bits_signed()
        low, high = range_info(bits, signed)
        self.c_range.setText(f"{bits}-bit range {low:,} to {high:,}")

        if not self.c_expr.text().strip():
            for base, field in self.c_value_fields.items():
                field.setText("0")
            self.calc_last_value = 0
            self.c_error.setText("")
            return

        try:
            value, overflow = evaluate_expression(self.c_expr.text(), self.calc_base, bits, signed)
        except CalcError as error:
            for field in self.c_value_fields.values():
                field.setText("—")
            self.c_error.setText(str(error))
            return

        self.calc_last_value = value
        for base, field in self.c_value_fields.items():
            field.setText(format_integer_value(value, base, bits))

        self.c_error.setText(
            f"Result wrapped to {bits} bits - the full value did not fit." if overflow else ""
        )

    # ------------------------------------------------------------------------------
    # Clear the Base Math tab
    def clear_calc(self) -> None:
        self.calc_action("clear")
        update_owner_status(self, "Base Math tab cleared.")


    # --------------------------------------------------------------------------
    # ANALOG SCALING TAB
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Analog Scaling tab layout
    def _build_analog_tab(self) -> None:
        layout = self.scrollable_page(self.analog_tab)

        config = QGroupBox("Ranges")
        cfg = QGridLayout(config)
        cfg.setHorizontalSpacing(10)
        cfg.setVerticalSpacing(8)

        self.a_direction = QComboBox()
        self.a_direction.addItems(["Raw to Units", "Units to Raw"])
        self.a_direction.setFixedWidth(_FIELD_WIDTH)
        cfg.addWidget(form_label("Direction", _LABEL_WIDTH), 0, 0)
        cfg.addWidget(self.a_direction, 0, 1, Qt.AlignLeft)

        self.a_preset = QComboBox()
        self.a_preset.addItems([
            f"{name}  ({low:g} to {high:g})"
            for name, (low, high, _) in ANALOG_RAW_PRESETS.items()
        ] + ["Custom"])
        cfg.addWidget(form_label("Raw Preset", _LABEL_WIDTH), 1, 0)
        cfg.addWidget(self.a_preset, 1, 1, 1, 3)

        self.a_preset_note = QLabel()
        self.a_preset_note.setObjectName("SubTitle")
        cfg.addWidget(self.a_preset_note, 2, 1, 1, 3)

        self.a_raw_low = self.input_row(cfg, 3, "Raw Low")
        self.a_raw_high = self.input_row(cfg, 3, "Raw High", column=2)
        self.a_eu_low = self.input_row(cfg, 4, "Units Low", "0")
        self.a_eu_high = self.input_row(cfg, 4, "Units High", "100", column=2)
        self.a_value = self.input_row(cfg, 5, "Raw Value", "Enter a value")

        self.a_clamp = QCheckBox("Clamp to range")
        cfg.addWidget(self.a_clamp, 5, 2, 1, 2, Qt.AlignLeft)

        cfg.setColumnStretch(4, 1)
        layout.addWidget(config)

        results = QGroupBox("Result")
        res = QGridLayout(results)
        res.setColumnStretch(1, 1)
        res.setVerticalSpacing(6)

        self.a_result = self.output_row(res, 0, "Scaled Value")
        self.a_percent = self.output_row(res, 1, "Percent of Span")
        self.a_resolution = self.output_row(res, 2, "Units per Count")
        self.a_raw_span = self.output_row(res, 3, "Raw Span")
        self.a_rounded = self.output_row(res, 4, "Rounded Raw")

        self.a_error = self.error_label()
        res.addWidget(self.a_error, 5, 0, 1, 3)
        layout.addWidget(results)

        clear = QPushButton("Clear")
        clear.setFixedWidth(CLEAR_BUTTON_WIDTH)
        clear.clicked.connect(self.clear_analog)
        layout.addWidget(clear, 0, Qt.AlignLeft)
        layout.addStretch(1)

        self.a_preset.currentIndexChanged.connect(self.apply_analog_preset)
        self.a_direction.currentTextChanged.connect(self.update_analog)
        self.a_clamp.stateChanged.connect(self.update_analog)

        for edit in (self.a_raw_low, self.a_raw_high, self.a_eu_low,
                     self.a_eu_high, self.a_value):
            edit.textChanged.connect(self.update_analog)

        # Hand-editing a raw limit means the preset no longer describes it.
        for edit in (self.a_raw_low, self.a_raw_high):
            edit.textEdited.connect(self.select_custom_preset)

        self.apply_analog_preset()

    # ------------------------------------------------------------------------------
    # Fill the raw limits from the selected preset
    def apply_analog_preset(self) -> None:
        index = self.a_preset.currentIndex()

        if index >= len(ANALOG_RAW_PRESETS):
            self.a_preset_note.setText("Enter the raw range by hand.")
            return

        low, high, note = list(ANALOG_RAW_PRESETS.values())[index]
        self.a_preset_note.setText(note)

        for edit, value in ((self.a_raw_low, low), (self.a_raw_high, high)):
            edit.blockSignals(True)
            edit.setText(f"{value:g}")
            edit.blockSignals(False)

        self.update_analog()

    # ------------------------------------------------------------------------------
    # Switch the preset combo to Custom without refilling the limits
    def select_custom_preset(self) -> None:
        if self.a_preset.currentIndex() < len(ANALOG_RAW_PRESETS):
            self.a_preset.blockSignals(True)
            self.a_preset.setCurrentIndex(self.a_preset.count() - 1)
            self.a_preset.blockSignals(False)
            self.a_preset_note.setText("Enter the raw range by hand.")

    # ------------------------------------------------------------------------------
    # Recalculate the Analog Scaling tab
    def update_analog(self) -> None:
        to_units = self.a_direction.currentText() == "Raw to Units"
        self.a_value.setPlaceholderText("Enter a raw count" if to_units else "Enter a value in units")

        outputs = [self.a_result, self.a_percent, self.a_resolution,
                   self.a_raw_span, self.a_rounded]

        raw_low = self.field_value(self.a_raw_low)
        raw_high = self.field_value(self.a_raw_high)
        eu_low = 0.0 if not self.a_eu_low.text().strip() else self.field_value(self.a_eu_low)
        eu_high = 100.0 if not self.a_eu_high.text().strip() else self.field_value(self.a_eu_high)
        value = self.field_value(self.a_value)

        if None in (raw_low, raw_high, eu_low, eu_high):
            self.clear_outputs(outputs)
            self.a_error.setText("Enter numbers for both ranges.")
            return

        if value is None:
            self.clear_outputs(outputs)
            self.a_error.setText("That value is not a number." if self.a_value.text().strip() else "")
            return

        clamp = self.a_clamp.isChecked()

        try:
            if to_units:
                out = scale_analog(value, raw_low, raw_high, eu_low, eu_high, clamp)
                scaled, rounded = out["eu"], None
            else:
                out = unscale_analog(value, raw_low, raw_high, eu_low, eu_high, clamp)
                scaled, rounded = out["raw"], float(out["raw_rounded"])

            # Resolution and span describe the ranges, not the direction, so
            # they are the same figures either way round.
            raw_span = raw_high - raw_low
            self.show_values([
                (self.a_result, scaled),
                (self.a_percent, out["percent"]),
                (self.a_resolution, (eu_high - eu_low) / raw_span if raw_span else None),
                (self.a_raw_span, raw_span),
                (self.a_rounded, rounded),
            ])
        except CalcError as error:
            self.clear_outputs(outputs)
            self.a_error.setText(str(error))
            return

        self.a_error.setText(self.analog_range_note(out, clamp))

    # ------------------------------------------------------------------------------
    # Return the out-of-range warning for a scaling result
    @staticmethod
    def analog_range_note(out: dict, clamp: bool) -> str:
        if not out["under_range"] and not out["over_range"]:
            return ""

        side = "below" if out["under_range"] else "above"
        if clamp:
            return f"Input is {side} range - result clamped to the limit."
        return f"Input is {side} range - result is extrapolated past the limit."

    # ------------------------------------------------------------------------------
    # Clear the Analog Scaling tab
    def clear_analog(self) -> None:
        self.a_value.clear()
        self.clear_outputs([self.a_result, self.a_percent, self.a_resolution,
                            self.a_raw_span, self.a_rounded])
        self.a_error.setText("")
        update_owner_status(self, "Analog Scaling tab cleared.")


    # --------------------------------------------------------------------------
    # OHM'S LAW TAB
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Ohm's Law tab layout
    def _build_ohms_tab(self) -> None:
        layout = self.scrollable_page(self.ohms_tab)

        entry = QGroupBox("Known Values")
        grid = QGridLayout(entry)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        note = QLabel("Fill in any two - the other two are solved for you.")
        note.setObjectName("SubTitle")
        grid.addWidget(note, 0, 0, 1, 4)

        self.o_volts = self.input_row(grid, 1, "Voltage (V)")
        self.o_amps = self.input_row(grid, 1, "Current (A)", column=2)
        self.o_ohms = self.input_row(grid, 2, "Resistance (R)")
        self.o_watts = self.input_row(grid, 2, "Power (W)", column=2)
        grid.setColumnStretch(4, 1)
        layout.addWidget(entry)

        results = QGroupBox("Solved")
        res = QGridLayout(results)
        res.setColumnStretch(1, 1)
        res.setVerticalSpacing(6)

        self.o_out_volts = self.output_row(res, 0, "Voltage (V)")
        self.o_out_amps = self.output_row(res, 1, "Current (A)")
        self.o_out_ohms = self.output_row(res, 2, "Resistance (R)")
        self.o_out_watts = self.output_row(res, 3, "Power (W)")

        self.o_error = self.error_label()
        res.addWidget(self.o_error, 4, 0, 1, 3)
        layout.addWidget(results)

        clear = QPushButton("Clear")
        clear.setFixedWidth(CLEAR_BUTTON_WIDTH)
        clear.clicked.connect(self.clear_ohms)
        layout.addWidget(clear, 0, Qt.AlignLeft)
        layout.addStretch(1)

        for edit in (self.o_volts, self.o_amps, self.o_ohms, self.o_watts):
            edit.textChanged.connect(self.update_ohms)

        self.update_ohms()

    # ------------------------------------------------------------------------------
    # Recalculate the Ohm's Law tab
    def update_ohms(self) -> None:
        inputs = [self.o_volts, self.o_amps, self.o_ohms, self.o_watts]
        outputs = [self.o_out_volts, self.o_out_amps, self.o_out_ohms, self.o_out_watts]

        filled = [edit for edit in inputs if edit.text().strip()]

        if any(self.field_invalid(edit) for edit in filled):
            self.clear_outputs(outputs)
            self.o_error.setText("Those entries must be numbers.")
            return

        if len(filled) != 2:
            self.clear_outputs(outputs)
            self.o_error.setText(
                "" if len(filled) < 2 else "Too many values - clear one to solve."
            )
            return

        try:
            out = solve_ohms_law(
                self.field_value(self.o_volts),
                self.field_value(self.o_amps),
                self.field_value(self.o_ohms),
                self.field_value(self.o_watts),
            )
        except CalcError as error:
            self.clear_outputs(outputs)
            self.o_error.setText(str(error))
            return

        self.show_values([
            (self.o_out_volts, out["volts"]),
            (self.o_out_amps, out["amps"]),
            (self.o_out_ohms, out["ohms"]),
            (self.o_out_watts, out["watts"]),
        ])
        self.o_error.setText("")

    # ------------------------------------------------------------------------------
    # Clear the Ohm's Law tab
    def clear_ohms(self) -> None:
        clear_line_edits([self.o_volts, self.o_amps, self.o_ohms, self.o_watts])
        update_owner_status(self, "Ohm's Law tab cleared.")


    # --------------------------------------------------------------------------
    # MOTOR & DRIVE TAB
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Motor & Drive tab layout
    def _build_motor_tab(self) -> None:
        layout = self.scrollable_page(self.motor_tab)

        # ---- Power and torque ----
        torque_box = QGroupBox("Power && Torque")
        grid = QGridLayout(torque_box)
        grid.setColumnStretch(5, 1)
        self.m_hp = self.input_row(grid, 0, "Power (HP)", "10")
        self.m_rpm = self.input_row(grid, 1, "Speed (RPM)", "1750")
        self.m_torque_lbft = self.output_row(grid, 0, "Torque (lb-ft)", column_offset=2)
        self.m_torque_nm = self.output_row(grid, 1, "Torque (N-m)", column_offset=2)
        self.m_kw = self.output_row(grid, 2, "Power (kW)", column_offset=2)
        self.m_torque_error = self.error_label()
        grid.addWidget(self.m_torque_error, 3, 0, 1, 5)
        layout.addWidget(torque_box)

        # ---- Synchronous speed and slip ----
        slip_box = QGroupBox("Synchronous Speed && Slip")
        grid = QGridLayout(slip_box)
        grid.setColumnStretch(5, 1)
        self.m_hz = self.input_row(grid, 0, "Line Freq (Hz)", "60")
        self.m_poles = self.input_row(grid, 1, "Poles", "4")
        self.m_actual = self.input_row(grid, 2, "Nameplate RPM", "1750")
        self.m_sync = self.output_row(grid, 0, "Sync Speed (RPM)", column_offset=2)
        self.m_slip = self.output_row(grid, 1, "Slip (%)", column_offset=2)
        self.m_slip_rpm = self.output_row(grid, 2, "Slip (RPM)", column_offset=2)
        self.m_slip_error = self.error_label()
        grid.addWidget(self.m_slip_error, 3, 0, 1, 5)
        layout.addWidget(slip_box)

        # ---- Circuit power ----
        power_box = QGroupBox("Circuit Power")
        grid = QGridLayout(power_box)
        grid.setColumnStretch(5, 1)
        self.m_phase = QComboBox()
        self.m_phase.addItems(["Three phase", "Single phase"])
        self.m_phase.setFixedWidth(_FIELD_WIDTH)
        grid.addWidget(form_label("Phase", _LABEL_WIDTH), 0, 0)
        grid.addWidget(self.m_phase, 0, 1, Qt.AlignLeft)
        self.m_volts = self.input_row(grid, 1, "Volts", "480")
        self.m_amps = self.input_row(grid, 2, "Amps", "100")
        self.m_pf = self.input_row(grid, 3, "Power Factor", "0.85")
        self.m_out_kw = self.output_row(grid, 1, "Real (kW)", column_offset=2)
        self.m_out_kva = self.output_row(grid, 2, "Apparent (kVA)", column_offset=2)
        self.m_out_kvar = self.output_row(grid, 3, "Reactive (kVAR)", column_offset=2)
        self.m_power_error = self.error_label()
        grid.addWidget(self.m_power_error, 4, 0, 1, 5)
        layout.addWidget(power_box)

        # ---- Full-load current ----
        fla_box = QGroupBox("Full-Load Current")
        grid = QGridLayout(fla_box)
        grid.setColumnStretch(5, 1)
        self.m_fla_hp = self.input_row(grid, 0, "Rating (HP)", "10")
        self.m_fla_volts = self.input_row(grid, 1, "Volts", "480")
        self.m_fla_pf = self.input_row(grid, 2, "Power Factor", "0.85")
        self.m_fla_eff = self.input_row(grid, 3, "Efficiency", "0.92")
        self.m_fla = self.output_row(grid, 0, "Current (A)", column_offset=2)
        self.m_fla_input = self.output_row(grid, 1, "Input (kW)", column_offset=2)
        self.m_fla_error = self.error_label()
        grid.addWidget(self.m_fla_error, 4, 0, 1, 5)

        fla_note = QLabel(
            "Calculated from the motor's output rating. Size conductors and overloads "
            "from the NEC full-load current tables, which run higher than the "
            "calculated value."
        )
        fla_note.setObjectName("SubTitle")
        fla_note.setWordWrap(True)
        grid.addWidget(fla_note, 5, 0, 1, 5)
        layout.addWidget(fla_box)

        # ---- Gearbox ----
        gear_box = QGroupBox("Gearbox")
        grid = QGridLayout(gear_box)
        grid.setColumnStretch(5, 1)
        self.m_gear_rpm = self.input_row(grid, 0, "Input RPM", "1750")
        self.m_gear_ratio = self.input_row(grid, 1, "Ratio : 1", "10")
        self.m_gear_torque = self.input_row(grid, 2, "Input Torque", "30")
        self.m_gear_eff = self.input_row(grid, 3, "Efficiency", "0.95")
        self.m_gear_out_rpm = self.output_row(grid, 0, "Output RPM", column_offset=2)
        self.m_gear_out_torque = self.output_row(grid, 1, "Output Torque", column_offset=2)
        self.m_gear_error = self.error_label()
        grid.addWidget(self.m_gear_error, 4, 0, 1, 5)
        layout.addWidget(gear_box)

        layout.addStretch(1)

        for edit in (self.m_hp, self.m_rpm):
            edit.textChanged.connect(self.update_motor_torque)
        for edit in (self.m_hz, self.m_poles, self.m_actual):
            edit.textChanged.connect(self.update_motor_slip)
        for edit in (self.m_volts, self.m_amps, self.m_pf):
            edit.textChanged.connect(self.update_motor_power)
        for edit in (self.m_fla_hp, self.m_fla_volts, self.m_fla_pf, self.m_fla_eff):
            edit.textChanged.connect(self.update_motor_fla)
        for edit in (self.m_gear_rpm, self.m_gear_ratio, self.m_gear_torque, self.m_gear_eff):
            edit.textChanged.connect(self.update_motor_gearbox)

        self.m_phase.currentTextChanged.connect(self.update_motor_power)
        self.m_phase.currentTextChanged.connect(self.update_motor_fla)

    # ------------------------------------------------------------------------------
    # Return whether the circuit is configured as three phase
    def motor_three_phase(self) -> bool:
        return self.m_phase.currentText() == "Three phase"

    # ------------------------------------------------------------------------------
    # Recalculate motor torque from power and speed
    def update_motor_torque(self) -> None:
        outputs = [self.m_torque_lbft, self.m_torque_nm, self.m_kw]
        hp = self.field_value(self.m_hp)
        rpm = self.field_value(self.m_rpm)

        if hp is None or rpm is None:
            self.clear_outputs(outputs)
            self.m_torque_error.setText(
                "Enter numbers." if self.field_invalid(self.m_hp) or self.field_invalid(self.m_rpm) else ""
            )
            return

        try:
            out = torque_from_power(hp, rpm)
        except CalcError as error:
            self.clear_outputs(outputs)
            self.m_torque_error.setText(str(error))
            return

        self.show_values([
            (self.m_torque_lbft, out["lb_ft"]),
            (self.m_torque_nm, out["n_m"]),
            (self.m_kw, out["kw"]),
        ])
        self.m_torque_error.setText("")

    # ------------------------------------------------------------------------------
    # Recalculate synchronous speed and slip
    def update_motor_slip(self) -> None:
        outputs = [self.m_sync, self.m_slip, self.m_slip_rpm]
        hertz = self.field_value(self.m_hz)
        poles = self.field_value(self.m_poles)
        actual = self.field_value(self.m_actual)

        if hertz is None or poles is None:
            self.clear_outputs(outputs)
            self.m_slip_error.setText(
                "Enter numbers." if self.field_invalid(self.m_hz) or self.field_invalid(self.m_poles) else ""
            )
            return

        if poles != int(poles):
            self.clear_outputs(outputs)
            self.m_slip_error.setText("Pole count must be a whole number.")
            return

        try:
            sync = synchronous_speed(hertz, int(poles))
            slip = slip_percent(sync, actual) if actual is not None else None
        except CalcError as error:
            self.clear_outputs(outputs)
            self.m_slip_error.setText(str(error))
            return

        self.show_values([
            (self.m_sync, sync),
            (self.m_slip, slip),
            (self.m_slip_rpm, None if actual is None else sync - actual),
        ])
        self.m_slip_error.setText("")

    # ------------------------------------------------------------------------------
    # Recalculate circuit power
    def update_motor_power(self) -> None:
        outputs = [self.m_out_kw, self.m_out_kva, self.m_out_kvar]
        volts = self.field_value(self.m_volts)
        amps = self.field_value(self.m_amps)
        power_factor = self.field_value(self.m_pf)

        if None in (volts, amps, power_factor):
            self.clear_outputs(outputs)
            self.m_power_error.setText(
                "Enter numbers."
                if any(self.field_invalid(e) for e in (self.m_volts, self.m_amps, self.m_pf))
                else ""
            )
            return

        try:
            out = motor_power(volts, amps, power_factor, self.motor_three_phase())
        except CalcError as error:
            self.clear_outputs(outputs)
            self.m_power_error.setText(str(error))
            return

        self.show_values([
            (self.m_out_kw, out["kw"]),
            (self.m_out_kva, out["kva"]),
            (self.m_out_kvar, out["kvar"]),
        ])
        self.m_power_error.setText("")

    # ------------------------------------------------------------------------------
    # Recalculate motor full-load current
    def update_motor_fla(self) -> None:
        outputs = [self.m_fla, self.m_fla_input]
        fields = (self.m_fla_hp, self.m_fla_volts, self.m_fla_pf, self.m_fla_eff)
        hp, volts, power_factor, efficiency = (self.field_value(e) for e in fields)

        if None in (hp, volts, power_factor, efficiency):
            self.clear_outputs(outputs)
            self.m_fla_error.setText(
                "Enter numbers." if any(self.field_invalid(e) for e in fields) else ""
            )
            return

        try:
            amps = full_load_amps(hp, volts, power_factor, efficiency, self.motor_three_phase())
        except CalcError as error:
            self.clear_outputs(outputs)
            self.m_fla_error.setText(str(error))
            return

        self.show_values([
            (self.m_fla, amps),
            (self.m_fla_input, hp_to_kw(hp) / efficiency),
        ])
        self.m_fla_error.setText("")

    # ------------------------------------------------------------------------------
    # Recalculate gearbox output
    def update_motor_gearbox(self) -> None:
        outputs = [self.m_gear_out_rpm, self.m_gear_out_torque]
        rpm = self.field_value(self.m_gear_rpm)
        ratio = self.field_value(self.m_gear_ratio)
        torque = self.field_value(self.m_gear_torque)
        efficiency = 1.0 if not self.m_gear_eff.text().strip() else self.field_value(self.m_gear_eff)

        if rpm is None or ratio is None or efficiency is None:
            self.clear_outputs(outputs)
            self.m_gear_error.setText(
                "Enter numbers."
                if any(self.field_invalid(e) for e in (self.m_gear_rpm, self.m_gear_ratio, self.m_gear_eff))
                else ""
            )
            return

        try:
            out = gearbox_output(rpm, ratio, torque or 0.0, efficiency)
        except CalcError as error:
            self.clear_outputs(outputs)
            self.m_gear_error.setText(str(error))
            return

        self.show_values([
            (self.m_gear_out_rpm, out["output_rpm"]),
            (self.m_gear_out_torque, None if torque is None else out["output_torque"]),
        ])
        self.m_gear_error.setText("")


    # --------------------------------------------------------------------------
    # ENCODER & MOTION TAB
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Build the Encoder & Motion tab layout
    def _build_encoder_tab(self) -> None:
        layout = self.scrollable_page(self.encoder_tab)

        drive = QGroupBox("Drive Train")
        grid = QGridLayout(drive)
        grid.setColumnStretch(4, 1)

        self.e_ppr = self.input_row(grid, 0, "Pulses per Rev", "1024")

        self.e_quad = QComboBox()
        self.e_quad.addItems(list(QUADRATURE_MODES.keys()))
        self.e_quad.setCurrentText("x4 (both edges, A and B)")
        grid.addWidget(form_label("Decode", _LABEL_WIDTH), 1, 0)
        grid.addWidget(self.e_quad, 1, 1, 1, 3)

        self.e_mech = QComboBox()
        self.e_mech.addItems(list(MECHANISM_TYPES))
        grid.addWidget(form_label("Mechanism", _LABEL_WIDTH), 2, 0)
        grid.addWidget(self.e_mech, 2, 1, 1, 3)

        self.e_dim = self.input_row(grid, 3, "Pitch per Rev", "5")
        self.e_gear = self.input_row(grid, 4, "Gear Ratio : 1", "1")

        travel_note = QLabel("Travel figures come back in whatever unit the pitch or diameter is entered in.")
        travel_note.setObjectName("SubTitle")
        travel_note.setWordWrap(True)
        grid.addWidget(travel_note, 5, 0, 1, 5)
        layout.addWidget(drive)

        results = QGroupBox("Resolution")
        res = QGridLayout(results)
        res.setColumnStretch(1, 1)
        res.setVerticalSpacing(6)

        self.e_counts = self.output_row(res, 0, "Counts per Rev")
        self.e_travel = self.output_row(res, 1, "Travel per Rev")
        self.e_per_count = self.output_row(res, 2, "Distance per Count")
        self.e_per_unit = self.output_row(res, 3, "Counts per Unit")

        self.e_error = self.error_label()
        res.addWidget(self.e_error, 4, 0, 1, 3)
        layout.addWidget(results)

        travel = QGroupBox("Travel && Frequency")
        trv = QGridLayout(travel)
        trv.setColumnStretch(1, 1)
        trv.setVerticalSpacing(6)

        self.e_distance = self.input_row(trv, 0, "Distance to Move", "100")
        self.e_move_counts = self.output_row(trv, 1, "Counts to Move")
        self.e_rpm = self.input_row(trv, 2, "Shaft Speed (RPM)", "3000")
        self.e_frequency = self.output_row(trv, 3, "Frequency (Hz)")
        layout.addWidget(travel)

        clear = QPushButton("Clear")
        clear.setFixedWidth(CLEAR_BUTTON_WIDTH)
        clear.clicked.connect(self.clear_encoder)
        layout.addWidget(clear, 0, Qt.AlignLeft)
        layout.addStretch(1)

        for edit in (self.e_ppr, self.e_dim, self.e_gear, self.e_distance, self.e_rpm):
            edit.textChanged.connect(self.update_encoder)

        self.e_quad.currentTextChanged.connect(self.update_encoder)
        self.e_mech.currentTextChanged.connect(self.update_encoder)
        self.update_encoder()

    # ------------------------------------------------------------------------------
    # Recalculate the Encoder & Motion tab
    def update_encoder(self) -> None:
        outputs = [self.e_counts, self.e_travel, self.e_per_count,
                   self.e_per_unit, self.e_move_counts, self.e_frequency]

        mechanism = self.e_mech.currentText()
        rotary = mechanism == "Rotary (degrees)"

        # A rotary readout is fixed at 360 degrees per revolution, so the
        # dimension field has nothing to contribute.
        self.e_dim.setEnabled(not rotary)

        ppr = self.field_value(self.e_ppr)
        dimension = 0.0 if rotary else self.field_value(self.e_dim)
        gear = 1.0 if not self.e_gear.text().strip() else self.field_value(self.e_gear)

        if None in (ppr, dimension, gear):
            self.clear_outputs(outputs)
            self.e_error.setText("")
            return

        try:
            out = encoder_resolution(
                ppr, QUADRATURE_MODES[self.e_quad.currentText()], mechanism, dimension, gear
            )
        except CalcError as error:
            self.clear_outputs(outputs)
            self.e_error.setText(str(error))
            return

        self.show_values([
            (self.e_counts, out["counts_per_rev"]),
            (self.e_travel, out["travel_per_rev"]),
            (self.e_per_count, out["distance_per_count"]),
            (self.e_per_unit, out["counts_per_unit"]),
        ])

        distance = self.field_value(self.e_distance)
        rpm = self.field_value(self.e_rpm)

        try:
            moved = None if distance is None else counts_for_distance(distance, out["distance_per_count"])
        except CalcError:
            moved = None

        self.show_values([
            (self.e_move_counts, moved),
            (self.e_frequency, None if rpm is None else pulse_frequency(out["counts_per_rev"], rpm)),
        ])
        self.e_error.setText("")

    # ------------------------------------------------------------------------------
    # Clear the Encoder & Motion tab
    def clear_encoder(self) -> None:
        clear_line_edits([self.e_distance, self.e_rpm])
        update_owner_status(self, "Encoder tab cleared.")


    # --------------------------------------------------------------------------
    # GENERAL ACTIONS AND STATUS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Copy a value to the clipboard
    def copy_value(self, value: str, name: str = "") -> None:
        copy_to_clipboard(self, value)

    # ------------------------------------------------------------------------------
    # Set main window status text
    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    # ------------------------------------------------------------------------------
    # Apply the selected theme to this window
    def apply_theme(self, theme_name: str) -> None:
        self.theme_name = theme_name
        apply_app_theme(theme_name)



# ******************************************************************************
#
# RUNTIME ENTRY POINT
#
# ******************************************************************************


# ------------------------------------------------------------------------------
# Initialize Qt application runtime and open the Engineering Calculator
def main() -> None:
    """Initialize Qt and open the standalone Engineering Calculator window."""
    set_windows_app_user_model_id("DDayControls.EngineeringCalculator.Qt")
    app = QApplication.instance() or QApplication(sys.argv)
    apply_app_theme(resolve_theme(get_saved_theme_pref()))

    app.setApplicationName(CALC_APP_NAME)
    app.setOrganizationName(COMPANY_NAME)

    icon_path = resource_path(CALC_ICON_ICO)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = EngineeringCalculator()
    window.show()
    sys.exit(app.exec())


# Script execution gateway wrapper
if __name__ == "__main__":
    main()
