#!/usr/bin/env python3
'''
A submodule for segmenting a jpg image

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'segment_image',
    'color_image_by_segments',
    'SegmentImage',
    'ClickableSegmentImage'
]

import json
import typing
import logging

from PyQt5 import QtCore, QtGui, QtWidgets


def widgetFactory(item_type: str) -> QtWidgets.QWidget:
    if item_type == None:
        w = QtWidgets.QLabel('No item type set')
        p = w.palette()
        p.setColor(p.ColorRole.WindowText, QtCore.Qt.GlobalColor.red)
        w.setPalette(p)
        return w
    elif item_type == 'str':
        return QtWidgets.QLineEdit()
    elif item_type == 'int':
        return QtWidgets.QSpinBox()
    else:
        logging.exception(NotImplementedError(
            f"No widget has been implemented for type {item_type}"))
        w = QtWidgets.QLabel(f'No widget for item type {item_type}')
        p = w.palette()
        p.setColor(p.ColorRole.WindowText, QtCore.Qt.GlobalColor.red)
        w.setPalette(p)
        return w


class FormDisplay(QtWidgets.QFrame):
    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 form: typing.Optional[str] = None) -> None:
        super().__init__(parent, flags)

        self.setLayout(QtWidgets.QFormLayout(self))
        if form is not None:
            self.fromJSON(form)

    def fromJSON(self, filename: str):
        with open(filename) as f:
            form_dict: 'dict[str, dict]' = json.load(f)

        widget = self.parseJSONDict(form_dict)

    def parseJSONDict(self, form_dict: 'dict[str, dict]'):
        for name, item in form_dict.items():
            try:
                item_type = item['type']
            except KeyError:
                logging.exception(KeyError(f"No type specified for {name}"))
                item_type = None

            w = widgetFactory(item_type)
            self.layout().addRow(name, w)
