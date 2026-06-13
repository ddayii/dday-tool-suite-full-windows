"""
DDay Controls Copy Format Editor - Qt Edition (PySide6)
=======================================================
Shared dialogs for editing copy-format presets and group visibility/order.
"""


from __future__ import annotations

from dday_controls_common import *
from PySide6.QtWidgets import QInputDialog


# ==============================================================================
# COPY FORMAT GROUP MANAGER WINDOW
# ==============================================================================

class CopyFormatGroupManagerDialog(QDialog):
    """Manage enabled state, display order, and user-defined copy-format groups."""

    BUILT_IN_GROUPS = set(DEFAULT_COPY_FORMAT_GROUPS.keys())
    USER_GROUP_NAME = "User Custom"


    # --------------------------------------------------------------------------
    # WINDOW INITIALIZATION
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Initialize the group manager window and build its controls
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Manage Format Groups")
        self.resize(560, 420)
        self.setMinimumSize(520, 300)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.rows: list[tuple[QCheckBox, QLineEdit, QPushButton, QPushButton, QPushButton, str]] = []

        self.groups = copy_format_groups_with_user_group(PREFERENCES.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS))
        self.group_order = copy_format_group_order(self.groups, PREFERENCES)
        self.enabled_groups = set(PREFERENCES.get("enabled_copy_format_groups", []))

        layout = QVBoxLayout(self)

        menubar = QMenuBar()
        layout.setMenuBar(menubar)
        
        file_menu = menubar.addMenu("File")
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.accept_if_valid)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        options_menu = menubar.addMenu("Options")
        add_copy_format_group_item_editor_action(options_menu, self)

        add_help_menu(menubar, self, "Manage Format Groups")
        
        layout.addLayout(
            build_header(
                "Manage Format Groups",
                "Choose which copy-format groups are shown, change their order, and add or remove user groups.",
                logo_size=36,
            )
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.row_container = QWidget()
        self.row_layout = QGridLayout(self.row_container)
        self.row_layout.setColumnStretch(0, 0)
        self.row_layout.setColumnStretch(1, 1)
        self.row_layout.setColumnStretch(2, 0)
        self.row_layout.setColumnStretch(3, 0)
        self.row_layout.setColumnStretch(4, 0)
        self.row_layout.setHorizontalSpacing(8)
        self.row_layout.setVerticalSpacing(6)
        self.row_layout.setContentsMargins(8, 8, 8, 8)
        self.row_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.row_container)
        layout.addWidget(self.scroll, 1)

        action_row = QHBoxLayout()
        add_btn = QPushButton("Add Group")
        defaults_btn = QPushButton("Restore Defaults")
        action_row.addWidget(add_btn)
        action_row.addStretch(1)
        action_row.addWidget(defaults_btn)
        layout.addLayout(action_row)

        bottom = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)
        cancel_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)
        bottom.addStretch(1)
        bottom.addWidget(save_btn)
        bottom.addWidget(cancel_btn)
        layout.addLayout(bottom)
        add_dialog_status_bar(layout, self)

        add_btn.clicked.connect(self.add_group)
        defaults_btn.clicked.connect(self.restore_defaults)
        save_btn.clicked.connect(self.accept_if_valid)
        cancel_btn.clicked.connect(self.reject)

        self.load_rows()


    # --------------------------------------------------------------------------
    # ROW LAYOUT HELPERS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Clear group manager rows
    def clear_rows(self) -> None:
        while self.row_layout.count():
            item = self.row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.rows.clear()


    # ------------------------------------------------------------------------------
    # Load copy-format group rows
    def load_rows(self) -> None:
        self.clear_rows()

        self.row_layout.addWidget(QLabel("Show"), 0, 0)
        self.row_layout.addWidget(QLabel("Group Name"), 0, 1)
        self.row_layout.addWidget(QLabel(""), 0, 2)
        self.row_layout.addWidget(QLabel(""), 0, 3)
        self.row_layout.addWidget(QLabel(""), 0, 4)

        for row_index, group_name in enumerate(self.group_order, start=1):
            self.add_group_row(group_name, row_index)


    # ------------------------------------------------------------------------------
    # Add one group manager row
    def add_group_row(self, group_name: str, row: int) -> None:
        show_check = QCheckBox()
        show_check.setChecked(group_name in self.enabled_groups)
        show_check.stateChanged.connect(
            lambda _state=0, name=group_name: update_owner_status(
                self,
                f"Group visibility changed: {name}. Click Save to apply.",
            )
        )

        name_edit = QLineEdit(group_name)
        name_edit.setReadOnly(True)
        name_edit.setProperty("lockedDisplay", True)
        refresh_widget_style(name_edit)

        protected_group = group_name == self.USER_GROUP_NAME

        up_btn = QPushButton("↑")
        down_btn = QPushButton("↓")
        delete_btn = QPushButton("Delete")

        up_btn.setFixedWidth(40)
        down_btn.setFixedWidth(40)
        delete_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)

        up_btn.clicked.connect(lambda: self.move_group(name_edit, -1))
        down_btn.clicked.connect(lambda: self.move_group(name_edit, 1))
        delete_btn.clicked.connect(lambda: self.delete_group(name_edit))

        if protected_group:
            lock_button_display(delete_btn, "The User Custom group is required for manual additions.")

        self.row_layout.addWidget(show_check, row, 0)
        self.row_layout.addWidget(name_edit, row, 1)
        self.row_layout.addWidget(up_btn, row, 2)
        self.row_layout.addWidget(down_btn, row, 3)
        self.row_layout.addWidget(delete_btn, row, 4)

        self.rows.append((show_check, name_edit, up_btn, down_btn, delete_btn, group_name))


    # ------------------------------------------------------------------------------
    # Rebuild group manager layout after order changes
    def rebuild_rows(self) -> None:
        self.capture_rows_to_state()
        self.load_rows()


    # --------------------------------------------------------------------------
    # GROUP EDIT ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Capture visible rows back to temporary state
    def capture_rows_to_state(self) -> None:
        new_groups = OrderedDict()
        new_order = []
        new_enabled = set()

        for show_check, name_edit, _, _, _, original_name in self.rows:
            name = name_edit.text().strip()
            if not name:
                continue

            source_items = self.groups.get(original_name, [])
            new_groups[name] = source_items
            new_order.append(name)

            if show_check.isChecked():
                new_enabled.add(name)

        self.groups = new_groups
        self.group_order = new_order
        self.enabled_groups = new_enabled


    # ------------------------------------------------------------------------------
    # Add a new user-defined group
    def add_group(self) -> None:
        self.capture_rows_to_state()

        base = "New Group"
        name = base
        index = 1

        while name in self.groups:
            index += 1
            name = f"{base} {index}"

        self.groups[name] = []
        self.group_order.append(name)
        self.enabled_groups.add(name)
        self.load_rows()
        update_owner_status(self, f"Added group: {name}. Click Save to apply.")


    # ------------------------------------------------------------------------------
    # Delete a selected group
    def delete_group(self, name_edit: QLineEdit) -> None:
        self.capture_rows_to_state()
        name = name_edit.text().strip()

        if name == self.USER_GROUP_NAME:
            self.status.setText("The User Custom group is required for manual additions.")
            return

        self.groups.pop(name, None)
        self.group_order = [group_name for group_name in self.group_order if group_name != name]
        self.enabled_groups.discard(name)
        self.load_rows()
        update_owner_status(self, f"Deleted group: {name}. Click Save to apply.")


    # ------------------------------------------------------------------------------
    # Move a group row up or down
    def move_group(self, name_edit: QLineEdit, direction: int) -> None:
        self.capture_rows_to_state()
        name = name_edit.text().strip()

        if name not in self.group_order:
            return

        index = self.group_order.index(name)
        new_index = index + direction

        if new_index < 0 or new_index >= len(self.group_order):
            return

        self.group_order[index], self.group_order[new_index] = self.group_order[new_index], self.group_order[index]
        self.load_rows()
        update_owner_status(self, f"Moved group: {name}. Click Save to apply.")


    # ------------------------------------------------------------------------------
    # Restore default built-in group state and order
    def restore_defaults(self) -> None:
        self.groups = copy_format_groups_with_user_group(DEFAULT_COPY_FORMAT_GROUPS)
        self.group_order = list(DEFAULT_PREFERENCES["copy_format_group_order"])
        self.enabled_groups = set(DEFAULT_PREFERENCES["enabled_copy_format_groups"])
        self.load_rows()
        self.status.setText("Group defaults restored. Click Save to apply.")


    # --------------------------------------------------------------------------
    # VALIDATION AND ACCEPT HANDLING
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Validate group rows and save temporary state
    def validate_rows(self) -> None:
        self.capture_rows_to_state()

        seen = set()
        for name in self.group_order:
            if not name:
                raise ValueError("Every group needs a name.")

            if name in seen:
                raise ValueError(f"Duplicate group name: {name}")

            seen.add(name)

        if self.USER_GROUP_NAME not in self.groups:
            self.groups[self.USER_GROUP_NAME] = []
            self.group_order.append(self.USER_GROUP_NAME)


    # ------------------------------------------------------------------------------
    # Accept group manager changes after validation
    def accept_if_valid(self) -> None:
        try:
            self.validate_rows()
        except ValueError as exc:
            self.status.setText(str(exc))
            return

        set_copy_format_group_preferences(
            self.groups,
            list(self.enabled_groups),
            self.group_order,
        )
        update_owner_status(self, "Group settings saved.")
        self.accept()



