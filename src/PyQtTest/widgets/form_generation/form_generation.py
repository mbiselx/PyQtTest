#!/usr/bin/env python3
'''
A submodule for loading a form from a JSON or YAML file

Author  :   Michael Biselx
Date    :   11.2022
Project :   PyQtTest
'''

__all__ = [
    'FormDisplay'
]

import json
import yaml
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
            self.fromFile(form)

    def fromFile(self, filename: str):
        '''read the form structure from a dict'''
        with open(filename) as f:
            if filename.lower().endswith('json'):
                prototype: 'dict[str, dict]' = json.load(f)
            elif filename.lower().endswith(('yaml', 'yml')):
                prototype: 'dict[str, dict]' = yaml.safe_load(f)
        self.formFromPrototype(prototype)

    def formFromPrototype(self, prototype: 'dict[str, typing.Any]'):
        for key, value in prototype.items():
            if key.lower() == 'fields':
                for protofield in value:
                    self.form.addRow(*self.formitemFromProtofield(protofield))

    def formitemFromProtofield(self, protofield: 'dict[str, dict]'):
        # get the obligatory fields :
        try:
            field_name = 'ERROR'
            field_name = str(protofield.get('name'))
            field_type = str(protofield.get('type')).lower()
        except KeyError as e:
            logging.error(f"Failed to parse field. Missing key '{e!s}'")
            return field_name, QtWidgets.QLabel(f"Missing '{e!s}'")

        # make the input widget according to the field
        if field_type == 'string':
            w = QtWidgets.QLineEdit(self)
            w.setText(str(protofield.get('value', '')))

        elif field_type == 'integer':
            w = QtWidgets.QSpinBox(self)
            w.setMinimum(int(protofield.get('minimum', 0)))
            w.setMaximum(int(protofield.get('maximum', 99)))
            w.setValue(int(protofield.get('value', 0)))

        elif field_type == 'decimal':
            w = QtWidgets.QDoubleSpinBox(self)
            w.setMinimum(float(protofield.get('minimum', 0)))
            w.setMaximum(float(protofield.get('maximum', 99)))
            w.setValue(float(protofield.get('value', 0)))
            w.setDecimals(int(protofield.get('precision', 2)))

        elif field_type == 'date':
            w = QtWidgets.QDateEdit(self)
            w.setCalendarPopup(True)
            value = str(protofield.get('value', 'today'))

            if value.lower() != 'today':
                try:
                    w.setDate(QtCore.QDate.fromString(
                        value,
                        QtCore.Qt.DateFormat.ISODate))
                except Exception as e:
                    logging.error(
                        f"could not parse {value} as a date")
                    logging.exception(e)
            else:
                w.setDate(QtCore.QDate.currentDate())

        elif field_type == 'choice':
            if protofield.get('exclusive', True):
                w = QtWidgets.QComboBox(self)
                w.setEditable(bool(protofield.get('open', False)))
                w.addItems(map(str, protofield.get('choices', [])))
                if 'value' in protofield:
                    w.setCurrentText(str(protofield.get('value')))
            else:
                w = QtWidgets.QWidget(self)
                w.setLayout(QtWidgets.QHBoxLayout(w))
                w.buttonGroup = QtWidgets.QButtonGroup(w)
                w.buttonGroup.setExclusive(False)
                values = protofield.get('value', [])
                if not isinstance(values, list):
                    values = [values]
                values = map(str, values)
                for choice in map(str, protofield.get('choices', [])):
                    cb = QtWidgets.QCheckBox(choice)
                    w.layout().addWidget(cb)
                    w.buttonGroup.addButton(cb)
                    if choice in values:
                        cb.setChecked(True)

        else:
            logging.error(
                f"No widget has been implemented for type '{field_type}'")
            w = QtWidgets.QLabel(f"'{field_type.title()}' not implemented")

        return field_name, w

    def export_callback(self, filename: str = None):
        formitem_dict = self.toDict()

    def toDict(self) -> 'dict[str, typing.Any]':
        for row in range(self.form.rowCount()):
            row_label = self.form.itemAt(row, self.form.ItemRole.LabelRole)
            row_field = self.form.itemAt(row, self.form.ItemRole.FieldRole)
            print(row_label.widget().text(), row_field.widget())
