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

import cv2
import typing
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    from ..plotting import colors
except (ImportError, ValueError):  # for the demo
    from PyQtTest.widgets.plotting import colors


def segment_image(img: np.ndarray = None, img_path: str = None) -> 'tuple[int, np.ndarray]':
    '''
    takes a dark image on bright background

    @parameters:
    * `img`      : image array
    * `img_path` : path to the image file

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
    return cv2.connectedComponents(~img_b, ltype=cv2.CV_16U)


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
        # True: colors.purple,
        False: colors.gray,
        None: colors.transparent
    }

    def __init__(self,
                 parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget,
                 img_path: str = None,
                 * args, **kwargs):
        super().__init__(parent=parent, flags=flags)

        if img_path:
            self.setImage(img=img_path)

    def setImage(self, img: typing.Union[str, np.ndarray]):
        '''set the image from a path or from a numpy array'''

        if isinstance(img, str):
            self.n_lbls, self.labels = segment_image(img_path=img)

            self.colorLabels = dict([(0, self._palette[None])] +
                                    [(l, self._palette[False]) for l in range(1, self.n_lbls)])
            img = color_image_by_segments(self.labels, self.colorLabels)

        pxmp = QtGui.QPixmap.fromImage(
            QtGui.QImage(img, img.shape[1], img.shape[0],
                         QtGui.QImage.Format.Format_RGBA8888)
        )
        self.setPixmap(pxmp)

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


class ClickableSegmentImage(SegmentImage):
    '''an image with segments whose color can be set individually by clicking them'''

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        '''on click'''
        x, y = round(event.localPos().x()), round(event.localPos().y())
        self.setOnlyRegionActive(self.labels[y][x])

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
