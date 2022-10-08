#!/usr/bin/env python3
'''
A module for displaying a KSP-style navball

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

import math
from multiprocessing.sharedctypes import Value
import numpy as np

from PyQt5 import QtCore, QtWidgets
from pyqtgraph.opengl import GLViewWidget, MeshData, GLMeshItem


class AbstractGeometry():

    vertices = [[]]
    faces = [[]]
    face_colors = [[]]

    def mesh(self) -> MeshData:

        return MeshData(vertexes=np.array(self.vertices),
                        faces=np.array(self.faces),
                        faceColors=np.array(self.face_colors) if len(self.face_colors) > 0 else None)


class Icosahedron(AbstractGeometry):
    _X = .525731112119133606
    _Z = .850650808352039932

    vertices = [
        [-_X, 0., _Z], [_X, 0., _Z], [-_X, 0., -_Z], [_X, 0., -_Z],
        [0., _Z, _X], [0., _Z, -_X], [0., -_Z, _X], [0., -_Z, -_X],
        [_Z, _X, 0.], [-_Z, _X, 0.], [_Z, -_X, 0.], [-_Z, -_X, 0.]
    ]

    faces = [
        [0, 4, 1],  [0, 9, 4],  [9, 5, 4], [4, 5, 8], [4, 8, 1],
        [8, 10, 1], [8, 3, 10], [5, 3, 8], [5, 2, 3], [2, 7, 3],
        [7, 10, 3], [7, 6, 10], [7, 11, 6], [11, 0, 6], [0, 1, 6],
        [6, 1, 10], [9, 0, 11], [9, 11, 2], [9, 2, 5], [7, 2, 11]
    ]


class IsoSphere(Icosahedron):
    def __init__(self, subdivisions=2) -> None:
        super().__init__()

        for div in range(subdivisions):
            self._subdivide()

    def _midpoint(self, p1, p2):
        p3 = [i + j for i, j in zip(p1, p2)]
        p3n = np.sqrt(sum([p**2 for p in p3]))
        return [p/p3n for p in p3]

    def _subdivide(self):
        new_faces = []

        for i, face in enumerate(self.faces):

            midpoint_idx = []
            for i in range(3):
                mp = self._midpoint(self.vertices[face[i]],
                                    self.vertices[face[(i+1) % 3]])

                idx = [idx for idx, v in enumerate(self.vertices) if sum(
                    (p1 - p2)**2 for p1, p2 in zip(mp, v)) < 1e-2]
                print(idx)
                if len(idx) > 0:
                    midpoint_idx.append(idx[0])
                else:
                    self.vertices.append(mp)
                    midpoint_idx.append(len(self.vertices)-1)

            # self.vertices.extend(midpoints)
            new_faces.append([face[0], midpoint_idx[0], midpoint_idx[2]])
            new_faces.append([midpoint_idx[0], face[1], midpoint_idx[1]])
            new_faces.append([midpoint_idx[2], midpoint_idx[1], face[2]])
            new_faces.append(midpoint_idx)

        self.faces = new_faces

        print(len(self.vertices))


class IsoNavball(IsoSphere):
    palette = {
        True: (1, 0, 0, 1),
        False: (0, 0, 1, 1)
    }

    def __init__(self) -> None:
        super().__init__(subdivisions=1)
        self._colorize()

    def _colorize(self):
        self.face_colors = []
        for face in self.faces:
            is_below = any(self.vertices[v][2] < 0 for v in face)
            self.face_colors.append(self.palette[is_below])


class Octahedron(AbstractGeometry):

    vertices = [
        [0, 0, 1],
        [1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0],
        [0, 0, -1]
    ]

    faces = [
        [0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1],
        [5, 1, 2], [5, 2, 3], [5, 3, 4], [5, 4, 1],
    ]


class UVSphere(AbstractGeometry):

    def __init__(self, nb_gores: int = 6, nb_rows: int = 3) -> None:

        self.vertices = [[0, 0, 1]]  # north pole
        for theta in reversed(np.linspace(-np.pi/2, np.pi/2, nb_rows+2, True)[1:-1]):
            for phi in np.linspace(0, 2*np.pi,  nb_gores, False):
                self.vertices.append(
                    [math.cos(phi)*math.cos(theta), math.sin(phi)*math.cos(theta), math.sin(theta)])
        self.vertices.extend([[0, 0, -1]])  # south pole

        n = len(self.vertices) - 1

        top_faces = [[0, g, 1+g % nb_gores]
                     for g in range(1, nb_gores+1)]
        bottom_faces = [[n-g-1, n-(g if g > 0 else nb_gores), n]
                        for g in reversed(range(nb_gores))]

        self.faces = top_faces
        for r in range(nb_rows-1):
            for g in range(1, nb_gores+1):
                self.faces.append(  # upper triangle
                    [r*nb_gores + g,
                     r*nb_gores + 1 + g % nb_gores,
                     (r+1)*nb_gores + g]
                )
                self.faces.append(  # lower triangle
                    [r*nb_gores + 1 + g % nb_gores,
                     (r+1)*nb_gores + g,
                     (r+1)*nb_gores + 1 + g % nb_gores]
                )

        self.faces.extend(bottom_faces)


class UVNavball(UVSphere):
    palette = {
        1: (1, 0, 0, 1),
        2: (0, 0, 1, 1),
        3: (0, 1, 0, 1),
        4: (0, 1, 1, 1),
        5: (1, 1, 0, 1),
        6: (1, 1, 1, 1),
        -1: (.5, 0, 0, 1),
        -2: (0, 0, .5, 1),
        -3: (0, .5, 0, 1),
        -4: (0, .5, .5, 1),
        -5: (.5, .5, 0, 1),
        -6: (.5, .5, .5, 1)
    }

    def __init__(self, nb_gores: int = 7, nb_rows: int = 5, pattern: str = 'spiral', density: int = 1) -> None:
        super().__init__(nb_gores, nb_rows)
        self._colorize(nb_gores, pattern, density)

    def _colorize(self, nb_gores: int, pattern: str, density: int):
        n = len(self.faces)
        self.face_colors = []

        # generate different patterns:
        if pattern.lower() == 'beachball':

            for idx in range(len(self.faces)):
                mod = +1 if idx < n//2 else -1

                if idx < nb_gores or idx >= n-nb_gores:
                    key = mod*(1 + idx//density % 2)
                else:
                    key = mod*(1 + idx//density//2 % 2)

                self.face_colors.append(self.palette[key])

        elif pattern.lower() == 'spiral':
            for idx in range(len(self.faces)):
                mod = +1 if idx < n//2 else -1

                if idx < nb_gores or idx >= n-nb_gores:
                    key = mod*(1 + idx//density % 2)
                else:
                    # current ring :
                    r = (idx - nb_gores) // (2 * nb_gores) + 1
                    # advance by one on every ring
                    key = mod * \
                        (1+((((idx-1 + 2*r) % (4*density)) >= (2*density))) % 2)

                self.face_colors.append(self.palette[key])

        elif pattern.lower() == 'checkerboard':
            for idx in range(len(self.faces)):
                mod = +1 if idx < n//2 else -1

                if idx < nb_gores or idx >= n-nb_gores:
                    key = mod*(1 + idx//density % 2)
                else:
                    # current ring :
                    r = ((idx - nb_gores) // (2 * nb_gores) + 1) // density
                    # gore on the current ring
                    g = (idx - nb_gores) % (2 * nb_gores) // density
                    # advance by one on every ring
                    key = mod*(1 + (int(g % 4 > 1) + r) % 2)

                self.face_colors.append(self.palette[key])

        else:
            raise ValueError(f"The pattern {pattern} has not been implemented")


class NavballWidget(GLViewWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # mesh_data = Isocahedron().mesh()
        mesh_data = UVNavball(96, 51, density=12).mesh()
        mesh = GLMeshItem(meshdata=mesh_data,
                          smooth=False,
                          drawFaces=True,
                          #   drawEdges=True,
                          #   edgeColor=(0, 0, 0, 1),
                          )
        self.addItem(mesh)

        self.setCameraPosition(distance=3)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(500, 500)


if __name__ == "__main__":
    import sys

    print(f"running '{__file__.split('/')[-1]}' as Qt App")
    app = QtWidgets.QApplication(sys.argv)

    mw = NavballWidget()
    mw.show()

    sys.exit(app.exec_())
