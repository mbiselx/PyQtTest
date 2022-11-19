
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
        self._image_rect = QtCore.QRect()

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
                p.drawText(self.rect(),
                           QtCore.Qt.AlignmentFlag.AlignCenter,
                           "no img")

        else:
            scaler = self._image.size().scaled(
                self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self._image_rect.setTopLeft(QtCore.QPoint((self.width() - scaler.width())//2,
                                                      (self.height() - scaler.height())//2))
            self._image_rect.setSize(scaler)

            with QtGui.QPainter(self) as p:
                p.drawImage(self._image_rect,
                            self._image,
                            self._image.rect())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.timer.stop()
        self.video.release()
        self.deleteLater()
        return super().closeEvent(a0)


class PathWidget(QtWidgets.QFrame):
    pathChanged = QtCore.pyqtSignal()

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self._path_segments: 'list[QtWidgets.QLineEdit]' = []

        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(*4*[0])
        self.setContentsMargins(*4*[0])

    def _remove_all(self):
        for i in range(self.layout().count()):
            w = self.layout().takeAt(i)
            if isinstance(w, QtWidgets.QLineEdit):
                w.editingFinished.disconnect(self.pathChanged)

    def setDepth(self, depth: int):
        if len(self._path_segments) > 0:
            self._remove_all()

        self._path_segments = [QtWidgets.QLineEdit(self) for i in range(depth)]

        for segment in self._path_segments:
            self.layout().addWidget(segment)
            if segment is not self._path_segments[-1]:
                self.layout().addWidget(QtWidgets.QLabel(os.sep, self))
            segment.editingFinished.connect(self.pathChanged)

    def setPath(self, path: str):
        path_segments = path.split(os.sep)

        if len(self._path_segments) < len(path_segments):
            self.setDepth(len(path_segments))

        for segment_lbl, segment_txt in zip(self._path_segments, path_segments):
            segment_lbl.setText(segment_txt)

    def path(self) -> str:
        return os.sep.join(segment.text() for segment in self._path_segments)


class SimpleCamera(QtWidgets.QFrame):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 destination_folder: str = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags,
                                     QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.stream_display = CameraStreamer(self)
        self.stream_display.setMinimumSize(200, 200)

        self._destination_folder = destination_folder

        self.destination_selector = PathWidget(self)
        self.destination_selector.setDepth(3)
        self.destination_selector.pathChanged.connect(self.setDestinationPath)

        self.root_selector = QtWidgets.QToolButton(self)
        self.root_selector.setText('...')
        self.root_selector.clicked.connect(self.setRootFolder)

        self.trigger_button = QtWidgets.QPushButton('photo', self)
        self.trigger_button.clicked.connect(self.takePhoto)
        self.trigger_button.setDisabled(destination_folder is None)

        # layout stuff
        bottom_bar = QtWidgets.QHBoxLayout()
        bottom_bar.addWidget(self.root_selector)
        bottom_bar.addWidget(self.destination_selector)
        bottom_bar.addWidget(self.trigger_button)

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(self.stream_display)
        self.layout().addLayout(bottom_bar)

    def setRootFolder(self, *, folder: str = None):
        if folder is None:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self)
            if folder == '':
                return

        logging.debug(
            f'{self.__class__.__name__}: root folder set to {folder}')
        self._root_folder = folder
        self.trigger_button.setEnabled(True)

    def setDestinationPath(self, *, folder: str = None):
        self._destination_folder = os.sep.join(
            (self._root_folder, self.destination_selector.path()))

        logging.debug(
            f'{self.__class__.__name__}: destination folder set to {self._destination_folder}')

    def takePhoto(self):
        # create outfile name based on date and time
        date = QtCore.QDate.currentDate().toString(QtCore.Qt.DateFormat.ISODate)
        time = QtCore.QTime.currentTime().toString('hh-mm-ss')
        outfile = os.sep.join((self._destination_folder,
                               f"{date}-{time}_webcam.jpg"))

        # check if destination folder exists, and if not, create it
        if not (os.path.isdir(self._destination_folder)):
            os.makedirs(self._destination_folder)

        # save image
        if not self.stream_display.image().save(outfile):
            logging.error(
                f"{self.__class__.__name__}: failed to write {outfile}")
