#!/usr/bin/env python3
'''
A submodule for loading a form from a JSON or YAML file

Author  :   Michael Biselx
Date    :   11.2022
Project :   PyQtTest
'''

__all__ = [
    'FormDisplay',
    'ListDisplay'
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
            w = QtWidgets.QLabel(f"Missing '{e!s}'")
            w.getValue = w.text
            return field_name, w

        # make the input widget according to the field
        if field_type == 'string':
            w = QtWidgets.QLineEdit(self)
            w.setText(str(protofield.get('value', '')))
            w.getValue = w.text

        elif field_type == 'integer':
            w = QtWidgets.QSpinBox(self)
            w.setMinimum(int(protofield.get('minimum', 0)))
            w.setMaximum(int(protofield.get('maximum', 99)))
            w.setValue(int(protofield.get('value', 0)))
            w.getValue = w.value

        elif field_type == 'decimal':
            w = QtWidgets.QDoubleSpinBox(self)
            w.setMinimum(float(protofield.get('minimum', 0)))
            w.setMaximum(float(protofield.get('maximum', 99)))
            w.setValue(float(protofield.get('value', 0)))
            w.setDecimals(int(protofield.get('precision', 2)))
            w.getValue = w.value

        elif field_type == 'date':
            w = QtWidgets.QDateEdit(self)
            w.setCalendarPopup(True)
            w.getValue = lambda: w.date().toString(QtCore.Qt.DateFormat.ISODate)
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
                w.getValue = w.currentText
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

                w.getValue = lambda: [
                    b.text() for b in w.buttonGroup.buttons() if b.isChecked()]
        else:
            logging.error(
                f"No widget has been implemented for type '{field_type}'")
            w = QtWidgets.QLabel(f"'{field_type.title()}' not implemented")
            w.getValue = w.text

        return field_name, w

    def export_callback(self, *, filename: str = None):
        if filename is None:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self)

        formitem_dict = self.toDict()

        if filename.endswith('yaml'):
            dumper = yaml.safe_dump
        elif filename.endswith('json'):
            dumper = json.dump
        else:
            print("dict contents:")
            for item in formitem_dict.items():
                print(*item, sep=' : ')
            raise TypeError(f'Filetype `{filename}` not supported')

        with open(filename, 'w') as file:
            dumper(formitem_dict, file)

    def get_row(self, row: int) -> 'tuple[str, typing.Any]':
        row_label = self.form.itemAt(row, self.form.ItemRole.LabelRole)
        row_field = self.form.itemAt(row, self.form.ItemRole.FieldRole)
        return row_label.widget().text(), row_field.widget().getValue()

    def toDict(self) -> 'dict[str, typing.Any]':
        return dict(self.get_row(row) for row in range(self.form.rowCount()))


class ListItemPicker(QtWidgets.QFrame):
    addItemRequest: QtCore.pyqtSignal
    removeItemRequest: QtCore.pyqtSignal

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._choice = QtWidgets.QComboBox(self)
        self._addItem = QtWidgets.QToolButton(self)
        self._addItem.setText('+')
        self.addItemRequest = self._addItem.clicked
        self._removeItem = QtWidgets.QToolButton(self)
        self._removeItem.setText('-')
        self.removeItemRequest = self._removeItem.clicked

        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().addWidget(self._choice)
        self.layout().addWidget(self._addItem)
        self.layout().addWidget(self._removeItem)
        self.layout().setContentsMargins(*4*[0])

    def setChoices(self, choices: list):
        for choice in choices:
            self._choice.addItem(
                f"{choice['name']} ({choice['type']})", choice)


class ListDisplay(QtWidgets.QFrame):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 form: typing.Optional[str] = None) -> None:
        super().__init__(parent, flags)

        self.form = QtWidgets.QFormLayout(self)
        self.setLayout(self.form)

        if form is not None:
            self.fromFile(form)

    def fromFile(self, filename: str):
        '''read the form structure from a dict'''
        with open(filename) as f:
            if filename.lower().endswith('json'):
                prototype: 'dict[str, dict]' = json.load(f)
            elif filename.lower().endswith(('yaml', 'yml')):
                prototype: 'dict[str, dict]' = yaml.safe_load(f)
        self._fromPrototype(prototype)

    def _fromPrototype(self, prototype: 'dict[str, typing.Any]', *, layout=None) -> QtWidgets.QWidget:
        if layout is None:
            layout = self.form

        name = prototype.get('name', '')
        dtype = str(prototype['type']).lower()

        if dtype == 'list':
            w = self._fromPrototype(prototype.get('value', {'type': 'group'}),
                                    layout=layout)
            w.setTitle(prototype.get('name', w.title()))
            lip = ListItemPicker(w)
            lip.setChoices(prototype['choices'])
            w.layout().addRow(lip)
            # np = QtWidgets.QLineEdit(w)
            # w.layout().addRow(np, lip)

            def removeItem():
                if w.layout().rowCount() > 1:
                    rr = w.layout().takeRow(w.layout().rowCount()-2)
                    rr.labelItem.widget().deleteLater()
                    rr.fieldItem.widget().deleteLater()
            lip.removeItemRequest.connect(removeItem)

            def insertNewItem():
                rr = w.layout().takeRow(w.layout().rowCount()-1)
                self._fromPrototype(lip._choice.currentData(),
                                    layout=w.layout())
                w.layout().addRow(rr.fieldItem.widget())
                # w.layout().addRow(rr.labelItem.widget(),
                #                   rr.fieldItem.widget())
            lip.addItemRequest.connect(insertNewItem)

        elif dtype == 'group':
            w = QtWidgets.QGroupBox()
            w.setTitle(prototype.get('name', ''))
            w.setLayout(QtWidgets.QFormLayout(w))
            for key, value in prototype.items():
                if key in ('name', 'type'):
                    continue
                self._fromPrototype(value, layout=w.layout())
            layout.addRow(w)

            # make the input widget according to the field
        else:
            l, w = self._fieldFromPrototype(prototype)
            layout.addRow(l, w)

        return w

    def _fieldFromPrototype(self, prototype: dict) -> 'tuple[str, QtWidgets.QWidget]':
        name = prototype.get('name', '')
        dtype = str(prototype['type']).lower()

        if dtype == 'string':
            w = QtWidgets.QLineEdit()
            w.setText(str(prototype.get('value', '')))

        elif dtype == 'integer':
            w = QtWidgets.QSpinBox()
            w.setMinimum(int(prototype.get('minimum', 0)))
            w.setMaximum(int(prototype.get('maximum', 99)))
            w.setValue(int(prototype.get('value', 0)))

        else:
            raise NotImplementedError(f"{dtype}")

        return name, w
