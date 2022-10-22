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


class AbstractTapeIndicator(QtWidgets.QFrame):
    '''
    An abstract class defining the tape (rolling-drum) type of indicator.
    The abstract Tape indicator draws nothing, it is mostly used to define the API.

    It is based on the QFrame widget, since this already has the lineWidth
    and midLineWidth methods.
    '''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self._alignment = QtCore.Qt.AlignmentFlag.AlignLeft  # default alignment
        self._inverted = False  # default is not inverted
        self._value = 0  # default value
        self._value_formatstr = "{:.2f}"  # default format string for the value
        self._tick_formatstr = "{:.2f}"  # default format string for the ticks
        self._lo, self._hi = -1., +1.  # default display range
        self._major_tick_interval = .2  # default major tick interval
        self._minor_tick_frequency = 5  # default number of minor ticks per major tick

    def setAlignment(self, alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignLeft):
        '''set the alignment of the widget. only `right`, `left`, `top` and `bottom` are allowed'''
        alignment = QtCore.Qt.AlignmentFlag(alignment)
        if not alignment in (QtCore.Qt.AlignmentFlag.AlignLeft, QtCore.Qt.AlignmentFlag.AlignRight, QtCore.Qt.AlignmentFlag.AlignTop, QtCore.Qt.AlignmentFlag.AlignBottom):
            raise ValueError("alignment must be a QtCore.Qt.AlignmentFlag, "
                             f"not {alignment!s}")
        self._alignment: QtCore.Qt.AlignmentFlag = alignment
        self.update()

    def alignment(self) -> QtCore.Qt.AlignmentFlag:
        '''get the current alignment'''
        return self._alignment

    def setInverted(self, active: bool):
        '''set an inverted appearance'''
        self._inverted = bool(active)
        self.update()

    def inverted(self) -> bool:
        '''does the widget have an inverted appearance'''
        return self._inverted

    def setValue(self, value: float, formatstr: str = None):
        '''set the value to display'''
        self._value = float(value)
        if formatstr is not None:
            # try it out so any errors are thrown immedately
            formatstr.format(value)
            self._value_formatstr = str(formatstr)
        self.update()

    def value(self) -> float:
        '''get the current value being displayed'''
        return self._value

    def setRelativeRange(self, low: float, high: float):
        '''set the upper and lower range to display'''
        if float(low) > 0:
            raise ValueError(
                f"Lower bound of the range must be <= 0, not {low}")
        if float(high) < 0:
            raise ValueError(
                f"Upper bound of the range must be >= 0, not {high}")
        self._lo = float(low)
        self._hi = float(high)
        self.update()

    def relativeRange(self) -> 'tuple[float, float]':
        '''get the current relative range'''
        return self._lo, self._hi

    def setTickInterval(self, interval: float, formatstr: str = None):
        '''set the tick mark spacing for major (labeled) ticks'''
        if float(interval) <= 0:
            raise ValueError(f"Major Tick interval must be greater than 0!")
        self._major_tick_interval = float(interval)
        if formatstr is not None:
            # try it out so any errors are thrown immedately
            formatstr.format(interval)
            self._tick_formatstr = str(formatstr)
        self.update()

    def tickInterval(self) -> float:
        '''get the tick mark spacing for the major (labeled) ticks'''
        return self._major_tick_interval

    def setMinorTickFrequency(self, freq: int):
        '''set the number of minor ticks per major (labeled) tick'''
        if int(freq) < 0:
            raise ValueError(f"Minor Tick frequency must be at least 0!")
        self._minor_tick_frequency = int(freq)
        self.update()

    def minorTickFrequency(self) -> int:
        '''get the number of minor ticks per major (labeled) tick'''
        return self._minor_tick_frequency

    def _generate_ticks(self) -> 'tuple[list[tuple[str, float]], list[float]]':
        '''generate the tick values'''
        # 0) reset
        major_ticks = []
        minor_ticks = []

        # 2) calculate the highest major tick
        major_top = int((self._value + self._hi)/self._major_tick_interval) * \
            self._major_tick_interval

        # 3) using this as a reference, generate all lower major ticks
        for n in range(int((self._hi - self._lo)/self._major_tick_interval)):
            val = major_top-n*self._major_tick_interval
            pos = (self._value - val + self._hi) / (self._hi - self._lo)
            major_ticks.append((self._tick_formatstr.format(val), pos))

        # 4) if required, generate minor ticks
        if self._minor_tick_frequency > 0:
            minor_tick_interval = self._major_tick_interval / \
                self._minor_tick_frequency / (self._hi - self._lo)
            # 4.1) generate the minor ticks above the top-most major tick
            minor_ticks = [
                major_ticks[0][-1] - n * minor_tick_interval for n in range(1, self._minor_tick_frequency)]

            # 4.2) generate all the minor ticks below this
            for _, pos in major_ticks:
                minor_ticks.extend(
                    pos + n*minor_tick_interval for n in range(1, self._minor_tick_frequency))

        # 5) apply inversion, if necessary
        if self._inverted:
            major_ticks = [(l, 1-p) for l, p in major_ticks]
            minor_ticks = [1-p for p in minor_ticks]

        return major_ticks, minor_ticks


