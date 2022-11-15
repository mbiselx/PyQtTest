
import typing
import logging

import os
import cv2

from PyQt5 import QtCore, QtGui, QtWidgets


class CameraStreamer(QtWidgets.QFrame):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 image: typing.Optional[QtGui.QImage] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)
        self._image = QtGui.QImage() if image is None else image

        self.video = cv2.VideoCapture(0)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._refresh_display)
        self.timer.start()

    def minimumSizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(50, 50)

    def image(self) -> QtGui.QImage:
        return self._image

    def _refresh_display(self):
        ret, frame = self.video.read()

        if ret:
            self._image = QtGui.QImage(frame,
                                       frame.shape[1],
                                       frame.shape[0],
                                       QtGui.QImage.Format.Format_BGR888)
            self.update()
        else:
            logging.debug('No image')

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:

        if self._image.isNull():

            with QtGui.QPainter(self) as p:
                p: QtGui.QPainter
                p.drawText(
                    a0.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, "no img")

        else:
            if self._image.height()*a0.rect().width() > self._image.width()*a0.rect().height():
                h = a0.rect().height()
                w = self._image.width()/self._image.height()*a0.rect().height()
            else:
                h = self._image.height()/self._image.width()*a0.rect().width()
                w = a0.rect().width()

            self._image_rect = QtCore.QRect(
                (a0.rect().width() - w)//2, (a0.rect().height() - h)//2,
                w, h)

            with QtGui.QPainter(self) as p:
                p: QtGui.QPainter
                p.drawImage(self._image_rect,
                            self._image, self._image.rect())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.timer.stop()
        self.video.release()
        return super().closeEvent(a0)


class SimpleCamera(QtWidgets.QFrame):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 destination_folder: str = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.stream_display = CameraStreamer(self)

        self.destination_folder = destination_folder

        self.destination_selector = QtWidgets.QToolButton(self)
        self.destination_selector.setText('...')
        self.destination_selector.clicked.connect(self.setDestinationFolder)

        self.trigger_button = QtWidgets.QPushButton('photo', self)
        self.trigger_button.clicked.connect(self.takePhoto)
        self.trigger_button.setDisabled(destination_folder is None)

        # layout stuff
        bottom_bar = QtWidgets.QHBoxLayout()
        bottom_bar.addWidget(self.trigger_button)
        bottom_bar.addWidget(self.destination_selector)

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(self.stream_display)
        self.layout().addLayout(bottom_bar)

    def setDestinationFolder(self, *, folder: str = None):
        if folder is None:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self)
            if folder == '':
                return

        logging.debug(
            f'{self.__class__.__name__}: destination folder set to {folder}')
        self.destination_folder = folder
        self.trigger_button.setEnabled(True)

    def takePhoto(self):
        date = QtCore.QDate.currentDate().toString(QtCore.Qt.DateFormat.ISODate)
        time = QtCore.QTime.currentTime().toString('hh-mm-ss')
        outfile = os.sep.join((self.destination_folder,
                               f"{date}-{time}_webcam.jpg"))
        if not self.stream_display.image().save(outfile):
            logging.error(
                f"{self.__class__.__name__}: failed to write {outfile}")
