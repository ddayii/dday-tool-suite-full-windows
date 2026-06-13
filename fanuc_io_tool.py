from __future__ import annotations

import os
import re
from pathlib import Path

from dday_controls_common import *

import fanuc_io_parser
import fanuc_template
import fanuc_csv_generator
import fanuc_karel_generator

APP_TITLE = "DDay Controls FANUC I/O Tool"
APP_SUBTITLE = "Create FANUC comment templates, RoboGuide CSV imports, and KAREL loaders"
TOOL_KEY = "fanuc_io_tool"


class DropLineEdit(QLineEdit):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.setAcceptDrops(True)
        self.setPlaceholderText("Drop a RoboGuide CSV or DDay Controls XLSX template here...")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.setText(path)
            self.owner.load_preview(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class FanucIOTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)

        # Use the FANUC/robot icon for this tool's window, taskbar, and header.
        fanuc_icon = resource_path("DDay_FANUC_Suite_Icon.ico")
        fanuc_png = resource_path("DDay_FANUC_Suite_Icon.png")
        if os.path.exists(fanuc_icon):
            self.setWindowIcon(QIcon(fanuc_icon))
        elif os.path.exists(fanuc_png):
            self.setWindowIcon(QIcon(fanuc_png))

        self.resize(920, 680)
        self.theme_name = resolve_theme(get_saved_theme_pref())
        self.data = fanuc_io_parser.empty_data()

        self.build_ui()
        register_tool_window(TOOL_KEY, self)
        self.set_status("Ready.")

    def build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        btn_text, btn_callback = companion_header_button(self, TOOL_KEY)
        layout.addLayout(
            build_header(
                APP_TITLE,
                APP_SUBTITLE,
                btn_text,
                btn_callback,
                logo_size=48,
                logo_file="DDay_FANUC_Suite_Icon.png",
            )
        )

        menu_bar = self.menuBar()
        add_file_menu(menu_bar, self)
        add_edit_menu(menu_bar, self)

        tools_menu = menu_bar.addMenu("Tools")
        add_available_tool_actions(tools_menu, self, TOOL_KEY)

        options_menu = menu_bar.addMenu("Options")
        add_theme_submenu(options_menu, self, self.refresh_theme)
        add_header_tool_selector_action(options_menu, self, TOOL_KEY)

        add_help_menu(menu_bar, self, APP_TITLE)

        input_group = QGroupBox("Input")
        grid = QGridLayout(input_group)
        self.input_path = DropLineEdit(self)
        browse = QPushButton("Browse")
        browse.clicked.connect(self.browse_input)
        grid.addWidget(form_label("File"), 0, 0)
        grid.addWidget(self.input_path, 0, 1)
        grid.addWidget(browse, 0, 2)
        layout.addWidget(input_group)

        output_group = QGroupBox("Output")
        out = QHBoxLayout(output_group)
        self.chk_template = QCheckBox("Create Template XLSX")
        self.chk_csv = QCheckBox("Create RoboGuide CSV")
        self.chk_karel = QCheckBox("Create KAREL .KL")
        self.chk_template.setChecked(True)
        self.chk_csv.setChecked(True)
        self.chk_karel.setChecked(True)
        out.addWidget(self.chk_template)
        out.addWidget(self.chk_csv)
        out.addWidget(self.chk_karel)
        out.addStretch(1)

        self.new_template_btn = QPushButton("New Template")
        self.new_template_btn.clicked.connect(self.create_new_template)
        out.addWidget(self.new_template_btn)

        self.process_btn = QPushButton("Process")
        self.process_btn.clicked.connect(self.process)
        out.addWidget(self.process_btn)
        layout.addWidget(output_group)

        self.summary = QTableWidget(0, 3)
        self.summary.setHorizontalHeaderLabels(["Type", "Rows", "Enabled with Comment"])
        self.summary.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.summary, 1)

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        log_layout.addWidget(self.log_box)
        clear_log = QPushButton("Clear Log")
        clear_log.clicked.connect(self.log_box.clear)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(clear_log)
        log_layout.addLayout(row)
        layout.addWidget(log_group, 1)

        self.status_bar = QStatusBar()
        self.status = QLabel("Ready.")
        self.version_label = QLabel(f"{COMPANY_NAME}  |  {APP_VERSION}")
        self.status_bar.addWidget(self.status, 1)
        self.status_bar.addPermanentWidget(self.version_label)
        self.setStatusBar(self.status_bar)

    def refresh_theme(self):
        self.theme_name = resolve_theme(get_saved_theme_pref())

    def set_status(self, text: str):
        self.status.setText(text)

    def log(self, text: str):
        self.log_box.append(text)
        self.set_status(text)

    def create_new_template(self):
        robot_name, ok = QInputDialog.getText(
            self,
            "New Robot Template",
            "Robot name for template filename:",
        )

        if not ok:
            return

        robot_name = self.safe_filename(robot_name)
        if not robot_name:
            QMessageBox.warning(self, "Robot Name Required", "Enter a robot name for the template filename.")
            return

        out_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(Path.home()),
        )

        if not out_dir:
            return

        try:
            data = fanuc_io_parser.new_template_data()
            output_path = Path(out_dir) / f"{robot_name}_DDay_IO_Template.xlsx"
            created = fanuc_template.create_template(data, output_path)
            self.data = data
            self.input_path.clear()
            self.populate_summary()
            self.log(f"Created blank template: {created}")
            QMessageBox.information(self, "Template Created", f"Created:\n\n{created}")
        except Exception as exc:
            QMessageBox.critical(self, "Template Error", str(exc))
            self.log(f"Template creation failed: {exc}")

    @staticmethod
    def safe_filename(text: str) -> str:
        text = str(text or "").strip()
        text = re.sub(r"[^\w\-]+", "_", text)
        text = re.sub(r"_+", "_", text).strip("_")
        return text

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select FANUC Comment File",
            "",
            "FANUC Comment Files (*.csv *.xlsx *.xlsm);;CSV Files (*.csv);;Excel Files (*.xlsx *.xlsm);;All Files (*.*)",
        )
        if path:
            self.input_path.setText(path)
            self.load_preview(path)

    def load_preview(self, path: str):
        try:
            self.data = fanuc_io_parser.load_file(path)
            self.populate_summary()
            total = fanuc_io_parser.count_rows(self.data)
            enabled = fanuc_io_parser.count_rows(self.data, enabled_only=True)
            self.log(f"Loaded {total} rows. {enabled} enabled rows have comments.")
        except Exception as exc:
            QMessageBox.critical(self, "Load Error", str(exc))
            self.log(f"Load failed: {exc}")

    def populate_summary(self):
        self.summary.setRowCount(0)
        for io_type in fanuc_io_parser.IO_TYPES:
            rows = self.data.get(io_type, [])
            enabled = [r for r in rows if r.enabled and r.comment]
            if not rows:
                continue
            r = self.summary.rowCount()
            self.summary.insertRow(r)
            self.summary.setItem(r, 0, QTableWidgetItem(io_type))
            self.summary.setItem(r, 1, QTableWidgetItem(str(len(rows))))
            self.summary.setItem(r, 2, QTableWidgetItem(str(len(enabled))))

    def process(self):
        input_text = self.input_path.text().strip()
        if not input_text:
            QMessageBox.warning(self, "No Input", "Select or drop a CSV/XLSX file first.")
            return
        input_path = Path(input_text)
        if not input_path.exists():
            QMessageBox.warning(self, "Missing File", "The selected input file does not exist.")
            return
        try:
            self.data = fanuc_io_parser.load_file(input_path)
            self.populate_summary()
            stem = input_path.stem.replace(" ", "_")
            out_dir = input_path.parent
            created = []
            if self.chk_template.isChecked():
                created.append(fanuc_template.create_template(self.data, out_dir / f"{stem}_DDay_IO_Template.xlsx"))
            if self.chk_csv.isChecked():
                created.append(fanuc_csv_generator.generate_csv(self.data, out_dir / f"{stem}_RoboGuide_Import.csv"))
            if self.chk_karel.isChecked():
                created.append(fanuc_karel_generator.generate_kl(self.data, out_dir / f"{stem}_Load_IO_Cmt.kl"))
            for p in created:
                self.log(f"Created: {p}")
            QMessageBox.information(self, "Complete", "Generated files:\n\n" + "\n".join(str(p) for p in created))
        except Exception as exc:
            QMessageBox.critical(self, "Process Error", str(exc))
            self.log(f"Process failed: {exc}")



def main():
    set_windows_app_user_model_id("DDayControls.FANUCIOTool.Qt")
    app = QApplication.instance() or QApplication([])
    apply_app_theme(resolve_theme(get_saved_theme_pref()))

    # Set the process/app icon for the standalone FANUC I/O Tool EXE.
    fanuc_icon = resource_path("DDay_FANUC_Suite_Icon.ico")
    fanuc_png = resource_path("DDay_FANUC_Suite_Icon.png")
    if os.path.exists(fanuc_icon):
        app.setWindowIcon(QIcon(fanuc_icon))
    elif os.path.exists(fanuc_png):
        app.setWindowIcon(QIcon(fanuc_png))

    window = FanucIOTool()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