# ==============================================================================
# COPY FORMAT GROUP ITEM EDITOR WINDOW
# ==============================================================================

class CopyFormatGroupItemEditorDialog(QDialog):
    """Edit copy-format items inside one selected group."""

    REQUIRED_CORE_NAMES = {"None", "Custom"}


    # --------------------------------------------------------------------------
    # WINDOW INITIALIZATION
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Initialize the group item editor window and build its controls
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Group Items")
        self.resize(600, 520)
        self.setMinimumSize(600, 300)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.rows: list[tuple[QLineEdit, QLineEdit, QLineEdit, QPushButton]] = []
        self.groups = copy_format_groups_with_user_group(
            PREFERENCES.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS)
        )
        self.group_order = copy_format_group_order(self.groups, PREFERENCES)
        self.enabled_groups = set(PREFERENCES.get("enabled_copy_format_groups", []))
        self.active_group = self.group_order[0] if self.group_order else "User Custom"
        self.loading_group = False
        self.grid_row = 1

        layout = QVBoxLayout(self)

        menubar = QMenuBar()
        
        file_menu = menubar.addMenu("File")
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.accept_if_valid)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        layout.setMenuBar(menubar)
        add_edit_menu(menubar, self)
        add_help_menu(menubar, self, "Edit Group Items")

        layout.addLayout(
            build_header(
                "Edit Group Items",
                "Choose a group, then add, remove, or edit that group's copy-format presets.",
                logo_size=36,
            )
        )

        group_row = QHBoxLayout()
        group_row.addWidget(form_label("Group", 55))
        self.group_combo = QComboBox()
        self.group_combo.addItems(self.group_order)
        group_row.addWidget(self.group_combo, 1)
        rename_group_btn = QPushButton("Rename Group...")
        rename_group_btn.setFixedWidth(130)
        rename_group_btn.clicked.connect(self.rename_current_group)
        group_row.addWidget(rename_group_btn)
        layout.addLayout(group_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.row_container = QWidget()
        self.row_layout = QGridLayout(self.row_container)
        self.row_layout.setColumnStretch(0, 2)
        self.row_layout.setColumnStretch(1, 1)
        self.row_layout.setColumnStretch(2, 1)
        self.row_layout.setColumnStretch(3, 0)
        self.row_layout.setHorizontalSpacing(8)
        self.row_layout.setVerticalSpacing(6)
        self.row_layout.setContentsMargins(8, 8, 8, 8)
        self.row_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.row_container)
        layout.addWidget(self.scroll, 1)

        button_row = QHBoxLayout()
        add_btn = QPushButton("Add")
        defaults_btn = QPushButton("Restore This Group")
        button_row.addWidget(add_btn)
        button_row.addStretch(1)
        button_row.addWidget(defaults_btn)
        layout.addLayout(button_row)

        bottom = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)
        cancel_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)
        bottom.addStretch(1)
        bottom.addWidget(save_btn)
        bottom.addWidget(cancel_btn)
        layout.addLayout(bottom)
        add_dialog_status_bar(layout, self)

        self.group_combo.currentTextChanged.connect(self.change_group)
        add_btn.clicked.connect(self.add_format)
        defaults_btn.clicked.connect(self.restore_current_group)
        save_btn.clicked.connect(self.accept_if_valid)
        cancel_btn.clicked.connect(self.reject)

        self.load_group_rows(self.active_group)


    # --------------------------------------------------------------------------
    # GROUP SELECTION AND STATE HANDLING
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Capture current row values into the active temporary group
    def capture_current_group(self) -> None:
        if self.loading_group:
            return

        items = []
        for name_edit, prefix_edit, suffix_edit, _ in self.rows:
            name = name_edit.text().strip()
            if not name:
                continue

            items.append({
                "name": name,
                "prefix": prefix_edit.text(),
                "suffix": suffix_edit.text(),
            })

        self.groups[self.active_group] = items


    # ------------------------------------------------------------------------------
    # Change the selected group and load its rows
    def change_group(self, group_name: str) -> None:
        if not group_name or group_name == self.active_group:
            return

        self.capture_current_group()
        self.active_group = group_name
        self.load_group_rows(group_name)
        update_owner_status(self, f"Editing group: {group_name}")


    # --------------------------------------------------------------------------
    # ROW LAYOUT HELPERS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Clear group item editor rows and header
    def clear_rows(self) -> None:
        while self.row_layout.count():
            item = self.row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.rows.clear()


    # ------------------------------------------------------------------------------
    # Add column header row
    def add_header_row(self) -> None:
        self.row_layout.addWidget(QLabel("Name"), 0, 0)
        self.row_layout.addWidget(QLabel("Prefix"), 0, 1)
        self.row_layout.addWidget(QLabel("Suffix"), 0, 2)
        self.row_layout.addWidget(QLabel(""), 0, 3)
        self.grid_row = 1


    # ------------------------------------------------------------------------------
    # Load rows for the selected group
    def load_group_rows(self, group_name: str) -> None:
        self.loading_group = True
        self.clear_rows()
        self.add_header_row()

        for item in self.groups.get(group_name, []):
            self.add_format_row(
                str(item.get("name", "")),
                str(item.get("prefix", "")),
                str(item.get("suffix", "")),
            )

        self.loading_group = False


    # ------------------------------------------------------------------------------
    # Add one editable item row
    def add_format_row(self, name: str = "", prefix: str = "", suffix: str = "") -> None:
        row = self.grid_row
        self.grid_row += 1

        name_edit = QLineEdit(name)
        prefix_edit = QLineEdit(prefix)
        suffix_edit = QLineEdit(suffix)
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)
        delete_btn.clicked.connect(lambda: self.delete_row(delete_btn))
        for edit in (name_edit, prefix_edit, suffix_edit):
            edit.textEdited.connect(
                lambda _text="": update_owner_status(
                    self,
                    "Group item edited. Click Save to apply.",
                )
            )

        self.row_layout.addWidget(name_edit, row, 0)
        self.row_layout.addWidget(prefix_edit, row, 1)
        self.row_layout.addWidget(suffix_edit, row, 2)
        self.row_layout.addWidget(delete_btn, row, 3)

        self.rows.append((name_edit, prefix_edit, suffix_edit, delete_btn))


    # ------------------------------------------------------------------------------
    # Rebuild the visible row layout after deleting a row
    def rebuild_row_layout(self) -> None:
        saved_rows = self.rows[:]

        while self.row_layout.count():
            item = self.row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        self.rows.clear()
        self.add_header_row()

        for name_edit, prefix_edit, suffix_edit, delete_btn in saved_rows:
            row = self.grid_row
            self.grid_row += 1
            self.row_layout.addWidget(name_edit, row, 0)
            self.row_layout.addWidget(prefix_edit, row, 1)
            self.row_layout.addWidget(suffix_edit, row, 2)
            self.row_layout.addWidget(delete_btn, row, 3)
            self.rows.append((name_edit, prefix_edit, suffix_edit, delete_btn))


    # --------------------------------------------------------------------------
    # GROUP NAME EDIT ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Rename the currently selected group
    def rename_current_group(self) -> None:
        old_name = self.active_group

        if not old_name:
            return

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Group",
            "Group name:",
            text=old_name,
        )

        if not accepted:
            return

        new_name = new_name.strip()

        if not new_name:
            self.status.setText("Group name cannot be blank.")
            return

        if new_name != old_name and new_name in self.groups:
            self.status.setText(f"Duplicate group name: {new_name}")
            return

        if new_name == old_name:
            return

        self.capture_current_group()

        renamed_groups = OrderedDict()
        for group_name, items in self.groups.items():
            renamed_groups[new_name if group_name == old_name else group_name] = items

        self.groups = renamed_groups
        self.group_order = [new_name if group_name == old_name else group_name for group_name in self.group_order]
        if old_name in self.enabled_groups:
            self.enabled_groups.discard(old_name)
            self.enabled_groups.add(new_name)
        self.active_group = new_name

        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        self.group_combo.addItems(self.group_order)
        self.group_combo.setCurrentText(new_name)
        self.group_combo.blockSignals(False)

        self.status.setText("Group renamed. Click Save to apply.")


    # --------------------------------------------------------------------------
    # FORMAT ROW EDIT ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Add a new item row to the current group
    def add_format(self) -> None:
        existing = {name_edit.text().strip() for name_edit, _, _, _ in self.rows}
        base = "New Format"
        name = base
        index = 1

        while name in existing:
            index += 1
            name = f"{base} {index}"

        self.add_format_row(name, "", "")
        update_owner_status(self, f"Added item to {self.active_group}. Click Save to apply.")

        for name_edit, _, _, _ in self.rows:
            if name_edit.text().strip() == name:
                name_edit.setFocus()
                name_edit.selectAll()
                break


    # ------------------------------------------------------------------------------
    # Delete one item row from the current group
    def delete_row(self, delete_btn: QPushButton) -> None:
        for row, (_, _, _, btn) in enumerate(self.rows):
            if btn is delete_btn:
                self.rows.pop(row)
                self.rebuild_row_layout()
                update_owner_status(self, "Deleted item. Click Save to apply.")
                return


    # ------------------------------------------------------------------------------
    # Restore the selected group to the shipped default items
    def restore_current_group(self) -> None:
        default_items = DEFAULT_COPY_FORMAT_GROUPS.get(self.active_group)

        if default_items is None:
            self.groups[self.active_group] = []
            self.status.setText("User group cleared. Click Save to apply.")
        else:
            self.groups[self.active_group] = [
                {
                    "name": str(item.get("name", "")),
                    "prefix": str(item.get("prefix", "")),
                    "suffix": str(item.get("suffix", "")),
                }
                for item in default_items
            ]
            self.status.setText("Group defaults restored. Click Save to apply.")

        self.load_group_rows(self.active_group)


    # --------------------------------------------------------------------------
    # VALIDATION AND ACCEPT HANDLING
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Validate all group items
    def validate_groups(self) -> None:
        self.capture_current_group()
        self.group_order = [name for name in self.group_order if name in self.groups]

        for group_name in self.group_order:
            seen_in_group = set()
            cleaned_items = []

            for item in self.groups.get(group_name, []):
                name = str(item.get("name", "")).strip()
                if not name:
                    raise ValueError(f"Every item in {group_name} needs a name.")

                if name in self.REQUIRED_CORE_NAMES:
                    raise ValueError(f"{name} is reserved and cannot be used as a group item.")

                if name in seen_in_group:
                    raise ValueError(f"Duplicate item in {group_name}: {name}")

                seen_in_group.add(name)
                cleaned_items.append({
                    "name": name,
                    "prefix": str(item.get("prefix", "")),
                    "suffix": str(item.get("suffix", "")),
                })

            self.groups[group_name] = cleaned_items


    # ------------------------------------------------------------------------------
    # Accept group item changes after validation
    def accept_if_valid(self) -> None:
        try:
            self.validate_groups()
        except ValueError as exc:
            self.status.setText(str(exc))
            return

        PREFERENCES["copy_format_groups"] = copy_format_groups_with_user_group(self.groups)
        PREFERENCES["copy_format_group_order"] = [
            name for name in self.group_order if name in PREFERENCES["copy_format_groups"]
        ]
        PREFERENCES["enabled_copy_format_groups"] = [
            name for name in PREFERENCES["copy_format_group_order"]
            if name in self.enabled_groups and name in PREFERENCES["copy_format_groups"]
        ]
        update_owner_status(self, "Group items saved.")
        self.accept()



