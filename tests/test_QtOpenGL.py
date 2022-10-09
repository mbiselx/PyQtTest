from PyQt5 import QtCore      # core Qt functionality
from PyQt5 import QtGui       # extends QtCore with GUI functionality
from PyQt5 import QtWidgets       # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget

import OpenGL.GL as gl        # python wrapping of OpenGL
from OpenGL import GLU        # OpenGL Utility Library, extends OpenGL functionality

import sys                    # we'll need this later to run our Qt application

from OpenGL.arrays import vbo
import numpy as np


from PyQtTest.widgets.hud.navball_pyqtgraph import IsoNavball, NavballWidget, UVNavball


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None, geometry='cube'):
        self.parent = parent
        self._geometry = geometry
        QtOpenGL.QGLWidget.__init__(self, parent)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 500)

    def initializeGL(self):
        # initialize the screen to blue
        self.qglClearColor(QtGui.QColor(0, 0, 0, 0))
        gl.glEnable(gl.GL_DEPTH_TEST)                  # enable depth testing

        self.initGeometry()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glPushMatrix()    # push the current matrix to the current stack

        # third, translate cube to specified depth
        gl.glTranslate(0.0, 0.0, -4.0)
        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        # first, translate cube center to origin
        gl.glTranslate(-0.5, -0.5, -0.5)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.vertVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, self.colorVBO)

        gl.glDrawElements(gl.GL_TRIANGLES, len(self.faces),
                          gl.GL_UNSIGNED_INT, self.faces)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glPopMatrix()    # restore the previous modelview matrix

    def initGeometry(self):
        if self._geometry == 'cube':
            self.initCube()
        else:
            self.initBall()

    def initCube(self):
        cubeVtxArray = np.array(
            [[-1.0, -1.0, -1.0],
             [1.0, -1.0, -1.0],
             [1.0, 1.0, -1.0],
             [-1.0, 1.0, -1.0],
             [-1.0, -1.0, 1.0],
             [1.0, -1.0, 1.0],
             [1.0, 1.0, 1.0],
             [-1.0, 1.0, 1.0]])
        self.vertVBO = vbo.VBO(np.reshape(cubeVtxArray,
                                          (1, -1)).astype(np.float32))
        self.vertVBO.bind()

        self.cubeClrArray = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]])
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray,
                                           (1, -1)).astype(np.float32))
        self.colorVBO.bind()

        self.faces = np.array(
            [0, 1, 2,
             0, 3, 2,
             3, 2, 6,
             3, 7, 6,
             1, 0, 4,
             1, 5, 4,
             2, 1, 5,
             2, 6, 5,
             0, 3, 7,
             0, 4, 7,
             7, 6, 5,
             7, 4, 5])

    def initBall(self):
        self.ball = IsoNavball(0)

        self.vertVBO = vbo.VBO(np.array(self.ball.vertices,
                                        dtype=np.float32).reshape((1, -1)))
        self.vertVBO.bind()

        # self.colorVBO = vbo.VBO(np.array(ball.face_colors,
        #                                  dtype=np.float32)[:, :3].reshape((1, -1)))
        self.colorVBO = vbo.VBO(np.array(len(self.ball.vertices) * [(1.0, 0.0, 0.0)],
                                         dtype=np.float32).reshape((1, -1)))
        self.colorVBO.bind()

        self.faces = np.array(self.ball.faces).reshape((1, -1)).squeeze()
        print(self.faces)

    def setRotX(self, val):
        self.rotX = val

    def setRotY(self, val):
        self.rotY = val

    def setRotZ(self, val):
        self.rotZ = val


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        # call the init for the parent class
        QtWidgets.QMainWindow.__init__(self)

        self.setWindowTitle('Hello OpenGL App')

        self.glWidget1 = GLWidget(self, 'cube')
        self.glWidget2 = GLWidget(self, 'ball')
        self.initGUI()

        timer = QtCore.QTimer(self)
        timer.setInterval(20)   # period, in milliseconds
        timer.timeout.connect(self.glWidget1.updateGL)
        timer.timeout.connect(self.glWidget2.updateGL)
        timer.start()

    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        GL_layout = QtWidgets.QHBoxLayout()
        gui_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(gui_layout)

        self.setCentralWidget(central_widget)

        GL_layout.addWidget(self.glWidget1)
        GL_layout.addWidget(self.glWidget2)
        gui_layout.addLayout(GL_layout)

        sliderX = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        sliderX.valueChanged.connect(lambda val: self.glWidget1.setRotX(val))
        sliderX.valueChanged.connect(lambda val: self.glWidget2.setRotX(val))

        sliderY = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        sliderY.valueChanged.connect(lambda val: self.glWidget1.setRotY(val))
        sliderY.valueChanged.connect(lambda val: self.glWidget2.setRotY(val))

        sliderZ = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        sliderZ.valueChanged.connect(lambda val: self.glWidget1.setRotZ(val))
        sliderZ.valueChanged.connect(lambda val: self.glWidget2.setRotZ(val))

        gui_layout.addWidget(sliderX)
        gui_layout.addWidget(sliderY)
        gui_layout.addWidget(sliderZ)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
