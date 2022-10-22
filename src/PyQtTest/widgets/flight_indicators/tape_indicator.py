#!/usr/bin/env python3
'''
A tape-type (or: rolling drum-type) indicator

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'TapeIndicator'
]

import typing

from PyQt5 import QtCore, QtGui, QtWidgets


class TapeIndicator(QtWidgets.QFrame):
    '''
    A tape-type (or: rolling drum-type) indicator, useful for displaying 
    unbounded one-dimensional values (e.g. altitude or airspeed)
    '''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        # the current value to display
        self._value_formatstr = "{:.2f}"
        self.setLineWidth(3)  # with of the geometry lines
        self.setRelativeRange(low=1, high=1)
        self.setTick(major_tick=.2, minor_tick=.2/5)
        self.setTickFormat()  # using default vals
        self.setValue(0)

        # create the geometry :
        self._createGeometry()

    def value(self) -> float:
        '''get the current value being displayed'''
        return self._value

    def setValue(self, value: float, formatstr: str = None):
        '''set the value to display (updates the widget)'''
        self._value = float(value)
        if formatstr is not None:
            self._value_formatstr = str(formatstr)

        # we take the time here to calculate the new positions for the tickmarks
        # 0) reset
        self._major_ticks = []
        self._minor_ticks = []

        # 1) get the major tick marks in the current range
        major_top = ((self._value + self._hi)/self._major_tick_spacing//1) * \
            self._major_tick_spacing
        for n in range(int((self._hi + self._lo)/self._major_tick_spacing)):
            val = major_top-n*self._major_tick_spacing
            pos = (self._value - val + self._hi) / (self._hi + self._lo)
            self._major_ticks.append((self._tick_formatstr.format(val), pos))

        # 2) get the minor tick marks in the current range
        if self._minor_tick_spacing is not None:
            maj_tk_pos = [t[1] for t in self._major_ticks]
            minor_top = ((self._value + self._hi) /
                         self._minor_tick_spacing//1)*self._minor_tick_spacing
            for n in range(int((self._hi + self._lo)/self._minor_tick_spacing)):
                val = minor_top-n*self._minor_tick_spacing
                pos = (self._value - val + self._hi) / (self._hi + self._lo)
                # avoid drawing two ticks in the same spot (it's bad for transparancy)
                if not any(abs(pos - mj) < 1e-6 for mj in maj_tk_pos):
                    self._minor_ticks.append(pos)

        self.update()

    def setRelativeRange(self, low: float, high: float):
        '''set the upper and lower range to display. Will be applied on the next setValue'''
        if low < 0 or high < 0:
            raise ValueError(
                "Relative ranges are expected to be positive or zero")
        self._lo = float(low)
        self._hi = float(high)

    def setTick(self, major_tick: float, minor_tick: float = None):
        '''set tick mark spacing. Will be applied on the next setValue'''
        self._major_tick_spacing = float(major_tick)
        if minor_tick is not None:
            self._minor_tick_spacing = float(minor_tick)  # throw TypeErrors
        else:
            self._major_tick_spacing = None

    def setTickFormat(self, formatstr: str = '{:.1f}', tick_length_px: int = 10, line_width_px: int = 2):
        '''set formatstring used for tick mark value. Will be applied on the next setValue'''
        self._tick_formatstr = str(formatstr)
        self._tick_length = int(tick_length_px)
        self._tick_width = int(line_width_px)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        '''re-generates the geometry on resize'''
        self._createGeometry()
        a0.accept()

    def minimumSizeHint(self) -> QtCore.QSize:
        val_rect = self.fontMetrics().boundingRect(
            self._value_formatstr.format(self._value)+'0')
        return QtCore.QSize(2*val_rect.width()+self._tick_length, 100)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(300, 500)

    def _createGeometry(self):
        '''create the fixed geometry'''
        self._vertLine = [
            QtCore.QPoint(self.width()//2, self.rect().top()),
            QtCore.QPoint(self.width()//2, self.rect().bottom()),
        ]
        self._indicator = [
            QtCore.QPoint(self.width()//2, self.height()//2),
            QtCore.QPoint(self.width(), self.height()//2),
        ]
        self._valuelbl = QtCore.QPoint(3*self.width()//4, self.height()//2-5)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        '''draws the widget'''
        # create the gradient used for drawing the text
        tg = QtGui.QLinearGradient(0.5, 0., .5, self.height())
        tg.setColorAt(0.01,
                      QtCore.Qt.GlobalColor.transparent)
        tg.setColorAt(.3,
                      self.palette().color(
                          QtGui.QPalette.ColorRole.WindowText))
        tg.setColorAt(.7,
                      self.palette().color(
                          QtGui.QPalette.ColorRole.WindowText))
        tg.setColorAt(0.99,
                      QtCore.Qt.GlobalColor.transparent)

        p = QtGui.QPainter(self)
        p.setPen(QtGui.QPen(tg, self.lineWidth()))

        # draw the fixed geometry
        p.drawLine(*self._vertLine)
        p.drawLine(*self._indicator)

        # draw the value
        lbl = self._value_formatstr.format(self._value)
        rect = self.fontMetrics().tightBoundingRect(lbl)
        p.drawText(self._valuelbl.x() - rect.width() //
                   2, self._valuelbl.y(), lbl)

        # draw the tick marks
        p.setPen(QtGui.QPen(tg, self._tick_width))
        mid = self.width()//2
        for lbl, pos in self._major_ticks:
            rect = self.fontMetrics().tightBoundingRect(lbl)
            p.drawLine(mid-self.lineWidth()//2, pos*self.height(),
                       mid-self._tick_length, pos*self.height())
            p.drawText(mid-self._tick_length-5-rect.width(),
                       pos*self.height() + rect.height()//2,
                       lbl)

        p.setPen(QtGui.QPen(tg, 1))
        for pos in self._minor_ticks:
            p.drawLine(mid-self.lineWidth()//2, pos*self.height(),
                       mid-self._tick_length//2, pos*self.height())

        p.end()


class TapeTestWidget(QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        testWidget = TapeIndicator(self)
        testWidget.setTickFormat('{:.1f}')
        testWidget.setValue(10, '{:.1f}m')

        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical, self)
        slider.valueChanged.connect(lambda v: testWidget.setValue(v/10 + 10))

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(slider)
        self.layout().addWidget(testWidget)