class TapeIndicator(AbstractTapeIndicator):
    '''
    A tape-type (or: rolling drum-type) indicator, useful for displaying
    unbounded one-dimensional values (e.g. altitude or airspeed)

    The palette is made up of two colors : 
    * `Foreground` : for the gemotrical elements
    * `BrightText` : for the textual elements

    The withd of the fixed geometrical elements can be set using the 
    `setMidLineWidth()` method, while the width of the tick marks may 
    be set using the `setLineWidth()` method.

    The alignement is set using the `setAlignment()` method. Additionally, 
    the orientation may be inverted (i.e. increasing towards the bottom/left) 
    using the `setInverted()` method.
    '''
    darkPalette = QtGui.QPalette()
    darkPalette.setColor(QtGui.QPalette.ColorRole.Foreground,  # elements
                         QtGui.QColor('limeGreen'))
    darkPalette.setColor(QtGui.QPalette.ColorRole.BrightText,  # text
                         QtGui.QColor('ForestGreen'))
    lightPalette = QtGui.QPalette()
    lightPalette.setColor(QtGui.QPalette.ColorRole.Foreground,
                          QtGui.QColor('lime'))
    lightPalette.setColor(QtGui.QPalette.ColorRole.BrightText,
                          QtGui.QColor('lime'))

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self._major_tick_length = 10  # px
        self._minor_tick_length = 5  # px
        self._minor_tick_width = 1  # px

        self.setLineWidth(3)  # using lineWidth as the major tick width
        self.setMidLineWidth(5)  # using midLineWidth as the geometry width
        self.setPalette(self.darkPalette)

    def minimumSizeHint(self) -> QtCore.QSize:
        '''minimum permissible size for this widget'''
        val_rect = self.fontMetrics().boundingRect(
            self._value_formatstr.format(self._value)+'0')
        if self._alignment in (QtCore.Qt.AlignmentFlag.AlignRight, QtCore.Qt.AlignmentFlag.AlignLeft):
            return QtCore.QSize(2*val_rect.width()+self._major_tick_length, 200)
        else:
            return QtCore.QSize(200, 2*val_rect.width()+self._major_tick_length)

    def _create_fixed_geometry(self):
        '''internal function for creating fixed geometry - should be called only on resize or alignement change'''
        # create the central slide/groove
        if self._alignment in (QtCore.Qt.AlignmentFlag.AlignRight, QtCore.Qt.AlignmentFlag.AlignLeft):
            self._slide_line = [
                QtCore.QPoint(self.width()//2, self.rect().top()),
                QtCore.QPoint(self.width()//2, self.rect().bottom()),
            ]
        else:
            self._slide_line = [
                QtCore.QPoint(self.rect().left(), self.height()//2),
                QtCore.QPoint(self.rect().right(), self.height()//2),
            ]

        # the lign which indicates the current value
        # requires a special case for each alignment
        if self._alignment == QtCore.Qt.AlignmentFlag.AlignLeft:
            self._indicator = [
                self.rect().center() + QtCore.QPoint(+1, 0),  # avoid weird rounding errors
                QtCore.QPoint(self.rect().right(),
                              self.rect().center().y())
            ]
        elif self._alignment == QtCore.Qt.AlignmentFlag.AlignRight:
            self._indicator = [
                self.rect().center() + QtCore.QPoint(-1, 0),  # avoid weird rounding errors
                QtCore.QPoint(self.rect().left(),
                              self.rect().center().y())
            ]
        elif self._alignment == QtCore.Qt.AlignmentFlag.AlignTop:
            self._indicator = [
                self.rect().center() + QtCore.QPoint(0, +1),  # avoid weird rounding errors
                QtCore.QPoint(self.rect().center().x(),
                              self.rect().bottom())
            ]
        elif self._alignment == QtCore.Qt.AlignmentFlag.AlignBottom:
            self._indicator = [
                self.rect().center() + QtCore.QPoint(0, -1),  # avoid weird rounding errors
                QtCore.QPoint(self.rect().center().x(),
                              self.rect().top())
            ]

    def _create_alpha_gradient(self,
                               color: typing.Union[QtCore.Qt.GlobalColor, QtGui.QColor],
                               rotated: bool = False) -> QtGui.QLinearGradient:
        '''internal function for creating the gradient map used to draw the widget'''
        if self._alignment in (QtCore.Qt.AlignmentFlag.AlignRight, QtCore.Qt.AlignmentFlag.AlignLeft):
            if rotated:
                gradient = QtGui.QLinearGradient(0, 0, self.height(), 0)
            else:  # normal
                gradient = QtGui.QLinearGradient(0, 0, 0, self.height())
        else:
            if rotated:
                gradient = QtGui.QLinearGradient(0, 0, 0, self.width())
            else:
                gradient = QtGui.QLinearGradient(0., 0, self.width(), 0)

        gradient.setColorAt(0.01,
                            QtCore.Qt.GlobalColor.transparent)
        gradient.setColorAt(.3,
                            color)
        gradient.setColorAt(.7,
                            color)
        gradient.setColorAt(0.99,
                            QtCore.Qt.GlobalColor.transparent)
        return gradient

    def setAlignment(self, alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignLeft):
        '''Set the alignment of the widget. Only `right`, `left`, `top` and `bottom` are allowed.'''
        super().setAlignment(alignment)
        self._create_fixed_geometry()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        self._create_fixed_geometry()
        a0.accept()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        '''draws the widget'''
        # super().paintEvent(a0) #we don't paint the QFrame rect !

        text = self._create_alpha_gradient(
            self.palette().color(QtGui.QPalette.ColorRole.BrightText))
        line = self._create_alpha_gradient(
            self.palette().color(QtGui.QPalette.ColorRole.Foreground))

        # create the painter
        with QtGui.QPainter(self) as p:
            p: QtGui.QPainter  # for typehinting
            p.setPen(QtGui.QPen(line, self.midLineWidth()))

            # draw the fixed geometry
            p.drawLine(*self._slide_line)
            p.drawLine(*self._indicator)

            # get the value text and its metrics
            value_text = self._value_formatstr.format(self._value)
            value_rect = self.fontMetrics().tightBoundingRect(value_text)
            # the point at which the value will be drawn
            if self._alignment == QtCore.Qt.AlignmentFlag.AlignLeft:
                value_anchor = self.rect().center() + \
                    QtCore.QPoint(self.midLineWidth(),
                                  -self.midLineWidth())
            elif self._alignment == QtCore.Qt.AlignmentFlag.AlignRight:
                value_anchor = self.rect().center() + \
                    QtCore.QPoint(-self.midLineWidth() - value_rect.width(),
                                  -self.midLineWidth())
            elif self._alignment == QtCore.Qt.AlignmentFlag.AlignTop:
                value_anchor = self.rect().center() + \
                    QtCore.QPoint(self.midLineWidth(),
                                  self.midLineWidth()+value_rect.height())
            elif self._alignment == QtCore.Qt.AlignmentFlag.AlignBottom:
                value_anchor = self.rect().center() + \
                    QtCore.QPoint(self.midLineWidth(),
                                  -self.midLineWidth())
            # draw the value text
            p.setPen(QtGui.QPen(text, self.lineWidth()))
            p.drawText(value_anchor, value_text)

            # draw the ticks
            p.setPen(QtGui.QPen(line, self.lineWidth()))
            major, minor = self._generate_ticks()
            if self._alignment == QtCore.Qt.AlignmentFlag.AlignLeft:
                mid = self.rect().center().x() - self.midLineWidth()//2-1
                for _, position in major:
                    p.drawLine(mid, position*self.height(),
                               mid-self._major_tick_length, position*self.height())
                p.setPen(QtGui.QPen(text, self.lineWidth()))
                for label, position in major:
                    rect = self.fontMetrics().tightBoundingRect(label)
                    p.drawText(mid-7-self._major_tick_length-rect.width(),
                               position*self.height() + rect.height()//2,
                               label)
                p.setPen(QtGui.QPen(line, self._minor_tick_width))
                for position in minor:
                    p.drawLine(mid, position*self.height(),
                               mid-self._minor_tick_length, position*self.height())
            elif self._alignment == QtCore.Qt.AlignmentFlag.AlignRight:
                mid = self.rect().center().x() + self.midLineWidth()//2+1
                for label, position in major:
                    p.drawLine(mid, position*self.height(),
                               mid+self._major_tick_length, position*self.height())
                p.setPen(QtGui.QPen(text, self.lineWidth()))
                for label, position in major:
                    rect = self.fontMetrics().tightBoundingRect(label)
                    p.drawText(mid+5+self._major_tick_length,
                               position*self.height() + rect.height()//2,
                               label)
                p.setPen(QtGui.QPen(line, self._minor_tick_width))
                for position in minor:
                    p.drawLine(mid, position*self.height(),
                               mid+self._minor_tick_length, position*self.height())
            elif self._alignment == QtCore.Qt.AlignmentFlag.AlignTop:
                mid = self.rect().center().y() - self.midLineWidth()//2-1
                text_rotated = self._create_alpha_gradient(
                    self.palette().color(QtGui.QPalette.ColorRole.BrightText), True)
                for _, position in major:
                    p.drawLine(position*self.width(), mid,
                               position*self.width(), mid-self._major_tick_length)
                p.save()
                p.setPen(QtGui.QPen(line, self._minor_tick_width))
                for position in minor:
                    p.drawLine(position*self.width(), mid,
                               position*self.width(), mid-self._minor_tick_length)
                p.translate(self.rect().center())
                p.rotate(-90)
                p.translate(-self.rect().center().y(),
                            -self.rect().center().x())
                p.setPen(QtGui.QPen(text_rotated, self.lineWidth()))
                for label, position in major:
                    rect = self.fontMetrics().tightBoundingRect(label)
                    p.drawText(self.rect().center().y()+self.midLineWidth()//2+6+self._major_tick_length,
                               position*self.width()+rect.height()//2,
                               label)
                p.restore()
            elif self._alignment == QtCore.Qt.AlignmentFlag.AlignBottom:
                mid = self.rect().center().y() + self.midLineWidth()//2+1
                text_rotated = self._create_alpha_gradient(
                    self.palette().color(QtGui.QPalette.ColorRole.BrightText), True)
                for _, position in major:
                    p.drawLine(position*self.width(), mid,
                               position*self.width(), mid+self._major_tick_length)
                p.setPen(QtGui.QPen(line, self._minor_tick_width))
                for position in minor:
                    p.drawLine(position*self.width(), mid,
                               position*self.width(), mid+self._minor_tick_length)
                p.save()
                p.translate(self.rect().center())
                p.rotate(-90)
                p.translate(-self.rect().center().y(),
                            -self.rect().center().x())
                p.setPen(QtGui.QPen(text_rotated, self.lineWidth()))
                for label, position in major:
                    rect = self.fontMetrics().tightBoundingRect(label)
                    p.drawText(self.rect().center().y()-self.midLineWidth()//2-8-self._major_tick_length-rect.width(),
                               position*self.width()+rect.height()//2,
                               label)
                p.restore()

        a0.accept()


class TapeTestWidget(QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        testWidget = TapeIndicator(self)
        testWidget.setValue(3, '{:.2f}m')
        testWidget.setTickInterval(.2, '{:.1f}m')

        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical, self)
        slider.valueChanged.connect(lambda v: testWidget.setValue(v/50 + 3))

        group = QtWidgets.QGroupBox("Alignment", self)
        group.setLayout(QtWidgets.QVBoxLayout())
        grp = QtWidgets.QButtonGroup(self)
        for alignement, lbl in [(QtCore.Qt.AlignmentFlag.AlignLeft, "left"),
                                (QtCore.Qt.AlignmentFlag.AlignRight, "right"),
                                (QtCore.Qt.AlignmentFlag.AlignTop, "top"),
                                (QtCore.Qt.AlignmentFlag.AlignBottom, "bot.")]:
            rb = QtWidgets.QRadioButton(lbl, group)
            grp.addButton(rb, alignement)
            group.layout().addWidget(rb)
        grp.button(testWidget.alignment()).setChecked(True)
        grp.idClicked.connect(testWidget.setAlignment)
        group.setMaximumWidth(150)

        inv = QtWidgets.QCheckBox('invert', group)
        inv.clicked.connect(testWidget.setInverted)
        group.layout().addWidget(inv)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(group)
        self.layout().addWidget(slider)
        self.layout().addWidget(testWidget)
