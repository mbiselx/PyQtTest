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


class ReloadAction(QtWidgets.QAction):
    '''reload the target widgets and create new instances thereof'''
    reloadFinished = QtCore.pyqtSignal(list)

    def __init__(self, parent: typing.Optional[QtCore.QObject],
                 targets: typing.Dict[QtWidgets.QWidget, typing.Iterator] = {}):
        super().__init__(parent)

        self.setText("&Reload")
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


class SeparatorAction(QtWidgets.QAction):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setSeparator(True)


class ReloadableWidget(QtWidgets.QWidget):
    '''a widget which implements the reload action and acts as a wrapper around another widget'''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 widget: typing.Optional[QtWidgets.QWidget] = None,
                 **args) -> None:
        super().__init__(parent, flags)

        if widget is None:
            widget = PlaceHolder(**args)
        else:
            widget = widget(**args)

        self.reload = ReloadAction(parent=self, targets={widget: args})
        self.reload.reloadFinished.connect(self.doLayout)
        self.addActions([self.reload,
                         SeparatorAction(self)])
        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(*4*[0])
        self.doLayout([widget])

    def doLayout(self, widgets: typing.List[QtWidgets.QWidget]):
        '''lay out widgets'''
        for widget in widgets:
            self.layout().addWidget(widget)
            self.addActions(widget.actions())
            widget.setContextMenuPolicy(
                QtCore.Qt.ContextMenuPolicy.NoContextMenu)
