from PyQt5 import QtCore, QtGui, QtWidgets

from guifw.gui_elements import MenuBar

import widgets

import typing


class GeneratorWidget(QtWidgets.QWidget):
    def __init__(self, parent: typing.Optional[QtWidgets.QMainWindow] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.dock_counter = 0

        makerBtn = QtWidgets.QPushButton(parent=self, text="Make Dock Widget")
        makerBtn.clicked.connect(self.makeDockWidget)

        lbl = QtWidgets.QLabel(parent=self, text="Hello World")
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(lbl)
        self.layout().addWidget(makerBtn)

        self.setGeometry(100, 200, 300, 80)

    def makeDockWidget(self):
        self.dock_counter += 1
        dockWidget = QtWidgets.QDockWidget(parent=self.parentWidget())
        dockWidget.setWindowTitle(f"Dock {self.dock_counter}")
        dockWidget.setWidget(QtWidgets.QLabel(
            parent=self.parentWidget(), text=f"Dock {self.dock_counter}"))
        dockWidget.setGeometry(100, 0, 200, 30)

        # setting allowed areas
        dockWidget.setAllowedAreas(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)

        if hasattr(self.parentWidget(), 'addDockWidget'):
            self.parentWidget().addDockWidget(
                QtCore.Qt.DockWidgetArea.TopDockWidgetArea, dockWidget)
        else:
            dockWidget.setFloating(True)
            dockWidget.show()


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.WindowType.Window) -> None:
        super().__init__(parent, flags)

        self.setMenuWidget(widgets.WidgetMaker())

        self.setCentralWidget(GeneratorWidget(parent=self))
        # self.setDockOptions(self.DockOption.AllowTabbedDocks)
        self.setWindowTitle("Docking Test")
        self.setGeometry(100, 200, 300, 80)


if __name__ == '__main__':
    import sys

    print(f"running {__file__} as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = MyMainWindow()
    mw.show()

    sys.exit(app.exec_())
