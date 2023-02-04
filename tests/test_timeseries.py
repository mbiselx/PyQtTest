#!/usr/bin/env python3
'''
A file used for testing

Author  :   Michael Biselx
Date    :   11.2022
Project :   PyQtTest
'''

import sys
import logging
import numpy as np

from PyQt5 import QtCore, QtWidgets

from PyQtTest.widgets.utils.reloadable_widget import ReloadableWidget
from PyQtTest.widgets.plotting.timeseries import MasterTimeLinePlot, InspectionPlot


class TestWidget(QtWidgets.QFrame):
    '''this is basically just a frame to hold the'''
    __depends__ = [
        MasterTimeLinePlot,
        InspectionPlot
    ]

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)

        # prepare data
        _data1 = np.array(np.random.random(100))
        _data2 = np.array(np.random.random(_data1.shape[0]))
        _ts = np.linspace(0,
                          _data1.shape[0] * 10,
                          _data1.shape[0])

        # create plots
        self.timeline = MasterTimeLinePlot(self)
        self.timeline.setData(x=_ts, y=_data1)

        self.inspection = InspectionPlot(self)
        for _data in (_data1, _data2):
            self.inspection.addData(x=_ts, y=_data)

        # register inspector to timeline
        self.timeline.register_inspectionPlot(self.inspection)

        # do layout
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(self.inspection)
        self.layout().addWidget(self.timeline)

    def sizeHint(self) -> QtCore.QSize:
        return super().sizeHint().expandedTo(QtCore.QSize(500, 500))

    def close(self) -> bool:
        self.timeline.close()
        self.inspection.close()
        return super().close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = ReloadableWidget(
        flags=QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.WindowCloseButtonHint,
        widget=TestWidget,
    )
    mw.show()
    print("widget has been shown")

    sys.exit(app.exec_())
