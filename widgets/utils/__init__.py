from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

import typing


class PlaceHolder(QLabel):
    def __init__(self, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setText("This is a PlaceHolder")
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
