#!/usr/bin/env python3
'''
A module for displaying a KSP-style navball

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

from PyQt5 import QtCore, QtGui, QtWidgets, Qt3DCore, Qt3DRender, Qt3DExtras


def createScene():
    # root
    rootEntity = Qt3DCore.QEntity()
    material = Qt3DExtras.QPhongMaterial(rootEntity)

    # sphere
    sphereEntity = Qt3DCore.QEntity(rootEntity)
    sphereMesh = Qt3DExtras.QSphereMesh()
    sphereMesh.setRadius(3)

    sphereEntity.addComponent(sphereMesh)
    sphereEntity.addComponent(material)

    return rootEntity


def createCamera(view: Qt3DExtras.Qt3DWindow) -> Qt3DRender.QCamera:
    camera = view.camera()
    camera.lens().setPerspectiveProjection(45.0, 1, 0.1, 1000)
    camera.setPosition(QtGui.QVector3D(0, 0, 15))
    camera.setViewCenter(QtGui.QVector3D(0, 0, 0))
    return camera


class NavballWidget(QtWidgets.QLabel):
    def __init__(self, parent: QtWidgets.QWidget = None) -> 'NavballWidget':
        super().__init__(parent)
        self.view3d = Qt3DExtras.Qt3DWindow()

        self.scene = createScene()
        self.camera = createCamera(self.view3d)
        self.camController = Qt3DExtras.QOrbitCameraController(self.scene)
        self.camController.setLinearSpeed(0)
        self.camController.setLookSpeed(0)
        self.camController.setCamera(self.camera)
        self.view3d.setRootEntity(self.scene)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(QtWidgets.QWidget.createWindowContainer(self.view3d, parent))


if __name__ == "__main__":
    import sys

    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = NavballWidget()
    mw.show()

    sys.exit(app.exec_())
