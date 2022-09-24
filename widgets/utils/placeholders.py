#!/usr/bin/env python3
'''
A set of placeholder widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

import typing

from PyQt5 import QtCore, QtGui, QtWidgets


class PlaceHolder(QtWidgets.QLabel):
    '''
    A simple placeholder widget
    '''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("PlaceHolder")
        self.setText("This is a PlaceHolder")
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(350, 50)


class DockPlaceHolder(QtWidgets.QDockWidget):
    '''
    A dockable placeholder widget
    '''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("DockPlaceHolder")
        self.setWidget(QtWidgets.QLabel(
            parent=self.parentWidget(),
            text="This is a dockable PlaceHolder"))

        self.setAllowedAreas(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setMinimumSize(350, 50)

        if hasattr(self.parentWidget(), 'addDockWidget'):
            self.parentWidget().addDockWidget(
                QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self)
        else:
            self.setFloating(True)
            self.show()
