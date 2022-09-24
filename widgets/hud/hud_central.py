#!/usr/bin/env python3
'''
A module containing widgets for containing the entire HUD

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

import typing

from PyQt5 import QtCore, QtGui, QtWidgets

from .hud_camera import CameraStream


class CameraTabs(QtWidgets.QTabWidget):
    '''
    the tabs for containing the different camera views
    '''

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._tab_indices: 'dict[int, int]' = {}

    def addTab(self, sysid: int, label: str = None):
        '''add a tab by SysID'''
        if label is None:
            label = f"Camera {sysid}"

        idx = super().addTab(CameraStream(parent=self, sysid=sysid),
                             label)
        self._tab_indices[sysid] = idx
