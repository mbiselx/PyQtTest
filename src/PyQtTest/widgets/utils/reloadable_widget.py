#!/usr/bin/env python3
'''
A reloadable widget for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'ReloadAction',
    'ReloadableWidget'
]

import typing
import traceback
from importlib import import_module, reload

from PyQt5 import QtCore, QtWidgets

from .placeholders import PlaceHolder


class ReloadWidgetAction(QtWidgets.QAction):
    '''
    a menu action to reload the target widgets and create new instances thereof.
    Shortcut : [CTRL + W]

    ! NOTE : this only relaods the file the widget is defined in, not all of its dependencies 

    @parameters : 
    * `parent`  :   the parent QtWidget
    * `targets` :   the target widgets to reaload, along with their instantiation arguments
    '''
    reloadFinished = QtCore.pyqtSignal(list)

    def __init__(self, parent: typing.Optional[QtCore.QObject],
                 targets: typing.Dict[QtWidgets.QWidget, typing.Iterator] = {}):
        super().__init__(parent)

        self.setText("Reload &Widget")
        self.setShortcut(QtCore.Qt.Modifier.CTRL + QtCore.Qt.Key.Key_W)
        tmp = QtWidgets.QWidget()
        self.setIcon(tmp.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        tmp.deleteLater()

        self.triggered.connect(self.reloadTargets)

        self.setTargets(targets)

    @property
    def targets(self) -> typing.Dict[QtWidgets.QWidget, typing.Iterator]:
        '''reload targets'''
        return self._targets

    def setTargets(self, targets: typing.Dict[QtWidgets.QWidget, typing.Iterator] = []):
        '''set reload targets'''
        if not isinstance(targets, dict):
            raise TypeError(
                f"reload targets must be a a dict of widgets and their init args, not {targets.__class__}")
        self._targets = targets

    def addTargets(self,  targets: typing.Union[QtWidgets.QWidget, typing.List[QtWidgets.QWidget]] = []):
        '''add reload targets'''
        if not isinstance(targets, dict):
            raise TypeError(
                f"reload targets must be a a dict of widgets and their init args, not {targets.__class__}")
        self._targets = dict(zip(**self._targets, **targets))

    def reloadTargets(self):
        '''reload targets from their modules'''
        reloaded = []
        for target, args in self.targets.items():
            try:  # don't suicide if something is wrong in new code
                # reload module and get an instance of the new class
                module = reload(import_module(target.__module__))
                reloaded.append(
                    getattr(module, target.__class__.__name__)(**args))

                # mark the old target for destruction
                target.deleteLater()

            except Exception:
                traceback.print_exc()  # notify user about what happened
                reloaded.append(target)  # re-use previous target

        # rebuild dict
        self._targets = dict(zip(reloaded, self._targets.values()))

        # notify subscribers
        self.reloadFinished.emit(reloaded)


class ReloadStyleSheetAction(QtWidgets.QAction):
    '''
    a menu action to reload the target widget's stylesheet.
    Shortcut : [CTRL + Q]

    @parameters : 
    * `parent`  :   the parent QtWidget
    * `target`  :   the target stylesheet to reaload
    '''
    reloadFinished = QtCore.pyqtSignal()

    def __init__(self, parent: typing.Optional[QtCore.QObject],
                 target: typing.Optional[str] = None):
        super().__init__(parent)

        self.setText("Reload &QSS")
        self.setShortcut(QtCore.Qt.Modifier.CTRL + QtCore.Qt.Key.Key_Q)
        tmp = QtWidgets.QWidget()
        self.setIcon(tmp.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        tmp.deleteLater()

        self.triggered.connect(self.loadStyleSheetFile)

        self.setStyleSheetFile(target)

    def setStyleSheetFile(self, styleSheetFile: str) -> None:
        self._stylesheet = styleSheetFile
        self.loadStyleSheetFile()

    def loadStyleSheetFile(self):
        if self._stylesheet is not None:
            with open(self._stylesheet, 'r') as file:
                styleSheet = file.read()
            self.parentWidget().setStyleSheet(styleSheet)
            self.reloadFinished.emit()


class SeparatorAction(QtWidgets.QAction):
    '''a separator for context menus'''

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setSeparator(True)


class ReloadableWidget(QtWidgets.QWidget):
    '''
    a widget which implements the reload action and acts as a wrapper around another widget.
    It can also reload the sylesheet at runtime.
    Shortcut : [CTRL + W] -> reloads widget
    Shortcut : [CTRL + Q] -> reloads stylesheet

    @parameters : 
    * `parent`      : (optional) the parent QtWidget
    * `flags`       : (optional) the window flags for the instantiation of the widgets
                        if no widget is specified, fall back on placeholder widget
    * `stylesheet`  : (optional) the stylesheet to reload (if any)
    * `widget`      : (optional) the target widget to reaload, followed by its instantiation arguments (with keywords)
    '''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 stylesheet: typing.Optional[str] = None,
                 widget: typing.Optional[typing.Type[QtWidgets.QWidget]] = None,
                 **args) -> None:
        super().__init__(parent, flags)

        widget = widget(**args) if widget is not None else PlaceHolder(**args)

        self.reloadWidget = ReloadWidgetAction(parent=self,
                                               targets={widget: args})
        self.reloadWidget.reloadFinished.connect(self.doLayout)

        self.reloadQSS = ReloadStyleSheetAction(parent=self,
                                                target=stylesheet)

        self.addActions([self.reloadWidget,
                         self.reloadQSS,
                         SeparatorAction(self)])
        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(*4*[0])
        self.doLayout([widget])

        self.setWindowTitle(widget.__class__.__name__)
        self.setWindowIcon(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))

    def doLayout(self, widgets: typing.List[QtWidgets.QWidget]):
        '''lay out widgets'''
        for widget in widgets:
            self.layout().addWidget(widget)
            self.addActions(widget.actions())
            widget.setContextMenuPolicy(
                QtCore.Qt.ContextMenuPolicy.NoContextMenu)
