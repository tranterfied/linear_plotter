from PyQt4 import QtGui
from app_classes import *

def main():
    app = QtGui.QApplication([])

    mw = MainWindow()
    mw.show()

    app.exec_()

if __name__ == '__main__':
    main()