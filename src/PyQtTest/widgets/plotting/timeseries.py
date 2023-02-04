#!/usr/bin/env python3
'''
A set of placeholder widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'InspectionPlot',
    'MasterTimeLinePlot'
]

import typing
import warnings
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

try:
    from .colors import ColorIterator
except ImportError:  # in case we're using the demo
    from PyQtTest.widgets.plotting.colors import ColorIterator


class InspectionPlot(pg.PlotWidget):
    '''A plot widget used for close-up timeseries inspection'''
    __depends__ = [
        ColorIterator
    ]

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


class MasterTimeLinePlot(pg.PlotWidget):
    '''The master timeseries plot, which can control other inspection plots'''
    sigRegionChanged = QtCore.pyqtSignal(object)
    sigPositionChanged = QtCore.pyqtSignal(pg.InfiniteLine)

    __depends__ = [
        ColorIterator
    ]

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

        self.inspection_plots: 'list[InspectionPlot]' = []

    def register_inspectionPlot(self, plot: InspectionPlot):
        self.inspection_plots.append(plot)

    def remove_inspectionPlot(self, plot: InspectionPlot):
        try:
            self.inspection_plots.remove(plot)
        except Exception as e:
            warnings.warn(str(e))

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
        for plot in self.inspection_plots:
            plot.updateXRange(lr)
        self.sigRegionChanged.emit(lr)

    def updateTime(self, ln: pg.InfiniteLine):
        for plot in self.inspection_plots:
            plot.updateXPos(ln)
        self.sigPositionChanged.emit(ln)


############################################
#  DEMO
############################################
if __name__ == '__main__':
    import sys

    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    _data1 = np.array(np.random.random(100))
    _data2 = np.array(np.random.random(_data1.shape[0]))
    _ts = np.linspace(0,
                      _data1.shape[0] * 10,
                      _data1.shape[0])

    tp = MasterTimeLinePlot()
    tp.setData(x=_ts, y=_data1)
    tp.show()

    ip = InspectionPlot()
    for _data in [_data1, _data2]:
        ip.addData(x=_ts, y=_data)
    ip.show()

    tp.register_inspectionPlot(ip)

    sys.exit(app.exec_())
