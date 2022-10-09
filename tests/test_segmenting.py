#!/usr/bin/env python3
'''
A file used for testing

Author  :   Michael Biselx
Date    :   10.2022
Project :   PyQtTest
'''

from PyQt5 import QtCore, QtWidgets

from PyQtTest.widgets.hit_marker.image_segmentor import ClickableSegmentImage
from PyQtTest.widgets.utils.reloadable_widget import ReloadableWidget
from PyQtTest.resources import get_path_to_img

if __name__ == '__main__':
    import sys

    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = ReloadableWidget(
        flags=QtCore.Qt.WindowType.WindowStaysOnTopHint,
        widget=ClickableSegmentImage,
        img_path=get_path_to_img('car_outline.jpg'),
        outline_img=True
    )
    mw.show()
    print("widget has been shown")

    sys.exit(app.exec_())
