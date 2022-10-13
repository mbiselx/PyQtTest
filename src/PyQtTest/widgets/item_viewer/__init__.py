#!/usr/bin/env python3
'''
An item viewr

Author  :   Michael Biselx
Date    :   10.2022
Project :   PyQtTest
'''

import os
import typing

from PyQt5 import QtCore, QtGui, QtWidgets

from ...resources import image_folder


class ItemViewer(QtWidgets.QSplitter):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent)

        self.dirview = DirView(self)
        self.imgview = ImgView(self)

        self.dirview.selected_file.connect(print)

        self.addWidget(self.dirview)
        self.addWidget(self.imgview)

        self.dirview.activated.connect(self.imgview.setItem)


class DirView(QtWidgets.QTreeView):
    Roles = QtWidgets.QFileSystemModel.Roles
    selected_file = QtCore.pyqtSignal(str)

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        model = QtWidgets.QFileSystemModel(self)
        model.setIconProvider(QtWidgets.QFileIconProvider())
        idx = model.setRootPath(image_folder)
        self.setModel(model)
        self.setRootIndex(idx)

        self.setAnimated(False)
        self.setIndentation(20)
        self.setSortingEnabled(True)


class ImgView(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.img = QtWidgets.QLabel(self)
        self.img.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                               QtWidgets.QSizePolicy.Policy.Expanding)
        appreciation = QtWidgets.QGroupBox('Appreciation')
        appreciation.setLayout(QtWidgets.QHBoxLayout())
        appreciation.grp = QtWidgets.QButtonGroup()
        for idx, val in enumerate(['ugly', 'ok', 'cute']):
            rb = QtWidgets.QRadioButton(val)
            appreciation.grp.addButton(rb, idx+1)
            appreciation.layout().addWidget(rb)
        appreciation.grp.idClicked.connect(print)

        self.notes = QtWidgets.QPlainTextEdit(self)
        notes = QtWidgets.QGroupBox('Notes')
        notes.setLayout(QtWidgets.QVBoxLayout())
        notes.layout().addWidget(self.notes)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.img)
        self.layout().addWidget(appreciation)
        self.layout().addWidget(notes)

    def setItem(self, item: QtCore.QModelIndex):
        self.item = item
        path: str = item.data(DirView.Roles.FilePathRole)
        if path.lower().endswith(('.png', '.jpg', '.webp')):
            img = QtGui.QImage(path)
            if img.height() > img.width():
                img = img.scaledToHeight(500)
            else:
                img = img.scaledToWidth(500)
            self.img.setPixmap(QtGui.QPixmap.fromImage(img))

    def updateAppreciation(self, val: int):
        print(val)
