#!/usr/bin/env python3
'''
A set of placeholder widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

import typing
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg


class ColorIterator():
    '''automatically iterate though colors'''
    colors = [(255, 255, 255),  # white
              (255, 000, 000),  # red
              (255, 215, 000),  # gold
              (000, 255, 000),  # lime
              (000, 255, 215),  # forest
              (000, 000, 255),  # blue
              (215, 000, 255)  # purple
              ]

    def __init__(self) -> None:
        self.i = 0

    def reset(self):
        self.i = 0

    def __iter__(self) -> None:
        '''iterator to run though all available colors'''
        return self.colors

    def __next__(self) -> 'tuple[int, int, int]':
        '''get the next color in a loop, as follows: 

        ```
        ci = ColorIterator()
        color1 = next(ci)
        color2 = next(ci)
        ...
        ```
        '''
        self.i = self.i + 1 if self.i < len(self.colors)-1 else 0
        print(self.colors[self.i])
        return self.colors[self.i]


class TimeLinePlot(pg.PlotWidget):
    sigRegionChanged = QtCore.pyqtSignal(object)
    sigPositionChanged = QtCore.pyqtSignal(pg.InfiniteLine)

    def __init__(self,
                 parent=None,
                 background='default',
                 plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, name='timeline', ** kargs)

        self.colorIterator = ColorIterator()

        plt = self.plotItem.plot()
        self.plotItem.setMouseEnabled(False, False)

        lr = pg.LinearRegionItem()
        lr.sigRegionChanged.connect(self.updateDataRange)
        self.plotItem.addItem(lr)

        ln = pg.InfiniteLine(0, movable=True)
        ln.sigPositionChanged.connect(self.updateTime)
        self.plotItem.addItem(ln)

    def setData(self, x: np.ndarray = None, y: np.ndarray = None):
        self.plotItem.clearPlots()
        self.colorIterator.reset()
        self.addData(x, y)

    def addData(self, x: np.ndarray = None, y: np.ndarray = None, **kwargs):
        if 'pen' in kwargs:
            pen = kwargs.pop('pen')
        else:
            pen = pg.mkPen(width=2, color=next(self.colorIterator))

        self.plotItem.addItem(pg.PlotDataItem(x=x, y=y, pen=pen, **kwargs))

    def updateDataRange(self, lr: pg.LinearRegionItem):
        self.sigRegionChanged.emit(lr)

    def updateTime(self, ln: pg.InfiniteLine):
        self.sigPositionChanged.emit(ln)


class InspectionPlot(pg.PlotWidget):

    def __init__(self,
                 parent=None,
                 background='default',
                 plotItem=None,
                 **kargs):
        super().__init__(parent, background, plotItem, **kargs)

        self.colorIterator = ColorIterator()
        plt = self.plotItem.plot()

    def setData(self, x: np.ndarray = None, y: np.ndarray = None):
        self.plotItem.clearPlots()
        self.colorIterator.reset()
        self.addData(x, y)

    def addData(self, x: np.ndarray = None, y: np.ndarray = None, **kwargs):
        if 'pen' in kwargs:
            pen = kwargs.pop('pen')
        else:
            pen = pg.mkPen(width=2, color=next(self.colorIterator))

        self.plotItem.addItem(pg.PlotDataItem(x=x, y=y, pen=pen, **kwargs))

    def updateXRange(self, lr: pg.LinearRegionItem):
        self.setXRange(*lr.getRegion(), padding=0)

    def updateXPos(self, ln: pg.InfiniteLine):
        if not hasattr(self, 'ln'):
            self.ln = pg.InfiniteLine(0)
            self.plotItem.addItem(self.ln)
        self.ln.setPos(ln.getPos())


if __name__ == '__main__':
    import sys

    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    _data1 = np.array(np.random.random(100))
    _data2 = np.array(np.random.random(_data1.shape[0]))
    _ts = np.linspace(0,
                      _data1.shape[0] * 10,
                      _data1.shape[0])

    tp = TimeLinePlot()
    tp.setData(x=_ts, y=_data1)
    tp.show()

    ip = InspectionPlot()
    ip.addData(x=_ts, y=_data1)
    ip.addData(x=_ts, y=_data2)
    ip.show()

    tp.sigRegionChanged.connect(ip.updateXRange)
    tp.sigPositionChanged.connect(ip.updateXPos)

    sys.exit(app.exec_())
