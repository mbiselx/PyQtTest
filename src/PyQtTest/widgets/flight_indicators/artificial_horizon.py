#!/usr/bin/env python3
'''
An artificial horizon widget

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'ArtificalHorizon'
]

import math
import typing

from PyQt5 import QtCore, QtGui, QtWidgets


class SimpleArtificalHorizon(QtWidgets.QFrame):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.setRoll(0)
        self.setPitch(0, -30, 30, 10)

        p = QtGui.QPalette()
        p.setColor(p.ColorRole.Base, QtGui.QColor('Brown'))
        p.setColor(p.ColorRole.AlternateBase, QtGui.QColor('dodgerBlue'))
        self.setPalette(p)

        self.setLineWidth(3)

    def roll(self) -> float:
        return self._roll

    def setRoll(self, roll: float):
        self._roll = float(roll)
        self.update()

    def pitch(self) -> float:
        return self._pitch

    def setPitch(self, pitch: float, min_pitch: int = None, max_pitch: int = None, pitch_grad: int = None):
        self._pitch = float(pitch)
        if min_pitch is not None:
            self._min_pitch = int(min_pitch)
        if max_pitch is not None:
            self._max_pitch = int(max_pitch)
        if pitch_grad is not None:
            self._pitch_grad = int(pitch_grad)
        self.update()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 500)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        # get the largest possible square
        margin = 10
        if self.rect().width() < self.rect().height()-2*margin:
            pad = self.rect().height() - self.rect().width()
            self._square = QtCore.QRect(0, pad//2,
                                        self.rect().width(),
                                        self.rect().width())
        else:
            pad = self.rect().width() - self.rect().height()
            self._square = QtCore.QRect(pad//2+margin, margin,
                                        self.rect().height()-2*margin,
                                        self.rect().height()-2*margin)

        # reticule geometry :
        self._reticule = [
            QtCore.QPoint(self._square.center().x() - self._square.width()//4,
                          self._square.center().y()),
            QtCore.QPoint(self._square.center().x() - self._square.width()//10,
                          self._square.center().y()),
            QtCore.QPoint(self._square.center().x(),
                          self._square.center().y() + self._square.height()//10),
            QtCore.QPoint(self._square.center().x() + self._square.width()//10,
                          self._square.center().y()),
            QtCore.QPoint(self._square.center().x() + self._square.width()//4,
                          self._square.center().y())
        ]

        # roll indicator geometry :
        self._roll_indicator = QtGui.QPolygon([
            QtCore.QPoint(self._square.center().x(),
                          self._square.top()),
            QtCore.QPoint(self._square.center().x()-10,
                          self._square.top()+25),
            QtCore.QPoint(self._square.center().x()+10,
                          self._square.top()+25),
        ])

        # pitch graduation geometry :
        self._pitch_graduations = []
        for pitch_mark in range(self._min_pitch, self._max_pitch+self._pitch_grad, self._pitch_grad):
            lbl = f"{pitch_mark}°"
            h = (self._square.width() * math.sin(pitch_mark/180*3.1415926))//2
            mark = QtCore.QLine(self._square.center().x()-self._square.width()//30-2*abs(pitch_mark),
                                self._square.center().y() + h,
                                self._square.center().x()+self._square.width()//30+2*abs(pitch_mark),
                                self._square.center().y() + h)
            pos = QtCore.QPoint(self._square.center().x() - self.fontMetrics().boundingRect(lbl).width()//2,
                                self._square.center().y() + h - 3)
            self._pitch_graduations.append((mark, lbl, pos))

        # roll graduations :
        self._roll_graduations = []
        ro = self._square.height()//2 + 1
        ri = ro + 5
        for roll_mark in range(-40, 50, 10):
            # lbl = f"{roll_mark}°"
            s = math.sin(roll_mark/180*3.1415926)
            c = math.cos(roll_mark/180*3.1415926)
            mark = QtCore.QLine(self._square.center().x() + int(s*ro),
                                self._square.center().y() - int(c*ro),
                                self._square.center().x() + int(s*ri),
                                self._square.center().y() - int(c*ri))
            self._roll_graduations.append(mark)

        a0.accept()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # 1) paint the moving background
        bg = QtGui.QPainter(self)
        bg.setPen(QtCore.Qt.PenStyle.NoPen)  # no outlines

        # apply roll
        bg.translate(self.rect().center())
        bg.rotate(self._roll)
        bg.translate(-self.rect().center())

        # draw the ground
        bg.setBrush(self.palette().base())
        bg.drawChord(self._square,
                     (180+self._pitch) * 16,
                     (180-2*self._pitch)*16)
        # draw the sky
        bg.setBrush(self.palette().alternateBase())
        bg.drawChord(self._square,
                     -self._pitch * 16,
                     (180+2*self._pitch)*16)

        # draw roll indicator
        bg.setBrush(self.palette().brightText())
        bg.drawConvexPolygon(self._roll_indicator)

        # draw graduations
        bg.setPen(QtCore.Qt.PenStyle.SolidLine)
        for mark, lbl, pos in self._pitch_graduations:
            bg.drawLine(mark)
            bg.drawText(pos, lbl)

        bg.end()

        # 2) paint the static overlay
        rt = QtGui.QPainter(self)
        rt.setPen(QtGui.QPen(
            self.palette().brightText().color(), self.lineWidth()))
        rt.drawPolyline(*self._reticule)

        rt.setPen(QtGui.QPen(
            self.palette().windowText().color(), self.lineWidth()))
        for mark in self._roll_graduations:
            rt.drawLine(mark)
        rt.end()


class HorizonTestWidget(QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.testWidget = SimpleArtificalHorizon(self)

        rollslider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        rollslider.setRange(-90, 90)
        rollslider.valueChanged.connect(lambda v: self.testWidget.setRoll(v))

        pitchslider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical, self)
        pitchslider.setRange(-20, 20)
        pitchslider.valueChanged.connect(lambda v: self.testWidget.setPitch(v))

        self.setLayout(QtWidgets.QGridLayout())
        self.layout().addWidget(pitchslider, 0, 0)
        self.layout().addWidget(self.testWidget, 0, 1)
        self.layout().addWidget(rollslider, 1, 1)

    def sizeHint(self) -> QtCore.QSize:
        return self.testWidget.sizeHint()
