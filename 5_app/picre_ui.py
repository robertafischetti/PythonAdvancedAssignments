"""
ui.py
-----
The Playblast Manager panel. 
UI built using PySide6 (Maya 2025+). 
Maya itself is optional at import time -- outside Maya,
scene_utils/burnin/playblast_core all fall back to mocks (see those modules),
so this panel can be opened and clicked around in a plain desktop Python
session for layout/UX iteration without Maya running at all.
"""

import getpass
import os
import sys
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

try:
    import maya.cmds as cmds
    import maya.OpenMayaUI as omui
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

if MAYA_AVAILABLE:
    from shiboken6 import wrapInstance


# using QSS for the stylesheet

STYLESHEET = """
QWidget#root {
    background: palette(window);
}
QFrame#card {
    background: palette(window);
    border: 1px solid palette(mid);
    border-radius: 10px;
}
QLabel#panelTitle {
    font-size: 16px;
    font-weight: 600;
    color: palette(window-text);
}
QLabel#sectionHeader {
    font-size: 12px;
    font-weight: 600;
    color: palette(window-text);
}
QLabel#fieldLabel {
    font-size: 11px;
    color: palette(mid);
}
QPushButton#primaryBtn {
    background: palette(highlight);
    color: palette(highlighted-text);
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#primaryBtn:hover { palette(mid); }

"""


# Burn-in fields exposed in the UI and where they land in the schematic
# preview, kept in the same corners burnin.py actually writes HUDs to.
BURNIN_FIELD_ORDER = ["shot_name", "frame", "artist", "date", "camera_name"]

BURNIN_FIELD_LABELS = {
    "shot_name": "Shot name",
    "frame": "Frame number",
    "artist": "Artist",
    "date": "Date",
    "camera_name": "Camera",
}

BURNIN_DEFAULT_ON = {"shot_name", "frame", "artist"}

CORNER_FOR_FIELD = {
    "shot_name": "top_left",
    "camera_name": "top_right",
    "artist": "bottom_left",
    "date": "bottom_center",
    "frame": "bottom_right",
}


def maya_main_window():
    """Return Maya's main window as a QWidget parent, or None outside Maya."""
    if not MAYA_AVAILABLE:
        return None
    
    main_window_ptr = omui.MQtUtil.mainWindow()
    
    if main_window_ptr is None:
        return None
    
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class Card(QtWidgets.QFrame):
    """A white, rounded-corner section container."""

    def __init__(self, parent=None):
        super(Card, self).__init__(parent)
        self.setObjectName("card")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(10)


class BurninPreview(QtWidgets.QFrame):
    """
    Schematic preview of where burn-in text will land on the frame -- not a
    real render, just corner labels that update live as fields/checkboxes
    change. Deliberately mirrors DEFAULT_LAYOUT in burnin.py so what an
    artist sees here is where the text will actually appear on the playblast.
    """

    def __init__(self, parent=None):
        super(BurninPreview, self).__init__(parent)
        self.setObjectName("previewPanel")
        self.setMinimumHeight(140)

        grid = QtWidgets.QGridLayout(self)
        grid.setContentsMargins(14, 10, 14, 10)

       


class PlayblastManagerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PlayblastManagerWidget, self).__init__(parent)
        self.setObjectName("root")
        self.setWindowTitle("Playblast Manager")
        self.setStyleSheet(STYLESHEET)
        self.setMinimumWidth(560)

       # self._naming_config = load_naming_config(self._config_path())
        self._build_ui()

    # -- setup -------------------------------------------------------------


    def _build_ui(self):
        outer_window = QtWidgets.QVBoxLayout(self) # lines up child widgets in a vertical column from top to bottom
        outer_window.setContentsMargins(20, 20, 20, 20)
        outer_window.setSpacing(14)

        title_row = QtWidgets.QHBoxLayout() # construct horizontal box layout objects
        title = QtWidgets.QLabel("Playblast manager")
        title.setObjectName("panelTitle")
        title_row.addWidget(title)
        title_row.addStretch()
        outer_window.addLayout(title_row)

        outer_window.addWidget(self._build_capture_card())
        outer_window.addWidget(self._build_naming_card())
        outer_window.addWidget(self._build_burnin_card())
        outer_window.addLayout(self._build_bottom_buttons())


    def _labeled_field(self, label_text, widget):
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(3)
        label = QtWidgets.QLabel(label_text)
        label.setObjectName("fieldLabel")
        col.addWidget(label)
        col.addWidget(widget)
        return col

    def _build_capture_card(self):
        card = Card()
        header = QtWidgets.QLabel("Capture settings")
        header.setObjectName("sectionHeader")
        card.layout.addWidget(header)

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(16)
        card.layout.addLayout(row)

        return card

    def _build_naming_card(self):
        card = Card()
        header = QtWidgets.QLabel("Naming and path")
        header.setObjectName("sectionHeader")
        card.layout.addWidget(header)

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(16)

        card.layout.addLayout(row)

        return card

    def _build_burnin_card(self):
        card = Card()
        header = QtWidgets.QLabel("Burn-in overlays")
        header.setObjectName("sectionHeader")
        card.layout.addWidget(header)

        check_row = QtWidgets.QHBoxLayout()
        self.burnin_checks = {}
        for field in BURNIN_FIELD_ORDER:
            box = QtWidgets.QCheckBox(BURNIN_FIELD_LABELS[field])
            box.setChecked(field in BURNIN_DEFAULT_ON)
            self.burnin_checks[field] = box
            check_row.addWidget(box)
        check_row.addStretch()
        card.layout.addLayout(check_row)

        self.preview = BurninPreview()
        card.layout.addWidget(self.preview)

        return card

    def _build_bottom_buttons(self):
        row = QtWidgets.QHBoxLayout()
        row.addStretch()

        self.generate_btn = QtWidgets.QPushButton("Generate playblast")
        self.generate_btn.setObjectName("primaryBtn")
        # self.generate_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.generate_btn.setCursor(QtCore.Qt.PointingHandCursor)
        row.addWidget(self.generate_btn)
        return row


    # -- data in/out ---------------------------------------------------

    def _enabled_burnin_fields(self):
        return [f for f in BURNIN_FIELD_ORDER if self.burnin_checks[f].isChecked()]



 


def show():
    """Launch the panel, parented to Maya's main window if running inside Maya."""
    #global _pbm_widget
    parent = maya_main_window()
    _pbm_widget = PlayblastManagerWidget(parent)
    print(parent)
    print(_pbm_widget)
    if parent is not None:
        _pbm_widget.setWindowFlags(QtCore.Qt.Window)
    _pbm_widget.show()
    return _pbm_widget


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    widget = show()
    widget.raise_()
    widget.activateWindow()
    sys.exit(app.exec())
