from PyQt5 import QtCore, QtGui, Qt
import numpy as np
from app_classes import *

def main():
    app = QtGui.QApplication([])

    mw = MainWindow()
    mw.show()

    app.exec_()

if __name__ == '__main__':
    main()