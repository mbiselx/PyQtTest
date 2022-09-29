#!/usr/bin/env python3
'''
A set of placeholder widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'PlaceHolder',
    'DockPlaceHolder',
    'GraphicPlaceholder',
    'GraphicDockPlaceholder'
]

import typing
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget


class PlaceHolder(QtWidgets.QLabel):
    '''
    A simple placeholder widget
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
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

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("DockPlaceHolder")
        self.setWidget(QtWidgets.QLabel(
            parent=self.parentWidget(),
            text="This is a dockable PlaceHolder"))
        self.setContentsMargins(0, 0, 0, 0)

        self.setAllowedAreas(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setMinimumSize(350, 50)

        if hasattr(self.parentWidget(), 'addDockWidget'):
            self.parentWidget().addDockWidget(
                QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self)
        else:
            self.setFloating(True)
            self.show()


class RandomGraphicPlotter(PlotWidget):
    '''
    a widget which plots random values
    '''

    def __init__(self,
                 parent=None,
                 data_range=[-100, -1],
                 background='default',
                 plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)

        self._data_range = data_range
        self._plot = self.plotItem.plot()
        self._data = []
        self._ts = []
        self._ts0 = QtCore.QTime.currentTime().msecsSinceStartOfDay()

        self.startTimer(200)

    def timerEvent(self, event: QtCore.QTimerEvent) -> None:
        now = QtCore.QTime.currentTime().msecsSinceStartOfDay() - self._ts0
        self._ts.append(now)
        self._data.append(np.random.random(1)[0])
        self._plot.setData(x=np.array(self._ts[self._data_range[0]:self._data_range[1]]),
                           y=np.array(self._data[self._data_range[0]:self._data_range[1]]))

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 500)


class GraphicPlaceholder(QtWidgets.QWidget):
    '''
    a free-standing widget for plotting random values
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 data_range: typing.List[int] = [-100, -1],
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("GraphicPlaceholder")

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(RandomGraphicPlotter(parent=self, data_range=data_range))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)


class GraphicDockPlaceholder(QtWidgets.QDockWidget):
    '''
    a dockable widget for plotting random values
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 data_range: typing.List[int] = [-100, -1],
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("GraphicDockPlaceholder")
        self.setWidget(RandomGraphicPlotter(parent=self,
                                            data_range=data_range))
        self.setContentsMargins(0, 0, 0, 0)

        self.setAllowedAreas(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setMinimumSize(350, 50)

        if hasattr(self.parentWidget(), 'addDockWidget'):
            self.parentWidget().addDockWidget(
                QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self)
        else:
            self.setFloating(True)
            self.show()
