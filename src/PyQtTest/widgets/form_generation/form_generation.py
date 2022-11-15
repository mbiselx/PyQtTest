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


class FormDisplay(QtWidgets.QFrame):
    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 form: typing.Optional[str] = None) -> None:
        super().__init__(parent, flags)

        self.form = QtWidgets.QFormLayout()

        export_button = QtWidgets.QPushButton('export', self)
        export_button.setIcon(self.style().standardIcon(
            self.style().StandardPixmap.SP_ToolBarHorizontalExtensionButton))
        export_button.clicked.connect(self.export_callback)

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addLayout(self.form)
        self.layout().addWidget(export_button)

        if form is not None:
            self.fromJSON(form)

    def fromJSON(self, filename: str):
        '''read the form structure from a dict'''
        with open(filename) as f:
            form_dict: 'dict[str, dict]' = json.load(f)

        self.parseJSONDict(form_dict)

    def parseJSONDict(self, form_dict: 'dict[str, dict]'):
        for name, item in form_dict.items():
            # get the type of the information field
            try:
                item_type = str(item['type']).lower()
            except KeyError:
                logging.error(f"No type specified for {name}")
                item_type = None

            # instantiate the widget
            if item_type == None:
                w = QtWidgets.QLabel('No item type set')
                p = w.palette()
                p.setColor(p.ColorRole.WindowText, QtCore.Qt.GlobalColor.red)
                w.setPalette(p)

            elif item_type == 'text':
                w = QtWidgets.QLineEdit(self)
                if 'default' in item:
                    w.setText(str(item['default']))

            elif item_type == 'integer':
                w = QtWidgets.QSpinBox(self)
                if 'minimum' in item:
                    w.setMinimum(item['minimum'])
                if 'maximum' in item:
                    w.setMaximum(item['maximum'])
                if 'default' in item:
                    w.setValue(int(item['default']))

            elif item_type == 'decimal':
                w = QtWidgets.QDoubleSpinBox(self)
                if 'minimum' in item:
                    w.setMinimum(item['minimum'])
                if 'maximum' in item:
                    w.setMaximum(item['maximum'])
                if 'precision' in item:
                    w.setDecimals(int(item['precision']))
                if 'default' in item:
                    w.setValue(float(item['default']))

            elif item_type == 'date':
                w = QtWidgets.QDateEdit(self)
                w.setCalendarPopup(True)
                if 'default' in item:
                    if str(item['default']).lower() == 'today':
                        w.setDate(QtCore.QDate.currentDate())
                    else:
                        try:
                            w.setDate(QtCore.QDate.fromString(
                                str(item['default']),
                                QtCore.Qt.DateFormat.ISODate))
                        except Exception as e:
                            logging.error(
                                f"could not parse {item['default']} as a date")
                            logging.exception(e)

            elif item_type == 'choice':
                w = QtWidgets.QComboBox(self)
                if 'choices' in item:
                    w.addItems(item['choices'])
                else:
                    logging.error(f"no choices given for item '{name}'")
                if 'default' in item:
                    for idx in range(w.count()):
                        if w.itemText(idx) == item['default']:
                            w.setCurrentIndex(idx)
                            break
                    else:
                        logging.warning(
                            f"default choice for item '{name}' could not be found")
            else:
                logging.error(
                    f"No widget has been implemented for type '{item_type}'")
                w = QtWidgets.QLabel(f"No widget for item type '{item_type}'")
                p = w.palette()
                p.setColor(p.ColorRole.WindowText, QtCore.Qt.GlobalColor.red)
                w.setPalette(p)

            self.form.addRow(name, w)

    def export_callback(self, filename: str = None):
        formitem_dict = self.toDict()

    def toDict(self) -> 'dict[str, typing.Any]':
        for row in range(self.form.rowCount()):
            row_label = self.form.itemAt(row, self.form.ItemRole.LabelRole)
            row_field = self.form.itemAt(row, self.form.ItemRole.FieldRole)
            print(row_label.widget().text(), row_field.widget())
