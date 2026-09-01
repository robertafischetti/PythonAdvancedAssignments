"""
content = assignment
course  = Python Advanced
 
date    = 14.11.2025
email   = contact@alexanderrichtertd.com
"""


import os
import sys
import webbrowser

from Qt import QtWidgets, QtGui, QtCore, QtCompat


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

        # LOAD Icons
        self.wgUtil.setWindowIcon(QtGui.QPixmap(IMG_PATH.format("btn_accept")))
        self.wgUtil.btnAccept.setIcon(QtGui.QPixmap(IMG_PATH.format("btn_accept")))
        #print(IMG_PATH.format("btn_accept.png"))
        self.wgUtil.btnHelp.setIcon(QtGui.QPixmap(IMG_PATH.format("btn_help")))

        # BUTTON
        self.wgUtil.btnAccept.clicked.connect(self.press_accept)
        self.wgUtil.btnHelp.clicked.connect(self.press_help)

        # SHOW the UI
        self.wgUtil.show()



    #************************************************************
    # PRESS
    def press_accept(self):
        print("You accepted this process!")

    def press_help(self):
        webbrowser.open("https://www.alexanderrichtertd.com")


#*******************************************************************
# START
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    classVar = SimpleUI()
    app.exec_()

