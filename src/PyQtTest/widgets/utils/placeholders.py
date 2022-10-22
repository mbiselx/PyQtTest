#!/usr/bin/env python3
'''
A set of placeholder widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'PlaceHolder',
    'DockPlaceHolder',
    'GraphicPlaceholder',
    'GraphicDockPlaceholder',
    'ComplexPlaceholder'
]

import typing
import numpy as np
import numpy.random

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotItem, PlotWidget


class PlaceHolder(QtWidgets.QLabel):
    '''
    A simple placeholder widget
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("PlaceHolder")
        self.setText("This is a PlaceHolder")
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(350, 50)


class DockPlaceHolder(QtWidgets.QDockWidget):
    '''
    A dockable placeholder widget
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("DockPlaceHolder")
        self.setWidget(QtWidgets.QLabel(
            parent=self.parentWidget(),
            text="This is a dockable PlaceHolder"))
        self.setContentsMargins(0, 0, 0, 0)

        self.setAllowedAreas(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setMinimumSize(350, 50)

        if hasattr(self.parentWidget(), 'addDockWidget'):
            self.parentWidget().addDockWidget(
                QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self)
        else:
            self.setFloating(True)
            self.show()


class RandomGraphicPlotter(PlotWidget):
    '''
    a widget which plots random values
    '''

    def __init__(self,
                 parent=None,
                 data_range=[-100, -1],
                 background='default',
                 plotItem: 'PlotItem|None' = None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)

        self._data_range = data_range
        if self.plotItem is None:
            self.plotItem = PlotItem()
        self._plot = self.plotItem.plot()
        self._data = []
        self._ts = []
        self._ts0 = QtCore.QTime.currentTime().msecsSinceStartOfDay()

        self.startTimer(200)

    def timerEvent(self, event: QtCore.QTimerEvent) -> None:
        now = QtCore.QTime.currentTime().msecsSinceStartOfDay() - self._ts0
        self._ts.append(now)
        self._data.append(numpy.random.random(1)[0])
        self._plot.setData(x=np.array(self._ts[self._data_range[0]:self._data_range[1]]),
                           y=np.array(self._data[self._data_range[0]:self._data_range[1]]))

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 500)


class GraphicPlaceholder(QtWidgets.QWidget):
    '''
    a free-standing widget for plotting random values
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 data_range: typing.List[int] = [-100, -1],
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("GraphicPlaceholder")

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(RandomGraphicPlotter(parent=self, data_range=data_range))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)


