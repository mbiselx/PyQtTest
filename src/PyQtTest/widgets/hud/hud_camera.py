#!/usr/bin/env python3
'''
A module containing widgets for displaying camera images

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

import typing

from PyQt5 import QtCore, QtGui, QtWidgets


class CameraStream(QtWidgets.QLabel):
    '''
    a widget for displaying camera images
    '''
    sysid = None

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 sysid: typing.Optional[int] = None) -> None:
        super().__init__(parent)
        self.setText("Waiting for camera stream ...")
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                           QtWidgets.QSizePolicy.Policy.MinimumExpanding)

        if sysid is not None:
            self.setTargetSystem(sysid)

    def setTargetSystem(self, sysid: typing.Union[int, 'list[int]']):
        '''set the target system for the camera'''
        if isinstance(sysid, int):
            self.sysid = [sysid]
        elif hasattr(sysid, '__inter__'):
            self.sysid = [s for s in sysid]
        self.setText(f"showing stream for camera {sysid}.")

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(960, 640)
