"""---------------------------------------------------------------------------------------
 Module: playblast_manager_ui

 Author = Roberta Fischetti

 Date = 2026-09-01

 Description = Playblast Manager UI designed with Qt Designer
---------------------------------------------------------------------------------------"""

import os
import sys
import webbrowser

from Qt import QtWidgets, QtGui, QtCompat


#*******************************************************************
# VARIABLE
TITLE = os.path.splitext(os.path.basename(__file__))[0]
CURRENT_PATH = os.path.dirname(__file__)
IMG_PATH = CURRENT_PATH + "/img/{}.png"

#*******************************************************************
# CLASS
class SimpleUI():
    def __init__(self):
        # BUILD local ui path
        path_ui = "/".join([os.path.dirname(__file__), "ui", TITLE + ".ui"])

        # LOAD ui with absolute path
        self.wgUtil = QtCompat.loadUi(path_ui)

        # LOAD Button Icon
        self.wgUtil.btn_help.setIcon(QtGui.QPixmap(IMG_PATH.format("btn_help")))

        # SIGNAL
        self.wgUtil.btn_generatePlayblast.clicked.connect(self.press_btn_generatePlayblast)
        self.wgUtil.btn_help.clicked.connect(self.press_help)

        # SHOW the UI
        self.wgUtil.show()

    #************************************************************
    # PRESS
    def press_btn_generatePlayblast(self):
        print("Playblast generated!")

    def press_help(self):
        webbrowser.open("https://github.com/robertafischetti/picre/wiki")


#*******************************************************************
# START
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    classVar = SimpleUI()
    app.exec_()


