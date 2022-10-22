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


class AbstractArtificalHorizon(QtWidgets.QFrame):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)
        self.setRoll(0, -30, 30, 5)
        self.setPitch(0, -30, 30, 10)

    def roll(self) -> float:
        return self._roll

    def setRoll(self, roll: float, min_roll: int = None, max_roll: int = None, roll_ticks: int = None):
        self._roll = float(roll)
        if min_roll is not None:
            self._min_roll = int(min_roll)
        if max_roll is not None:
            self._max_roll = int(max_roll)
        if roll_ticks is not None:
            self._roll_ticks = int(roll_ticks)
        self.update()

    def pitch(self) -> float:
        return self._pitch

    def setPitch(self, pitch: float, min_pitch: int = None, max_pitch: int = None, pitch_ticks: int = None):
        self._pitch = float(pitch)
        if min_pitch is not None:
            self._min_pitch = int(min_pitch)
        if max_pitch is not None:
            self._max_pitch = int(max_pitch)
        if pitch_ticks is not None:
            self._pitch_ticks = int(pitch_ticks)
        self.update()

    def _height_from_pitch(self, pitch) -> int:
        return self._square.center().y() + (self._square.height() * math.sin(pitch/180*3.1415926))//2

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
        for pitch_mark in range(self._min_pitch, self._max_pitch+self._pitch_ticks, self._pitch_ticks):
            lbl = f"{pitch_mark}°"
            h = self._height_from_pitch(pitch_mark)
            mark = QtCore.QLine(self._square.center().x()-self._square.width()//30-2*abs(pitch_mark), h,
                                self._square.center().x()+self._square.width()//30+2*abs(pitch_mark), h)
            pos = QtCore.QPoint(self._square.center().x() - self.fontMetrics().boundingRect(lbl).width()//2,
                                h - 3)
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


class SimpleArtificalHorizon(AbstractArtificalHorizon):
    darkPalette = QtGui.QPalette()
    darkPalette.setColor(QtGui.QPalette.ColorRole.Base,
                         QtGui.QColor('SaddleBrown'))
    darkPalette.setColor(QtGui.QPalette.ColorRole.AlternateBase,
                         QtGui.QColor('DodgerBlue'))
    lightPalette = QtGui.QPalette()
    lightPalette.setColor(QtGui.QPalette.ColorRole.Base,
                          QtGui.QColor('Chocolate'))
    lightPalette.setColor(QtGui.QPalette.ColorRole.AlternateBase,
                          QtGui.QColor('LightSkyBlue'))

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.setPalette(self.lightPalette)
        self.setLineWidth(3)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 500)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # 1) paint the moving background
        bg = QtGui.QPainter(self)
        bg.setPen(QtCore.Qt.PenStyle.NoPen)  # no outlines

        # apply roll
        bg.translate(self.rect().center())
        bg.rotate(-self._roll)
        bg.translate(-self.rect().center())

        # draw the ground
        bg.setBrush(self.palette().base())
        bg.drawEllipse(self._square)
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


class HUDArtificalHorizon(AbstractArtificalHorizon):
    darkPalette = QtGui.QPalette()
    darkPalette.setColor(QtGui.QPalette.ColorRole.Highlight,  # elements
                         QtGui.QColor('Gold'))
    darkPalette.setColor(QtGui.QPalette.ColorRole.BrightText,  # text
                         QtGui.QColor('ForestGreen'))
    lightPalette = QtGui.QPalette()
    lightPalette.setColor(QtGui.QPalette.ColorRole.Highlight,
                          QtGui.QColor('yellow'))
    lightPalette.setColor(QtGui.QPalette.ColorRole.BrightText,
                          QtGui.QColor('lime'))

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.setPalette(self.darkPalette)
        self.setLineWidth(3)
        f = self.font()
        f.setFamily('Comic Sans MS')
        f.setPointSize(14)
        self.setFont(f)

        self.blur = QtWidgets.QGraphicsBlurEffect(self)
        self.blur.setBlurRadius(1.7)
        self.setGraphicsEffect(self.blur)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 500)

    def setBlurred(self, active):
        '''enable/disable a slight blur effect to make the HUD more HUD-y'''
        self.blur.setEnabled(active)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # 1) paint the moving horizon
        bg = QtGui.QPainter(self)
        bg.setPen(QtGui.QPen(
            self.palette().highlight().color(), self.lineWidth()))

        # apply roll
        bg.translate(self.rect().center())
        bg.rotate(-self._roll)
        bg.translate(-self.rect().center())

        # draw the ground
        h = self._height_from_pitch(self._pitch)
        bg.drawLine(-1000000, h, self.width()+1000000, h)

        # draw roll indicator
        bg.setPen(QtCore.Qt.PenStyle.NoPen)
        bg.setBrush(self.palette().highlight())
        bg.drawConvexPolygon(self._roll_indicator)

        # draw graduations
        bg.setPen(QtGui.QPen(
            self.palette().brightText().color(), 1))
        for mark, lbl, pos in self._pitch_graduations:
            bg.drawLine(mark)
            bg.drawText(pos, lbl)

        bg.end()

        # 2) paint the static overlay
        rt = QtGui.QPainter(self)
        rt.setPen(QtGui.QPen(
            self.palette().highlight().color(), self.lineWidth()))
        rt.drawPolyline(*self._reticule)

        rt.setPen(QtGui.QPen(
            self.palette().brightText().color(), self.lineWidth()))
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


class FunHorizonTestWidget(HUDArtificalHorizon):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        from ...sensors import imu

        def updateOrientation():
            r, p, y = imu.get_current_euler_deg()
            # print(r, p, y)
            self.setRoll(r)
            self.setPitch(p)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(updateOrientation)
        self.timer.start()
