#!/usr/bin/env python3
'''
A file used for testing

Author  :   Michael Biselx
Date    :   10.2022
Project :   PyQtTest
'''

from PyQt5 import QtCore, QtWidgets

from PyQtTest.widgets.hud.navball_pyqtgraph import NavballWidget
from PyQtTest.widgets.utils.reloadable_widget import ReloadableWidget

if __name__ == '__main__':
    import sys

    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = ReloadableWidget(
        flags=QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.WindowCloseButtonHint,
        widget=NavballWidget
    )
    mw.show()
    print("widget has been shown")

    sys.exit(app.exec_())
