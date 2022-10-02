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

import pickle
import cv2
import typing
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    from ..plotting import colors
    from ...resources import image_label_folder, get_path_to_img
except (ImportError, ValueError):  # for the demo
    from PyQtTest.widgets.plotting import colors
    from PyQtTest.resources import image_label_folder, get_path_to_img


def segment_image(img: np.ndarray = None,
                  img_path: str = None,
                  outline_img: bool = True) -> 'tuple[int, np.ndarray]':
    '''
    takes a dark area image on bright background

    @parameters:
    * `img`         : image array
    * `img_path`    : path to the image file
    * `outline_img` : use an outline image instead of an area image

    @returns :
    * `(nb_lbls, labels)` : the number of labels in the image,
            as well as the labeled image
    '''

    if img is None:
        if img_path is None:
            raise RuntimeError("Either an image or a path must be specified")
        else:
            img = cv2.imread(img_path)

    # get image in grayscale
    img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # binarize
    _, img_b = cv2.threshold(img_g, 0, 255,
                             cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # segment
    if not outline_img:
        return cv2.connectedComponents(~img_b, ltype=cv2.CV_16U)
    else:
        n_lbls, labels = cv2.connectedComponents(img_b, ltype=cv2.CV_16U)
        # set the background labels to 0 (assumption: the first area
        # returned after the outline is the background):
        labels[labels > 0] -= 1

        return n_lbls, labels


def color_image_by_segments(labels: np.ndarray, color_dict: 'dict[int, colors.ColorRGBA]') -> np.ndarray:
    '''
    colors an image based on given labels

    @parameters :
    * `labels`: the labeled image
    * `color_dict` : a dictionary containing the colors by label

    @returns :
    * `img` : the colorized image
    '''
    img = np.zeros((*labels.shape, 4), dtype=np.uint8)

    for label, color in color_dict.items():
        img[np.where(labels == label)] = color

    return img


class SegmentImage(QtWidgets.QLabel):
    '''an image with segments whose color can be set individually'''
    _palette: 'dict[None|bool, colors.ColorRGBA]' = {
        True: colors.red,
        False: colors.gray,
        None: colors.transparent
    }
    _segment_names: 'dict[int, str]' = {}

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 img_path: str = None,
                 * args, **kwargs):
        super().__init__(parent=parent, flags=flags)

        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)

        class InstantToolTipSyle(QtWidgets.QProxyStyle):
            '''a stye which shows the tool tip without delay'''

            def styleHint(self, hint: QtWidgets.QStyle.StyleHint,
                          option: typing.Optional[QtWidgets.QStyleOption] = None,
                          widget: typing.Optional[QtWidgets.QWidget] = None,
                          returnData: typing.Optional[QtWidgets.QStyleHintReturn] = None) -> int:
                if hint == QtWidgets.QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
                    return 0
                else:
                    return super().styleHint(hint, option, widget, returnData)

        self.setStyle(InstantToolTipSyle(self.style()))

        if img_path:
            self.setImage(img=img_path)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        '''track the mouse to display relevant tool tip'''
        lbl = self.labels[round(event.localPos().y()),
                          round(event.localPos().x())]
        # don't show tooltip for background
        self.setToolTip(self._segment_names[lbl] if lbl != 0 else '')
        # don't pass the event on
        event.accept()

    def setImage(self, img: typing.Union[str, np.ndarray]):
        '''set the image from a path or directly from a numpy array'''

        if isinstance(img, str):
            self.n_lbls, self.labels = segment_image(img_path=img)

            # create the tooltip segment names
            self._segment_names = dict(
                zip(range(self.n_lbls), map(str, range(self.n_lbls))))

            self.colorLabels = dict([(0, self._palette[None])] +
                                    [(l, self._palette[False]) for l in range(1, self.n_lbls)])
            img = color_image_by_segments(self.labels, self.colorLabels)

        pxmp = QtGui.QPixmap.fromImage(
            QtGui.QImage(img, img.shape[1], img.shape[0],
                         QtGui.QImage.Format.Format_RGBA8888)
        )
        self.setPixmap(pxmp)

    def setLabelName(self, label: int, name: str):
        '''set the name to display in the tooltip'''
        self._segment_names[label] = name

    def setLabelNames(self, names: 'list[str]'):
        '''set the names to display in the tooltip'''
        for lbl, name in enumerate(names):
            self._segment_names[lbl] = name

    def setOnlyRegionActive(self, label: int):
        '''set a single region as active, switching the others off'''
        self.colorLabels = dict([(0, self._palette[None])] +
                                [(l, self._palette[l == label]) for l in range(1, self.n_lbls)])
        img = color_image_by_segments(self.labels, self.colorLabels)
        self.setImage(img)

    def updateRegionActive(self, label: int, active: bool = True):
        '''change the state of a region, leaving the others unchanged'''
        self.colorLabels[label] = self._palette[active]
        img = color_image_by_segments(self.labels, self.colorLabels)
        self.setImage(img)

    def activeRegions(self) -> 'list[int]':
        return [l for l, c in self.colorLabels.items() if c == self._palette[True]]

    def activeRegionNames(self) -> 'list[str]':
        return [self._segment_names[l] for l in self.activeRegions()]