# ==============================================================================
# COPY FORMAT EDITOR WINDOW
# ==============================================================================

class CopyFormatEditorDialog(QDialog):
    """Editor for shared copy-format presets stored in AppData."""

    REQUIRED_NAMES = {"None", "Custom"}
    USER_GROUP_NAME = "User Custom"


    # --------------------------------------------------------------------------
    # WINDOW INITIALIZATION
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Initialize the window and build its controls
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Copy Formats")
        self.resize(600, 550)
        self.setMinimumSize(600, 300)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.rows: list[tuple[QLineEdit, QLineEdit, QLineEdit, QPushButton, str, bool]] = []
        self.grid_row = 1

        self.ensure_user_custom_group()

        layout = QVBoxLayout(self)

        menubar = QMenuBar()
        layout.setMenuBar(menubar)
        
        file_menu = menubar.addMenu("File")
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.accept_if_valid)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        add_edit_menu(menubar, self)

        options_menu = menubar.addMenu("Options")
        add_copy_format_group_manager_action(options_menu, self)

        add_help_menu(menubar, self, "Edit Copy Formats")

        layout.addLayout(
            build_header(
                "Edit Copy Formats",
                "Edit shared copy presets used by the ASCII Chart and Scalar Converter.",
                logo_size=36,
            )
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.row_container = QWidget()
        self.row_layout = QGridLayout(self.row_container)

        self.add_header_row()

        self.row_layout.setColumnStretch(0, 2)
        self.row_layout.setColumnStretch(1, 1)
        self.row_layout.setColumnStretch(2, 1)
        self.row_layout.setColumnStretch(3, 0)
        self.row_layout.setHorizontalSpacing(8)
        self.row_layout.setVerticalSpacing(6)
        self.row_layout.setContentsMargins(8, 8, 8, 8)
        self.row_layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.row_container)
        layout.addWidget(self.scroll, 1)

        self.load_enabled_group_rows()

        button_row = QHBoxLayout()
        add_btn = QPushButton("Add")
        defaults_btn = QPushButton("Restore Defaults")
        button_row.addWidget(add_btn)
        button_row.addStretch(1)
        button_row.addWidget(defaults_btn)
        layout.addLayout(button_row)

        bottom = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)
        cancel_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)
        bottom.addStretch(1)
        bottom.addWidget(save_btn)
        bottom.addWidget(cancel_btn)
        layout.addLayout(bottom)
        add_dialog_status_bar(layout, self)

        add_btn.clicked.connect(self.add_format)
        defaults_btn.clicked.connect(self.restore_defaults)
        save_btn.clicked.connect(self.accept_if_valid)
        cancel_btn.clicked.connect(self.reject)


    # --------------------------------------------------------------------------
    # GROUP SELECTION CONTROLS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Ensure the user custom group exists in preferences
    def ensure_user_custom_group(self) -> None:
        groups = PREFERENCES.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS)
        if self.USER_GROUP_NAME not in groups:
            groups[self.USER_GROUP_NAME] = []
            PREFERENCES["copy_format_groups"] = groups


    # ------------------------------------------------------------------------------
    # Return currently enabled copy-format group names
    def enabled_group_names(self) -> list[str]:
        return ordered_enabled_copy_format_groups(PREFERENCES)


    # ------------------------------------------------------------------------------
    # Reload visible copy formats from enabled group settings
    def reload_enabled_groups(self) -> None:
        self.load_enabled_group_rows()


    # ------------------------------------------------------------------------------
    # Refresh this editor after copy-format groups are customized
    def refresh_copy_format_options(self) -> None:
        self.load_enabled_group_rows()


    # --------------------------------------------------------------------------
    # ROW LAYOUT HELPERS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Add column header row to copy-format editor grid
    def add_header_row(self) -> None:
        self.row_layout.addWidget(QLabel("Name"), 0, 0)
        self.row_layout.addWidget(QLabel("Prefix"), 0, 1)
        self.row_layout.addWidget(QLabel("Suffix"), 0, 2)
        self.row_layout.addWidget(QLabel(""), 0, 3)
        self.grid_row = 1


    # ------------------------------------------------------------------------------
    # Add a group header row to the copy-format editor grid
    def add_group_header_row(self, group_name: str) -> None:
        header = QLabel(group_name)
        header.setStyleSheet("font-weight: bold; padding-top: 8px;")
        self.row_layout.addWidget(header, self.grid_row, 0, 1, 4)
        self.grid_row += 1


    # ------------------------------------------------------------------------------
    # Clear copy-format editor rows and rebuild the header row
    def clear_rows(self) -> None:
        while self.row_layout.count():
            item = self.row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.rows.clear()
        self.add_header_row()


    # ------------------------------------------------------------------------------
    # Load enabled group rows into the editor grid
    def load_enabled_group_rows(self) -> None:
        self.clear_rows()

        self.add_group_header_row("Core")
        self.add_format_row("None", "", "", "Core", True)

        groups = PREFERENCES.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS)

        for group_name in self.enabled_group_names():
            group_items = groups.get(group_name, [])
            self.add_group_header_row(group_name)

            is_group_item = group_name != self.USER_GROUP_NAME
            for item in group_items:
                name = str(item.get("name", "")).strip()
                if not name or name in self.REQUIRED_NAMES:
                    continue

                self.add_format_row(
                    name,
                    str(item.get("prefix", "")),
                    str(item.get("suffix", "")),
                    group_name,
                    is_group_item,
                )

        self.add_group_header_row("Custom")
        self.add_format_row("Custom", "", "", "Core", True)


    # ------------------------------------------------------------------------------
    # Add one editable copy-format row to the editor grid
    def add_format_row(self, name: str, prefix: str = "", suffix: str = "", group_name: str = "User Custom", is_group_item: bool = False) -> None:
        row = self.grid_row
        self.grid_row += 1

        name_edit = QLineEdit(name)
        prefix_edit = QLineEdit(prefix)
        suffix_edit = QLineEdit(suffix)
        delete_btn = QPushButton("Delete")

        delete_btn.setFixedWidth(CLEAR_BUTTON_WIDTH)

        if name in self.REQUIRED_NAMES:
            name_edit.setReadOnly(True)
            lock_button_display(delete_btn)

        if name == "Custom":
            prefix_edit.setReadOnly(True)
            suffix_edit.setReadOnly(True)

        if is_group_item:
            lock_button_display(
                delete_btn,
                "Built-in format entries cannot be deleted. "
                "Disable the group or edit the format instead.",
            )

        for edit in (name_edit, prefix_edit, suffix_edit):
            edit.textEdited.connect(
                lambda _text="": update_owner_status(
                    self,
                    "Copy format edited. Click Save to apply.",
                )
            )

        delete_btn.clicked.connect(lambda: self.delete_row(delete_btn))

        self.row_layout.addWidget(name_edit, row, 0)
        self.row_layout.addWidget(prefix_edit, row, 1)
        self.row_layout.addWidget(suffix_edit, row, 2)
        self.row_layout.addWidget(delete_btn, row, 3)

        self.rows.append((name_edit, prefix_edit, suffix_edit, delete_btn, group_name, is_group_item))


    # ------------------------------------------------------------------------------
    # Delete the selected user copy-format editor row
    def delete_row(self, delete_btn: QPushButton) -> None:
        for row, (_, _, _, btn, _, _) in enumerate(self.rows):
            if btn is delete_btn:
                self.rows.pop(row)
                self.rebuild_row_layout()
                update_owner_status(self, "Deleted copy format. Click Save to apply.")
                return


    # ------------------------------------------------------------------------------
    # Rebuild copy-format editor grid after row changes
    def rebuild_row_layout(self) -> None:
        while self.row_layout.count():
            item = self.row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        self.add_header_row()

        last_group = None
        for name_edit, prefix_edit, suffix_edit, delete_btn, group_name, is_group_item in self.rows:
            if group_name != last_group:
                self.add_group_header_row(group_name)
                last_group = group_name

            row = self.grid_row
            self.grid_row += 1
            self.row_layout.addWidget(name_edit, row, 0)
            self.row_layout.addWidget(prefix_edit, row, 1)
            self.row_layout.addWidget(suffix_edit, row, 2)
            self.row_layout.addWidget(delete_btn, row, 3)


    # --------------------------------------------------------------------------
    # FORMAT ROW EDIT ACTIONS
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Add a new user copy-format row
    def add_format(self) -> None:
        groups = PREFERENCES.setdefault("enabled_copy_format_groups", [])
        if self.USER_GROUP_NAME not in groups:
            groups.append(self.USER_GROUP_NAME)

        existing = {name_edit.text().strip() for name_edit, _, _, _, _, _ in self.rows}
        base = "New Format"
        name = base
        index = 1

        while name in existing:
            index += 1
            name = f"{base} {index}"

        if not any(group_name == self.USER_GROUP_NAME for _, _, _, _, group_name, _ in self.rows):
            self.add_group_header_row(self.USER_GROUP_NAME)

        # Keep Custom as the last visible format by inserting the new user row before it.
        custom_rows = [row for row in self.rows if row[0].text().strip() == "Custom"]
        self.rows = [row for row in self.rows if row[0].text().strip() != "Custom"]
        self.add_format_row(name, "", "", self.USER_GROUP_NAME, False)
        self.rows.extend(custom_rows)
        self.rebuild_row_layout()
        update_owner_status(self, f"Added copy format: {name}. Click Save to apply.")

        for name_edit, _, _, _, _, _ in self.rows:
            if name_edit.text().strip() == name:
                name_edit.setFocus()
                name_edit.selectAll()
                break


    # ------------------------------------------------------------------------------
    # Restore built-in copy-format groups in the editor
    def restore_defaults(self) -> None:
        groups = OrderedDict(DEFAULT_COPY_FORMAT_GROUPS)
        groups[self.USER_GROUP_NAME] = []
        PREFERENCES["copy_format_groups"] = groups
        PREFERENCES["enabled_copy_format_groups"] = list(DEFAULT_COPY_FORMAT_GROUPS.keys())

        PREFERENCES["copy_format_group_order"] = list(DEFAULT_PREFERENCES["copy_format_group_order"])

        self.load_enabled_group_rows()
        self.status.setText("Built-in defaults restored. Click Save to save.")


    # --------------------------------------------------------------------------
    # VALIDATION AND ACCEPT HANDLING
    # --------------------------------------------------------------------------


    # ------------------------------------------------------------------------------
    # Validate editor rows and return copy-format dictionary
    def formats_from_rows(self) -> OrderedDict[str, tuple[str | None, str | None]]:
        formats: OrderedDict[str, tuple[str | None, str | None]] = OrderedDict()
        seen: set[str] = set()

        for name_edit, prefix_edit, suffix_edit, _, _, _ in self.rows:
            name = name_edit.text().strip()

            if not name:
                raise ValueError("Every copy format needs a name.")

            if name in seen:
                raise ValueError(f"Duplicate copy format name: {name}")

            seen.add(name)

            if name == "Custom":
                formats[name] = (None, None)
            else:
                formats[name] = (prefix_edit.text(), suffix_edit.text())

        if "None" not in formats:
            raise ValueError("The None format is required.")

        if "Custom" not in formats:
            formats["Custom"] = (None, None)

        return formats


    # ------------------------------------------------------------------------------
    # Save visible editor rows back into their copy-format groups
    def save_rows_to_groups(self) -> None:
        enabled_groups = self.enabled_group_names()
        groups = OrderedDict(PREFERENCES.get("copy_format_groups", DEFAULT_COPY_FORMAT_GROUPS))

        for group_name in enabled_groups:
            groups[group_name] = []

        for name_edit, prefix_edit, suffix_edit, _, group_name, _ in self.rows:
            name = name_edit.text().strip()

            if group_name == "Core" or name in self.REQUIRED_NAMES:
                continue

            if group_name not in groups:
                groups[group_name] = []

            groups[group_name].append({
                "name": name,
                "prefix": prefix_edit.text(),
                "suffix": suffix_edit.text(),
            })

        PREFERENCES["copy_format_groups"] = groups
        PREFERENCES["enabled_copy_format_groups"] = enabled_groups


    # ------------------------------------------------------------------------------
    # Accept copy-format editor changes after validation
    def accept_if_valid(self) -> None:
        try:
            self.edited_formats = self.formats_from_rows()
        except ValueError as exc:
            self.status.setText(str(exc))
            return

        self.save_rows_to_groups()
        update_owner_status(self, "Copy formats saved.")
        self.accept()
