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
import logging
from importlib import import_module, reload

from PyQt5 import QtCore, QtWidgets

from .placeholders import PlaceHolder


class ReloadWidgetAction(QtWidgets.QAction):
    '''
    a menu action to reload the target widgets and create new instances thereof.
    Shortcut : [CTRL + R]

    NOTE : dependencies of the widget must be marked in a special 
    class-variable `__depends__` list in order to be reloaded

    @parameters : 
    * `parent`  :   the parent QtWidget
    * `targets` :   the target widgets to reaload, along with their instantiation arguments
    '''
    reloadFinished = QtCore.pyqtSignal(list)

    def __init__(self, parent: typing.Optional[QtCore.QObject],
                 targets: typing.Dict[QtWidgets.QWidget, typing.Iterator] = {}):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.setText("Reload &Widget")
        self.setShortcut(QtCore.Qt.Modifier.CTRL + QtCore.Qt.Key.Key_R)
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
                f"reload targets must be a dict of widgets and their init args, not {targets.__class__}")
        self._targets = targets

    def addTargets(self,  targets: typing.Union[QtWidgets.QWidget, typing.List[QtWidgets.QWidget]] = []):
        '''add reload targets'''
        if not isinstance(targets, dict):
            raise TypeError(
                f"reload targets must be a dict of widgets and their init args, not {targets.__class__}")
        self._targets = dict(zip(**self._targets, **targets))

    def reload_class(self, target_class: type) -> type:
        '''deep-reload target_class' module and get the new target_class'''
        if target_class.__module__ != '__main__':
            module = reload(import_module(target_class.__module__))
            target_class = getattr(module, target_class.__name__)
        else:
            self.logger.warning(
                f"can't reload {target_class.__name__} from '__main__'")

        # check if the new class has any dependencies and reload these:
        if hasattr(target_class, '__depends__'):
            self.logger.debug(
                f"reloading dependencies of {target_class.__name__}")
            for depend in target_class.__depends__:
                self.reload_class(depend)

            # now we have to reload the module again, to make sure the
            # reloaded dependencies are taken into account
            if target_class.__module__ != '__main__':
                module = reload(import_module(target_class.__module__))
                target_class = getattr(module, target_class.__name__)

        return target_class

    def reloadTargets(self):
        '''reload targets from their modules'''
        self.logger.info("reloading targets")
        reloaded = []
        for target, args in self.targets.items():
            try:  # don't suicide if something is wrong in new code

                # reload module and get the new class
                target_class = self.reload_class(target.__class__)

                # create a new instance of the target class
                reloaded.append(target_class(**args))

                # mark the old target for destruction
                target.deleteLater()

            except Exception as e:
                self.logger.error(f'Failed to reload {target.__class__}')
                self.logger.exception(e)
                reloaded.append(target)  # re-use previous target

        # rebuild dict
        self._targets = dict(zip(reloaded, self._targets.values()))

        # notify subscribers
        self.reloadFinished.emit(reloaded)
        self.logger.info("targets reloaded")


class ReloadStyleSheetAction(QtWidgets.QAction):
    '''
    a menu action to reload the target widget's stylesheet.
    Shortcut : [CTRL + SHIFT + R]

    @parameters : 
    * `parent`  :   the parent QtWidget
    * `target`  :   the target stylesheet to reaload
    '''
    reloadFinished = QtCore.pyqtSignal()

    def __init__(self, parent: typing.Optional[QtCore.QObject],
                 target: typing.Optional[str] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.setText("Reload &QSS")
        self.setShortcut(QtCore.Qt.Modifier.CTRL +
                         QtCore.Qt.Modifier.SHIFT + QtCore.Qt.Key.Key_R)
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
        self.logger.info("reloading stylesheet")

        if self._stylesheet is None:
            self.logger.warning("no stylesheet")
            return

        with open(self._stylesheet, 'r') as file:
            styleSheet = file.read()
        self.parentWidget().setStyleSheet(styleSheet)
        self.reloadFinished.emit()
        self.logger.info("stylesheet reloaded")


class SeparatorAction(QtWidgets.QAction):
    '''a separator for context menus'''

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setSeparator(True)


class ReloadableWidget(QtWidgets.QWidget):
    '''
    a widget which implements the reload action and acts as a wrapper around another widget.
    It can also reload the sylesheet at runtime.
    Shortcut : [CTRL + R] -> reloads widget
    Shortcut : [CTRL + SHIFT + R] -> reloads stylesheet

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
