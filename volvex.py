"""
Volvex - KryoFlux GUI
PySide6 frontend for dtc and mimage
© 2026 Roberto Chichiarelli
"""

import sys
import os
import re
import json
import datetime
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QComboBox, QLineEdit,
    QPlainTextEdit, QButtonGroup, QGroupBox, QSpinBox,
    QScrollArea, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction

VERSION = "1.0.0"

DUMP_IMAGE_TYPES = [
    ("0  - KryoFlux stream files (preservation)",  "0"),
    ("0a - KryoFlux stream files (format guided)", "0a"),
    ("2  - CT Raw image DS/DD MFM",                "2"),
    ("3  - FM sector image 40/80t SS/DS",          "3"),
    ("4  - MFM sector image 40/80t SS/DS DD/HD",   "4"),
    ("5  - AmigaDOS sector image DS DD/HD",        "5"),
    ("6  - CBM DOS sector image SS DD GCR",        "6"),
    ("7  - Apple DOS 3.2 sector image GCR",        "7"),
    ("8  - Apple DOS 3.3+ sector image GCR",       "8"),
    ("9  - Apple DOS 400K/800K SS/DS GCR",         "9"),
    ("10 - Emu sector image SS DD FM",             "10"),
    ("11 - Emu II sector image DS DD FM",          "11"),
    ("12 - Amiga DiskSpare DS DD/HD MFM",          "12"),
    ("13 - DEC RX01 SS SD FM",                     "13"),
    ("14 - DEC RX02 SS SD/DD FM/DMMFM",           "14"),
    ("20 - CBM GCR image SS DD",                   "20"),
    ("25 - CBM DOS extended image SS DD GCR",      "25"),
]

WRITE_IMAGE_TYPES = [
    ("0 - Auto-detect",            "0"),
    ("1 - IPF image",              "1"),
    ("2 - Amiga ADF sector image", "2"),
    ("3 - CBM G64 image",          "3"),
    ("4 - KryoFlux stream files",  "4"),
]

STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1a1a1a;
    color: #d0d0d0;
    font-family: "Liberation Mono", "Courier New", monospace;
    font-size: 11px;
}
QMenuBar {
    background-color: #111111;
    color: #aaaaaa;
    border-bottom: 1px solid #333;
}
QMenuBar::item:selected { background-color: #2a2a2a; color: #ffffff; }
QMenu {
    background-color: #1e1e1e;
    color: #cccccc;
    border: 1px solid #333;
}
QMenu::item:selected { background-color: #ff6600; color: #ffffff; }
QGroupBox {
    border: 1px solid #333333;
    border-radius: 3px;
    margin-top: 8px;
    padding-top: 6px;
    color: #888888;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QPushButton {
    background-color: #2a2a2a;
    color: #aaaaaa;
    border: 1px solid #404040;
    border-radius: 2px;
    padding: 4px 12px;
    min-height: 22px;
}
QPushButton:hover { background-color: #333333; color: #ffffff; border-color: #555555; }
QPushButton:checked { background-color: #ff6600; color: #ffffff; border-color: #ff6600; }
QPushButton:disabled { background-color: #1e1e1e; color: #444444; border-color: #2a2a2a; }
QPushButton#btn_go {
    background-color: #cc4400;
    color: #ffffff;
    border: none;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
    min-height: 32px;
    border-radius: 2px;
}
QPushButton#btn_go:hover { background-color: #ff6600; }
QPushButton#btn_go:disabled { background-color: #2a2a2a; color: #444444; }
QPushButton#btn_stop {
    background-color: #1a1a1a;
    color: #cc4400;
    border: 1px solid #cc4400;
    font-size: 11px;
    letter-spacing: 1px;
    min-height: 32px;
    border-radius: 2px;
}
QPushButton#btn_stop:hover { background-color: #cc4400; color: #ffffff; }
QComboBox {
    background-color: #222222;
    color: #cccccc;
    border: 1px solid #383838;
    border-radius: 2px;
    padding: 3px 6px;
    min-height: 22px;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    color: #cccccc;
    selection-background-color: #ff6600;
    selection-color: #ffffff;
    border: 1px solid #383838;
}
QLineEdit {
    background-color: #222222;
    color: #cccccc;
    border: 1px solid #383838;
    border-radius: 2px;
    padding: 3px 6px;
    min-height: 22px;
}
QLineEdit:focus { border-color: #ff6600; }
QSpinBox {
    background-color: #222222;
    color: #cccccc;
    border: 1px solid #383838;
    border-radius: 2px;
    padding: 2px 4px;
    min-height: 22px;
}
QCheckBox { color: #aaaaaa; spacing: 6px; }
QCheckBox:hover { color: #ffffff; }
QCheckBox::indicator {
    width: 13px; height: 13px;
    border: 1px solid #444444;
    border-radius: 2px;
    background-color: #222222;
}
QCheckBox::indicator:checked { background-color: #ff6600; border-color: #ff6600; }
QPlainTextEdit {
    background-color: #0d0d0d;
    color: #33ff33;
    border: 1px solid #2a2a2a;
    border-radius: 2px;
    font-family: "Liberation Mono", "Courier New", monospace;
    font-size: 11px;
    selection-background-color: #ff6600;
}
QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { background-color: #1a1a1a; width: 8px; border: none; }
QScrollBar::handle:vertical {
    background-color: #383838;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #ff6600; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QLabel#cmd_preview {
    color: #555555;
    font-family: "Liberation Mono", "Courier New", monospace;
    font-size: 10px;
}
QStatusBar {
    background-color: #111111;
    color: #555555;
    border-top: 1px solid #2a2a2a;
    font-size: 10px;
}
"""


class CommandRunner(QThread):
    output   = Signal(str)
    finished = Signal(int)

    def __init__(self, cmd, parent=None):
        super().__init__(parent)
        self.cmd = cmd
        self._process = None

    def run(self):
        try:
            self._process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in self._process.stdout:
                self.output.emit(line.rstrip())
            self._process.wait()
            self.finished.emit(self._process.returncode)
        except FileNotFoundError:
            self.output.emit(f"[ERROR] Command not found: {self.cmd[0]}")
            self.finished.emit(-1)
        except Exception as e:
            self.output.emit(f"[ERROR] {e}")
            self.finished.emit(-1)

    def stop(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()


class Volvex(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Volvex {VERSION}")
        self.setMinimumSize(960, 620)
        self.resize(1100, 680)
        self._runner            = None
        self._init_runner       = None
        self._init_output_lines = []
        self._last_cmd          = []
        self._last_output_lines = []
        self._config_file = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),"volvex", "config.json")
        self._config = self._load_config()
        self._build_menu()
        self._build_ui()
        self._update_mode(dump=True)
        self._update_cmd_preview()

    def _load_config(self):
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "source_dir": os.path.expanduser("~"),
            "output_dir": os.path.expanduser("~"),
            "log_enabled": False,
            "log_dir": os.path.expanduser("~"),
        }

    def _save_config(self):
        os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
        with open(self._config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    def _build_menu(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        act_save_preset = QAction("Save preset...", self)
        act_save_preset.triggered.connect(self._save_preset)
        file_menu.addAction(act_save_preset)
        act_load_preset = QAction("Load preset...", self)
        act_load_preset.triggered.connect(self._load_preset)
        file_menu.addAction(act_load_preset)
        file_menu.addSeparator()
        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        actions_menu = mb.addMenu("Actions")
        act_init = QAction("Init KryoFlux (dtc -c2)", self)
        act_init.triggered.connect(self._run_init)
        actions_menu.addAction(act_init)
        act_mimage = QAction("Run Mimage", self)
        act_mimage.triggered.connect(self._run_mimage)
        actions_menu.addAction(act_mimage)

        settings_menu = mb.addMenu("Settings")
        act_prefs = QAction("Preferences", self)
        act_prefs.triggered.connect(self._open_preferences)
        settings_menu.addAction(act_prefs)

        help_menu = mb.addMenu("Help")
        act_about = QAction("About", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(8)
        top = QHBoxLayout()
        top.setSpacing(10)
        top.addLayout(self._build_controls(), stretch=0)
        top.addWidget(self._build_output(), stretch=1)
        root.addLayout(top, stretch=1)
        root.addLayout(self._build_bottom())

    def _build_controls(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        grp_mode = QGroupBox("1  ·  Operating Mode")
        grp_mode.setFixedWidth(270)
        mode_layout = QHBoxLayout(grp_mode)
        mode_layout.setSpacing(4)
        self.btn_dump  = QPushButton("DUMP")
        self.btn_write = QPushButton("WRITE")
        self.btn_dump.setCheckable(True)
        self.btn_write.setCheckable(True)
        self.btn_dump.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.btn_dump)
        self.mode_group.addButton(self.btn_write)
        self.mode_group.buttonClicked.connect(self._on_mode_clicked)
        mode_layout.addWidget(self.btn_dump)
        mode_layout.addWidget(self.btn_write)
        layout.addWidget(grp_mode)

        grp_drive = QGroupBox("2  ·  Drive")
        grp_drive.setFixedWidth(270)
        drive_layout = QHBoxLayout(grp_drive)
        drive_layout.addWidget(QLabel("Drive number (-d):"))
        self.spin_drive = QSpinBox()
        self.spin_drive.setRange(0, 3)
        self.spin_drive.setValue(0)
        self.spin_drive.setFixedWidth(52)
        self.spin_drive.valueChanged.connect(self._update_cmd_preview)
        drive_layout.addWidget(self.spin_drive)
        drive_layout.addStretch()
        layout.addWidget(grp_drive)

        grp_type = QGroupBox("3  ·  Image Type")
        grp_type.setFixedWidth(270)
        type_layout = QVBoxLayout(grp_type)
        self.combo_image = QComboBox()
        self.combo_image.currentIndexChanged.connect(self._update_cmd_preview)
        type_layout.addWidget(self.combo_image)
        layout.addWidget(grp_type)

        grp_paths = QGroupBox("4  ·  Paths")
        grp_paths.setFixedWidth(270)
        paths_layout = QVBoxLayout(grp_paths)
        paths_layout.setSpacing(4)

        self.lbl_outpath = QLabel("Output path / filename base:")
        paths_layout.addWidget(self.lbl_outpath)
        path_row = QHBoxLayout()
        self.edit_outpath = QLineEdit()
        self.edit_outpath.setPlaceholderText("/path/to/output/diskname")
        self.edit_outpath.textChanged.connect(self._update_cmd_preview)
        self.btn_browse_out = QPushButton("…")
        self.btn_browse_out.setFixedWidth(28)
        self.btn_browse_out.clicked.connect(self._browse_output)
        path_row.addWidget(self.edit_outpath)
        path_row.addWidget(self.btn_browse_out)
        paths_layout.addLayout(path_row)

        self.lbl_infile = QLabel("Source image file:")
        paths_layout.addWidget(self.lbl_infile)
        infile_row = QHBoxLayout()
        self.edit_infile = QLineEdit()
        self.edit_infile.setPlaceholderText("source.adf / source.ipf ...")
        self.edit_infile.textChanged.connect(self._update_cmd_preview)
        self.btn_browse_in = QPushButton("…")
        self.btn_browse_in.setFixedWidth(28)
        self.btn_browse_in.clicked.connect(self._browse_input)
        infile_row.addWidget(self.edit_infile)
        infile_row.addWidget(self.btn_browse_in)
        paths_layout.addLayout(infile_row)
        layout.addWidget(grp_paths)

        grp_opts = QGroupBox("5  ·  Options")
        grp_opts.setFixedWidth(270)
        opts_outer = QVBoxLayout(grp_opts)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)
        scroll_content = QWidget()
        self.opts_layout = QVBoxLayout(scroll_content)
        self.opts_layout.setSpacing(3)
        self.opts_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(scroll_content)
        opts_outer.addWidget(scroll)

        self._opt_rows = {}
        self._add_opt("retries",      "Retries (-t)",              flag="-t",   spinbox=True, default=5,  rng=(1, 20))
        self._add_opt("start_track",  "Start track (-s)",          flag="-s",   spinbox=True, default=0,  rng=(0, 83))
        self._add_opt("end_track",    "End track (-e)",            flag="-e",   spinbox=True, default=83, rng=(0, 83))
        self._add_opt("side_0",       "Side 0 only (-g0)",         flag="-g0")
        self._add_opt("side_1",       "Side 1 only (-g1)",         flag="-g1")
        self._add_opt("40_tracks",    "40 tracks (-k2)",           flag="-k2")
        self._add_opt("create_path",  "Create path (-p)",          flag="-p")
        self._add_opt("flippy",       "Flippy disk (-y)",          flag="-y")
        self._add_opt("write_verify", "Verify after write (-wv1)", flag="-wv1", write_only=True)
        self._add_opt("write_erase",  "Wipe before write (-we2)",  flag="-we2", write_only=True)

        self.opts_layout.addStretch()
        layout.addWidget(grp_opts)
        layout.addStretch()
        return layout

    def _add_opt(self, key, label, flag, spinbox=False, default=0, rng=(0, 99), write_only=False):
        row = QHBoxLayout()
        row.setSpacing(4)
        cb = QCheckBox(label)
        cb.stateChanged.connect(self._update_cmd_preview)
        row.addWidget(cb)
        spin = None
        if spinbox:
            spin = QSpinBox()
            spin.setRange(*rng)
            spin.setValue(default)
            spin.setFixedWidth(52)
            spin.setEnabled(False)
            spin.valueChanged.connect(self._update_cmd_preview)
            cb.stateChanged.connect(lambda s, sp=spin: sp.setEnabled(bool(s)))
            row.addWidget(spin)
        self.opts_layout.addLayout(row)
        self._opt_rows[key] = (cb, spin, flag, write_only)

    def _build_output(self):
        grp = QGroupBox("Output")
        layout = QVBoxLayout(grp)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(4)
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText("[ Volvex ready ]")
        layout.addWidget(self.terminal)

        log_row = QHBoxLayout()
        self.chk_log = QCheckBox("Save log to file")
        self.chk_log.setChecked(self._config.get("log_enabled", False))
        log_row.addWidget(self.chk_log)
        self.lbl_log_path = QLabel(self._config.get("log_dir", os.path.expanduser("~")))
        self.lbl_log_path.setObjectName("cmd_preview")
        log_row.addWidget(self.lbl_log_path, stretch=1)
        btn_log_dir = QPushButton("…")
        btn_log_dir.setFixedWidth(28)
        btn_log_dir.clicked.connect(self._pick_log_dir)
        log_row.addWidget(btn_log_dir)
        layout.addLayout(log_row)
        return grp

    def _build_bottom(self):
        layout = QHBoxLayout()
        layout.setSpacing(8)
        self.lbl_cmd = QLabel("")
        self.lbl_cmd.setObjectName("cmd_preview")
        self.lbl_cmd.setWordWrap(True)
        layout.addWidget(self.lbl_cmd, stretch=1)
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedWidth(80)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop)
        self.btn_go = QPushButton("GO")
        self.btn_go.setObjectName("btn_go")
        self.btn_go.setFixedWidth(100)
        self.btn_go.clicked.connect(self._run_dtc)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_go)
        return layout

    def _on_mode_clicked(self, btn):
        self._update_mode(dump=(btn is self.btn_dump))

    def _update_mode(self, dump: bool):
        self.combo_image.blockSignals(True)
        self.combo_image.clear()
        for label, val in (DUMP_IMAGE_TYPES if dump else WRITE_IMAGE_TYPES):
            self.combo_image.addItem(label, userData=val)
        self.combo_image.blockSignals(False)

        for key, (cb, spin, flag, write_only) in self._opt_rows.items():
            if write_only:
                cb.setVisible(not dump)
                if spin:
                    spin.setVisible(not dump)

        self.lbl_outpath.setVisible(dump)
        self.edit_outpath.setVisible(dump)
        self.btn_browse_out.setVisible(dump)
        self.lbl_infile.setVisible(not dump)
        self.edit_infile.setVisible(not dump)
        self.btn_browse_in.setVisible(not dump)
        self._update_cmd_preview()

    def _build_dtc_cmd(self):
        dump     = self.btn_dump.isChecked()
        img_type = self.combo_image.currentData()
        outpath  = self.edit_outpath.text().strip()
        infile   = self.edit_infile.text().strip()
        drive    = self.spin_drive.value()

        cmd = ["dtc", f"-d{drive}"]

        if dump:
            if outpath:
                cmd.append(f"-f{outpath}")
            for key, (cb, spin, flag, write_only) in self._opt_rows.items():
                if cb.isChecked() and flag in ("-y", "-k2"):
                    cmd.append(flag)
            cmd.append(f"-i{img_type}")
        else:
            cmd.append("-w")
            if infile:
                cmd.append(f"-f{infile}")
            cmd.append(f"-wi{img_type}")

        for key, (cb, spin, flag, write_only) in self._opt_rows.items():
            if not cb.isChecked():
                continue
            if flag in ("-y", "-k2"):
                continue
            cmd.append(f"{flag}{spin.value()}" if spin else flag)

        return cmd

    def _update_cmd_preview(self):
        self.lbl_cmd.setText("  ".join(self._build_dtc_cmd()))

    def _zenity(self, args):
        env = os.environ.copy()
        env["GTK_THEME"] = "Adwaita:dark"
        result = subprocess.run(
            ["zenity", "--width=800", "--height=600"] + args,
            capture_output=True, text=True, env=env
        )
        return result.stdout.strip()

    def _browse_output(self):
        start = self._config.get("output_dir", os.path.expanduser("~"))
        path = self._zenity(["--file-selection", "--directory",
                             "--title=Select output directory",
                             f"--filename={start}/"])
        if path:
            self.edit_outpath.setText(path + "/disk")

    def _browse_input(self):
        start = self._config.get("source_dir", os.path.expanduser("~"))
        path = self._zenity(["--file-selection",
                             "--title=Select source image",
                             f"--filename={start}/"])
        if path:
            self.edit_infile.setText(path)

    def _pick_log_dir(self):
        p = self._zenity(["--file-selection", "--directory",
                          "--title=Select log directory",
                          f"--filename={self.lbl_log_path.text()}/"])
        if p:
            self.lbl_log_path.setText(p)
            self._config["log_dir"] = p
            self._save_config()

    def _write_log(self):
        if not self.chk_log.isChecked():
            return
        log_dir = self._config.get("log_dir", os.path.expanduser("~"))
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(log_dir, f"volvex_{timestamp}.log")
        with open(log_path, "w") as f:
            f.write(f"Volvex log — {datetime.datetime.now().isoformat()}\n")
            f.write(f"Command: {' '.join(self._last_cmd)}\n")
            f.write("─" * 60 + "\n")
            f.write("\n".join(self._last_output_lines))
        self.terminal.appendPlainText(f"[ Log saved: {log_path} ]")

    def _get_preset(self):
        preset = {
            "mode": "dump" if self.btn_dump.isChecked() else "write",
            "drive": self.spin_drive.value(),
            "image_type_index": self.combo_image.currentIndex(),
            "outpath": self.edit_outpath.text(),
            "infile": self.edit_infile.text(),
            "options": {}
        }
        for key, (cb, spin, flag, write_only) in self._opt_rows.items():
            preset["options"][key] = {
                "checked": cb.isChecked(),
                "value": spin.value() if spin else None
            }
        return preset

    def _apply_preset(self, preset):
        dump = preset.get("mode", "dump") == "dump"
        (self.btn_dump if dump else self.btn_write).setChecked(True)
        self._update_mode(dump=dump)
        self.spin_drive.setValue(preset.get("drive", 0))
        idx = preset.get("image_type_index", 0)
        if 0 <= idx < self.combo_image.count():
            self.combo_image.setCurrentIndex(idx)
        self.edit_outpath.setText(preset.get("outpath", ""))
        self.edit_infile.setText(preset.get("infile", ""))
        for key, opts in preset.get("options", {}).items():
            if key in self._opt_rows:
                cb, spin, flag, write_only = self._opt_rows[key]
                cb.setChecked(opts.get("checked", False))
                if spin and opts.get("value") is not None:
                    spin.setValue(opts["value"])
        self._update_cmd_preview()

    def _save_preset(self):
        path = self._zenity(["--file-selection", "--save",
                             "--title=Save preset",
                             "--filename=preset.json",
                             "--file-filter=JSON files | *.json"])
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        with open(path, "w") as f:
            json.dump(self._get_preset(), f, indent=2)
        self.statusBar().showMessage(f"Preset saved: {path}")

    def _load_preset(self):
        path = self._zenity(["--file-selection",
                             "--title=Load preset",
                             "--file-filter=JSON files | *.json"])
        if not path:
            return
        try:
            with open(path) as f:
                self._apply_preset(json.load(f))
            self.statusBar().showMessage(f"Preset loaded: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load preset:\n{e}")

    def _run_cmd(self, cmd):
        if self._runner and self._runner.isRunning():
            return
        self._last_cmd = cmd
        self._last_output_lines = []
        self.terminal.appendPlainText(f"\n$ {' '.join(cmd)}\n")
        self._runner = CommandRunner(cmd)
        self._runner.output.connect(self.terminal.appendPlainText)
        self._runner.output.connect(self._last_output_lines.append)
        self._runner.finished.connect(self._on_finished)
        self.btn_go.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.statusBar().showMessage("Running...")
        self._runner.start()

    def _run_dtc(self):
        self._run_cmd(self._build_dtc_cmd())

    def _run_init(self):
        self.terminal.appendPlainText("$ dtc -c2\n")
        self.btn_go.setEnabled(False)
        self.statusBar().showMessage("Initializing KryoFlux...")
        self._init_output_lines = []
        self._init_runner = CommandRunner(["dtc", "-c2"])
        self._init_runner.output.connect(self.terminal.appendPlainText)
        self._init_runner.output.connect(self._init_output_lines.append)
        self._init_runner.finished.connect(self._on_init_finished)
        self._init_runner.start()

    def _on_init_finished(self, code):
        self.btn_go.setEnabled(True)
        if code != 0:
            self.statusBar().showMessage("Init failed.")
            return
        max_track = self._parse_max_track("\n".join(self._init_output_lines))
        if max_track is not None:
            _, spin_start, _, _ = self._opt_rows["start_track"]
            _, spin_end,   _, _ = self._opt_rows["end_track"]
            spin_start.setRange(0, max_track)
            spin_start.setValue(0)
            spin_end.setRange(0, max_track)
            spin_end.setValue(max_track)
            self.terminal.appendPlainText(f"\n[ Max track: {max_track} — spinboxes updated ]")
            self.statusBar().showMessage(f"Init OK — max track: {max_track}")
        else:
            self.terminal.appendPlainText("\n[ Could not detect max track ]")
            self.statusBar().showMessage("Init OK — max track not detected")

    def _parse_max_track(self, output: str):
        match = re.search(r"max[_\s]?track[=:\s]+(\d+)", output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search(r"[Tt]rack\s+(\d+)", output)
        if match:
            return int(match.group(1))
        return None

    def _run_mimage(self):
        src = self._zenity(["--file-selection",
                            "--title=Mimage: select source image",
                            f"--filename={self._config.get('source_dir', os.path.expanduser('~'))}/"])
        if not src:
            return
        out_dir = self._zenity(["--file-selection", "--directory",
                                "--title=Mimage: select output directory",
                                f"--filename={self._config.get('output_dir', os.path.expanduser('~'))}/"])
        if not out_dir:
            return
        base = os.path.splitext(os.path.basename(src))[0]
        self._run_cmd(["mimage", src, f"{out_dir}/{base}"])

    def _stop(self):
        if self._runner:
            self._runner.stop()

    def _on_finished(self, code):
        self.btn_go.setEnabled(True)
        self.btn_stop.setEnabled(False)
        status = "Done" if code == 0 else f"Exited with code {code}"
        self.terminal.appendPlainText(f"\n[ {status} ]")
        self.statusBar().showMessage(status)
        self._write_log()

    def _open_preferences(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Preferences")
        dialog.setFixedSize(480, 180)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        for label_text, config_key in [
            ("Default source image directory:", "source_dir"),
            ("Default output directory:",       "output_dir"),
        ]:
            layout.addWidget(QLabel(label_text))
            row = QHBoxLayout()
            edit = QLineEdit(self._config.get(config_key, ""))
            btn  = QPushButton("…")
            btn.setFixedWidth(28)
            def make_browse(e=edit, k=config_key):
                def browse():
                    p = self._zenity(["--file-selection", "--directory",
                                      f"--title=Select {k}",
                                      f"--filename={e.text()}/"])
                    if p:
                        e.setText(p)
                return browse
            btn.clicked.connect(make_browse())
            row.addWidget(edit)
            row.addWidget(btn)
            layout.addLayout(row)
            setattr(dialog, f"edit_{config_key}", edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_save   = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_save.setFixedWidth(80)
        btn_cancel.setFixedWidth(80)

        def save():
            self._config["source_dir"] = dialog.edit_source_dir.text().strip()
            self._config["output_dir"] = dialog.edit_output_dir.text().strip()
            self._save_config()
            dialog.accept()

        btn_save.clicked.connect(save)
        btn_cancel.clicked.connect(dialog.reject)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)
        dialog.exec()

    def _show_about(self):
        QMessageBox.about(
            self, "Volvex",
            f"Volvex {VERSION}\n"
            "© 2026 Roberto Chichiarelli\n\n"
            "GUI frontend for KryoFlux dtc and mimage.\n\n"
            "IMPORTANT: KryoFlux DTC (dtc) is proprietary software\n"
            "owned by KryoFlux Products & Services Ltd / SPS.\n"
            "Volvex does not include, modify or redistribute dtc.\n\n"
            "mimage © 2026 Roberto Chichiarelli\n"
            "github.com/Rob1c/Mimage\n\n"
            "Report bugs: roberto.chichiarelli@gmail.com"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    win = Volvex()
    win.show()
    sys.exit(app.exec())
