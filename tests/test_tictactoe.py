#!/usr/bin/env python3
'''
A file used for testing

Author  :   Michael Biselx
Date    :   10.2022
Project :   PyQtTest
'''

import sys
import logging

from PyQt5 import QtCore, QtWidgets

from PyQtTest.widgets.utils.reloadable_widget import ReloadableWidget
from PyQtTest.widgets.tictactoe.gui_utils import TicTacToeGame

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = ReloadableWidget(
        flags=QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.WindowCloseButtonHint,
        widget=TicTacToeGame,
    )
    mw.show()
    print("widget has been shown")

    sys.exit(app.exec_())
