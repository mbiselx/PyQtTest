#!/usr/bin/env python3
'''
A set of utility widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

import serial
import typing
import collections

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQtTest.guifw.gui_elements import MenuBar
from .placeholders import PlaceHolder, DockPlaceHolder, GraphicPlaceholder, GraphicDockPlaceholder


class SerialSelectWidget(QtWidgets.QComboBox):
    '''
    A widget for selecting the serial port to use

    parameters : 
    * parent    :   (optional) the parent QtWidget
    '''
    default_choices = ['udp 0.0.0.14550', 'tcp 0.0.0.0.1', '...']

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.rescanForSerials()
        self.activated.connect(self.selectPort)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                           QtWidgets.QSizePolicy.Policy.Maximum)

    def showPopup(self) -> None:
        '''internal callback : on opening the widget, the ports are rescanned'''
        self.rescanForSerials()
        return super().showPopup()

    def rescanForSerials(self):
        '''rescan available ports'''
        self.clear()
        self.addItems(self.default_choices[0:2])
        for i in range(5, 7):
            try:
                port = f"COM{i}"
                ser = serial.Serial(port=port, timeout=.001)
                self.addItem(port, ser)
            except serial.SerialException:
                pass
        self.addItem(self.default_choices[-1])

    def selectPort(self):
        '''internal callback on port selection by user'''
        print(self.currentText())
        if self.currentText() == '...':
            fd = QtWidgets.QFileDialog(
                parent=self, caption='Open File', filter='*.*')
            fd.show()


class BaudSelectWidget(QtWidgets.QComboBox):
    '''
    A widget for selecting the baudrate of the serial port

    parameters : 
    * parent    :   (optional) the parent QtWidget
    '''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        for idx, baudrate in enumerate(serial.Serial.BAUDRATES):
            self.addItem(str(baudrate), baudrate)
            if baudrate == 115200:
                self.setCurrentIndex(idx)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                           QtWidgets.QSizePolicy.Policy.Maximum)


class ClockWidget(QtWidgets.QLabel):
    '''
    A widget for displaying the current time

    parameters : 
    * parent    :   (optional) the parent QtWidget
    * flags     :   (optional) the windwoflags for the instantiation of the widgets
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(10, 0, 10, 0)

        self.startTimer(200)

    def timerEvent(self, event: QtCore.QTimerEvent) -> None:
        '''internal callback to update the display'''
        now = QtCore.QTime.currentTime()
        self.setText(now.toString('hh:mm:ss'))


class WidgetMaker(MenuBar):
    '''
    A widget factory for quick prototyping

    parameters : 
    * parent    :   (optional) the parent QtWidget
    * flags     :   (optional) the windwoflags for the instantiation of the widgets
    * widgetDict :  (optional) a dictionary of widgets to instantiate
    '''
    widgetDict: 'dict[str, type]' = collections.OrderedDict([
        ("PlaceHolder", PlaceHolder),
        ("DockPlaceHolder", DockPlaceHolder),
        ("GraphicPlaceHolder", GraphicPlaceholder),
        ("GraphicDockPlaceholder", GraphicDockPlaceholder)
    ])

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 widgetDict: typing.Optional[typing.Dict[str, typing.Type[QtWidgets.QWidget]]] = None) -> None:
        super().__init__(parent, flags)

        if widgetDict is not None:
            self.widgetDict = widgetDict

        self.combo = QtWidgets.QComboBox(self)
        for lbl, w in self.widgetDict.items():
            self.combo.addItem(lbl, userData=w)

        makeBtn = QtWidgets.QToolButton(self)
        makeBtn.setText('+')
        makeBtn.clicked.connect(self.makeWidget)
        makeBtn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,
                              QtWidgets.QSizePolicy.Policy.Expanding)

        self.add([self.combo, makeBtn])

    def currentWidget(self) -> 'type[QtWidgets.QWidget]':
        '''get the type of the current widget'''
        return self.combo.currentData(QtCore.Qt.ItemDataRole.UserRole)

    def makeWidget(self):
        '''internal callback to create a widget'''
        w_type = self.currentWidget()
        w = w_type(parent=self.window(), flags=QtCore.Qt.WindowType.Window)
        w.show()


class StandardMenuBar(MenuBar):
    '''
    a standard menu bar for quick prototyping
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.add([
            SerialSelectWidget(self),
            BaudSelectWidget(self),
            QtWidgets.QSpacerItem(0, 0,
                                  QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                  QtWidgets.QSizePolicy.Policy.Maximum),
            WidgetMaker(self),
            QtWidgets.QSpacerItem(0, 0,
                                  QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                  QtWidgets.QSizePolicy.Policy.Maximum),
            ClockWidget(self),
        ])