class ClickableSegmentImage(SegmentImage):
    '''an image with segments whose color can be set individually by clicking them'''

    clicked = QtCore.pyqtSignal()
    clicked_segment = QtCore.pyqtSignal(int)

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None, flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget, img_path: str = None, *args, **kwargs):
        super().__init__(parent, flags, img_path, *args, **kwargs)

        class SetNameAction(QtWidgets.QAction):
            newName = QtCore.pyqtSignal(int, str)

            def __init__(self, *args, text='Set &Name', **kwargs) -> None:
                super().__init__(text=text, *args, **kwargs)
                self.dialog = QtWidgets.QInputDialog()
                self.dialog.setWindowFlags(self.dialog.windowFlags() &
                                           ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)
                self.setIcon(QtGui.QIcon(get_path_to_img('label.webp')))
                self.dialog.setWindowTitle("Set segment name")
                self.dialog.setLabelText('New segment name :')
                self.dialog.accepted.connect(self._newName)

                self.triggered.connect(self._showDialog)

            def _showDialog(self):
                '''internal callback'''
                active = self.parentWidget().activeRegionNames()
                if len(active) == 1:  # only show if there's an active region
                    self.dialog.setTextValue(active[0])
                    self.dialog.show()

            def _newName(self):
                '''internal callback'''
                l = self.parentWidget().activeRegions()[0]
                lbl = self.dialog.textValue()
                self.parentWidget().setLabelName(l, lbl)
                self.newName.emit(l, lbl)

        class ExportNamesAction(QtWidgets.QAction):
            def __init__(self, parent: QtWidgets.QWidget, *args, text='&Export Names', **kwargs) -> None:
                super().__init__(text, parent, *args, **kwargs)
                self.setIcon(parent.style().standardIcon(
                    QtWidgets.QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton))
                self.triggered.connect(self._exportNames)

            def _exportNames(self):
                '''internal callback'''
                filename = QtWidgets.QFileDialog.getSaveFileName(self.parentWidget(),
                                                                 'Choose the file to export to', image_label_folder,
                                                                 'PICKLE (*.p)')
                if filename[0] != '':
                    outfile = filename[0] + (
                        '.p' if not filename[0].lower().endswith('.p') else '')

                    with open(outfile, 'wb') as file:
                        pickle.dump(self.parentWidget()._segment_names, file)

        class ImportNamesAction(QtWidgets.QAction):
            def __init__(self, parent: QtWidgets.QWidget, *args, text='&Import Names', **kwargs) -> None:
                super().__init__(text, parent, *args, **kwargs)

                pxmp: QtGui.QPixmap = parent.style().standardIcon(
                    QtWidgets.QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton).pixmap(QtCore.QSize(32, 32))
                pxmp = pxmp.transformed(QtGui.QTransform(*[-1, 0, 0,
                                                           0, 1, 0,
                                                           0, 0, 1]), QtCore.Qt.TransformationMode.SmoothTransformation)
                self.setIcon(QtGui.QIcon(pxmp))
                self.triggered.connect(self._importNames)

            def _importNames(self):
                '''internal callback'''
                filename = QtWidgets.QFileDialog.getOpenFileName(self.parentWidget(),
                                                                 'Choose the file to import from', image_label_folder,
                                                                 'PICKLE (*.p)')
                if filename[0] != '':
                    infile = filename[0] + (
                        '.p' if not filename[0].lower().endswith('.p') else '')

                    with open(infile, 'rb') as file:
                        self.parentWidget()._segment_names = pickle.load(file)

        self.addActions([SetNameAction(parent=self),
                         ExportNamesAction(parent=self),
                         ImportNamesAction(parent=self)])
        self.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        '''on click'''
        lbl = self.labels[round(event.localPos().y()),
                          round(event.localPos().x())]
        self.setOnlyRegionActive(lbl)
        self.clicked.emit()
        self.clicked_segment.emit(lbl)
        event.accept()

############################################
#  DEMO
############################################


if __name__ == '__main__':
    import sys
    from PyQtTest.resources import get_path_to_img

    app = QtWidgets.QApplication(sys.argv)

    img_path = get_path_to_img('car.jpg')

    # demonstrate integration into QtWidget
    mw = ClickableSegmentImage(img_path=img_path)
    mw.setWindowTitle("integration demo")
    mw.show()

    sys.exit(app.exec_())