class GraphicDockPlaceholder(QtWidgets.QDockWidget):
    '''
    a dockable widget for plotting random values
    '''

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 data_range: typing.List[int] = [-100, -1],
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 *args, **kwargs) -> None:
        super().__init__(parent, flags)
        self.setWindowTitle("GraphicDockPlaceholder")
        self.setWidget(RandomGraphicPlotter(parent=self,
                                            data_range=data_range))
        self.setContentsMargins(0, 0, 0, 0)

        self.setAllowedAreas(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setMinimumSize(350, 50)

        if hasattr(self.parentWidget(), 'addDockWidget'):
            self.parentWidget().addDockWidget(
                QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self)
        else:
            self.setFloating(True)
            self.show()


class ComplexPlaceholder(QtWidgets.QWidget):
    ImageDataRole = QtWidgets.QListWidgetItem.ItemType.UserType + 1
    DescriptionRole = QtWidgets.QListWidgetItem.ItemType.UserType + 2

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget):
        super().__init__(parent=parent, flags=flags)

        itemList = self._createList(['kitten', 'puppy', 'calf', 'foal'])
        itemViewer = self._createItemViewer()
        itemEditor = self._createItemEditor()

        itemList.itemActivated.connect(itemViewer.setActiveItem)
        itemList.itemActivated.connect(itemEditor.setActiveItem)
        itemEditor.itemEdited.connect(itemViewer.updateActiveItem)
        itemEditor.mustacheSelected.connect(itemViewer.setMustache)
        itemEditor.mustacheScale.connect(itemViewer.setMustacheScale)
        itemEditor.resetRequested.connect(itemViewer.resetImage)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(itemList)
        self.layout().addWidget(itemViewer)
        self.layout().addWidget(itemEditor)

    def _createList(self, baby_animals) -> QtWidgets.QListWidget:
        '''create the list viwer sub-widget wichi contains the items'''
        from ...resources import get_path_to_img
        list = QtWidgets.QListWidget()
        for baby_animal in baby_animals:
            file_path = get_path_to_img(baby_animal + '.jpg')
            item = QtWidgets.QListWidgetItem(
                QtGui.QIcon(file_path), baby_animal)
            item.setData(self.ImageDataRole, QtGui.QImage(file_path))
            item.setData(self.DescriptionRole,
                         f"This is a cute image of a {baby_animal}.")
            list.addItem(item)

        list.setMaximumWidth(300)

        return list

    def _createItemViewer(self) -> QtWidgets.QWidget:
        '''create the item viewer sub-widget'''
        viewer = QtWidgets.QWidget(self)

        title = QtWidgets.QLabel('image title')
        title.setProperty('title', True)
        title.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                            QtWidgets.QSizePolicy.Policy.Maximum)
        viewer.setTitle = title.setText

        descr = QtWidgets.QLabel('image discription')
        descr.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                            QtWidgets.QSizePolicy.Policy.Maximum)
        viewer.setDescription = descr.setText

        img = QtWidgets.QLabel('waiting for image')
        img._mustache = None
        img.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        img.minimumSizeHint = lambda: QtCore.QSize(250, 250)
        img.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                          QtWidgets.QSizePolicy.Policy.Expanding)

        def setImage(image: QtGui.QImage):
            if image.height()/img.height() > image.width()/img.width():
                i = image.scaledToHeight(img.height())
            else:
                i = image.scaledToWidth(img.width())

            img.setPixmap(QtGui.QPixmap.fromImage(i))
            img.sizeHint = lambda: image.size()
        viewer.setImage = setImage

        def resetImage():
            if viewer._activeItem is not None:
                viewer.setImage(viewer._activeItem.data(self.ImageDataRole))
        viewer.resetImage = resetImage

        def setActiveItem(item:  QtWidgets.QListWidgetItem):
            viewer._activeItem = item
            viewer.setTitle(item.text())
            viewer.setImage(item.data(self.ImageDataRole))
            viewer.setDescription(item.data(self.DescriptionRole))
        viewer._activeItem = None
        viewer.setActiveItem = setActiveItem

        def updateActiveItem():
            if viewer._activeItem is not None:
                viewer.setTitle(viewer._activeItem.text())
                viewer.setImage(viewer._activeItem.data(self.ImageDataRole))
                viewer.setDescription(
                    viewer._activeItem.data(self.DescriptionRole))
        viewer.updateActiveItem = updateActiveItem

        def resizeEvent(event: QtGui.QResizeEvent):
            if viewer._activeItem is not None:
                viewer.setImage(viewer._activeItem.data(self.ImageDataRole))
        viewer.resizeEvent = resizeEvent

        def setMustache(id: int):
            from ...resources import get_path_to_img
            if id > 0:
                img._mustache = QtGui.QImage(
                    get_path_to_img(f'mustache{id}.png'))
            else:
                img._mustache = None
        viewer.setMustache = setMustache

        def setMustacheScale(scale: int):
            img._mustacheScale = scale
        img._mustacheScale = 20
        viewer.setMustacheScale = setMustacheScale

        def drawMustache(event: QtGui.QMouseEvent):
            if img._mustache is not None and viewer._activeItem is not None:
                m = img._mustache.scaledToWidth(
                    img.pixmap().width()*img._mustacheScale//100)
                p = QtCore.QPoint(
                    event.x() - m.width()//2 - (img.width() - img.pixmap().width())//2,
                    event.y() - m.height()//2 - (img.height() - img.pixmap().height())//2)
                painter = QtGui.QPainter(img.pixmap())
                painter.drawImage(p, m)
                painter.end()
                img.update()
            event.accept()
        img.mousePressEvent = drawMustache

        viewer.setLayout(QtWidgets.QVBoxLayout())
        viewer.layout().addWidget(title)
        viewer.layout().addWidget(descr)
        viewer.layout().addWidget(img)

        return viewer

    def _createItemEditor(self) -> QtWidgets.QWidget:
        '''create the item editor sub-widget'''

        class Editor(QtWidgets.QWidget):
            itemEdited = QtCore.pyqtSignal()
            mustacheSelected = QtCore.pyqtSignal(int)
            mustacheScale = QtCore.pyqtSignal(int)
            resetRequested = QtCore.pyqtSignal()

            def __init__(self) -> None:
                super().__init__()

                self._activeItem: 'QtWidgets.QListWidgetItem|None' = None

                self.name_editor = QtWidgets.QLineEdit()
                self.name_editor.editingFinished.connect(self.editItemName)

                self.descr_editor = QtWidgets.QPlainTextEdit()
                self.descr_editor.keyPressEvent = self.editItemDescr
                self.descr_editor.focusOutEvent = self.editItemDescr

                mustaches = QtWidgets.QGroupBox('Mustaches')
                mustaches.setCheckable(True)
                mustaches.setChecked(False)
                bg = QtWidgets.QButtonGroup()
                bgl = QtWidgets.QHBoxLayout()
                for id in range(1, 3):
                    rb = QtWidgets.QRadioButton(f'Mustache {id}')
                    if id == 1:
                        rb.setChecked(True)
                    bgl.addWidget(rb)
                    bg.addButton(rb, id)
                mustaches.toggled.connect(lambda active: self.mustacheSelected.emit(
                    bg.checkedId()) if active else (self.resetRequested.emit(), self.mustacheSelected.emit(0)))
                bg.idClicked.connect(self.mustacheSelected.emit)

                scaler = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
                scaler.setRange(0, 100)
                scaler.setValue(20)
                scaler.valueChanged.connect(self.mustacheScale)

                mustaches.setLayout(QtWidgets.QVBoxLayout())
                mustaches.layout().addLayout(bgl)
                mustaches.layout().addWidget(scaler)

                buttons = QtWidgets.QHBoxLayout()
                buttons.addWidget(QtWidgets.QPushButton('Does Nothing'))
                buttons.addWidget(QtWidgets.QPushButton('Also Nothing'))

                self.setLayout(QtWidgets.QFormLayout())
                self.layout().addRow('Name', self.name_editor)
                self.layout().addRow('Description', self.descr_editor)
                self.layout().addRow(mustaches)
                self.layout().addRow(buttons)
                self.layout().addItem(QtWidgets.QSpacerItem(0, 0,
                                                            QtWidgets.QSizePolicy.Policy.Maximum,
                                                            QtWidgets.QSizePolicy.Policy.Expanding))

            def setActiveItem(self, item: QtWidgets.QListWidgetItem):
                self._activeItem = item
                self.name_editor.setText(item.text())
                self.descr_editor.setPlainText(
                    item.data(ComplexPlaceholder.DescriptionRole))

            def editItemName(self):
                if self._activeItem is not None:
                    self._activeItem.setText(self.name_editor.text())
                    self.itemEdited.emit()

            def editItemDescr(self, event: 'QtGui.QFocusEvent | QtGui.QKeyEvent'):
                if isinstance(event, QtGui.QKeyEvent):
                    if not (event.key() == QtCore.Qt.Key.Key_Return and not event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier):
                        # pass the keypress on the the text editor
                        return QtWidgets.QPlainTextEdit.keyPressEvent(self.descr_editor, event)

                if self._activeItem is not None:
                    self._activeItem.setData(ComplexPlaceholder.DescriptionRole,
                                             self.descr_editor.toPlainText())
                    self.itemEdited.emit()

                if isinstance(event, QtGui.QFocusEvent):
                    self.descr_editor.__class__.focusOutEvent(
                        self.descr_editor, event)
                else:
                    self.descr_editor.clearFocus()

        return Editor()
