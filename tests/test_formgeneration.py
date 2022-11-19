#!/usr/bin/env python3
'''
A file used for testing

Author  :   Michael Biselx
Date    :   11.2022
Project :   PyQtTest
'''

import sys
import logging

from PyQt5 import QtCore, QtWidgets

from PyQtTest.widgets.utils.reloadable_widget import ReloadableWidget
from PyQtTest.widgets.form_generation.form_generation import FormDisplay

from PyQtTest.resources import get_path_to_template

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = ReloadableWidget(
        flags=QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.WindowCloseButtonHint,
        widget=FormDisplay,
        form=get_path_to_template('testing_template.yaml'))
    mw.show()
    print("widget has been shown")

    sys.exit(app.exec_())
