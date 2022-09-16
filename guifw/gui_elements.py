from tkinter import Menu
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

import typing

__all__ = [
    'MenuBar'
]


class MenuBar(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Policy.Maximum,
                           QSizePolicy.Policy.MinimumExpanding)

        self.items = []

    def add(self, widget: typing.Union[QWidget, typing.List[QWidget]]):
        if widget is not None:
            if hasattr(widget, '__iter__'):
                for w in widget:
                    self.add(w)
            else:
                if issubclass(widget.__class__, QWidget):
                    self.layout().addWidget(widget)
                elif issubclass(widget.__class__, QLayout):
                    self.layout().addLayout(widget)
                else:
                    raise TypeError(
                        f"Unexpected element of type {widget.__class__}")
                self.items.append(widget)
