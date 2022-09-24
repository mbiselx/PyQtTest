#!/usr/bin/env python3
'''
A file used for testing

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''
import typing


from PyQt5 import QtCore, QtGui, QtWidgets

from widgets.utils import StandardMenuBar
from widgets.hud import CameraTabs


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Window) -> None:
        super().__init__(parent, flags)

        self.setMenuWidget(StandardMenuBar(self))

        self.setCentralWidget(CameraTabs(self))
        self.centralWidget().addTab(0)
        self.setWindowTitle("Test Window")

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(max(super().sizeHint().width(), self.menuWidget().sizeHint().width()),
                            super().sizeHint().height())


if __name__ == '__main__':
    import sys

    print(f"running {__file__} as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = MyMainWindow()
    mw.show()

    sys.exit(app.exec_())
