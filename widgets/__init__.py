
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

from guifw.gui_elements import MenuBar

import collections
import typing


from .utils import PlaceHolder


class WidgetMaker(MenuBar):
    widgetDict = collections.OrderedDict([
        ("PlaceHolder", PlaceHolder)
    ])

    def __init__(self, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.combo = QComboBox(self)
        for lbl, w in self.widgetDict.items():
            self.combo.addItem(lbl, userData=w)

        makeBtn = QToolButton(self)
        makeBtn.setText(' + ')
        makeBtn.clicked.connect(self.makeWidget)

        self.add([self.combo, makeBtn])

    def makeWidget(self):
        w = self.combo.currentData(QtCore.Qt.ItemDataRole.UserRole)
        w(parent=self.parentWidget(), flags=QtCore.Qt.WindowType.Window).show()
