#!/usr/bin/env python3
'''
A module containing different utility widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''


class ColorRGBA(tuple):
    '''a class for handling color-related stuff'''

    def __new__(cls, r: int, g: int, b: int, a=255) -> 'ColorRGBA':
        try:
            self = tuple.__new__(cls, (int(r), int(g), int(b), int(a)))
        except ValueError:
            raise TypeError("ColorRGBA colors must be integers") from None
        for c in self:
            if not (0 <= c <= 255):
                raise ValueError("ColorRGBA colors must be 0 <= c <= 255")
        return self

    @property
    def r(self) -> int: return self[0]
    @property
    def g(self) -> int: return self[1]
    @property
    def b(self) -> int: return self[2]
    @property
    def a(self) -> int: return self[3]


class ColorIterator():
    '''automatically iterate though colors'''
    colors = [ColorRGBA(255, 255, 255),  # white
              ColorRGBA(255, 000, 000),  # red
              ColorRGBA(255, 215, 000),  # gold
              ColorRGBA(000, 255, 000),  # lime
              ColorRGBA(000, 255, 215),  # forest
              ColorRGBA(000, 000, 255),  # blue
              ColorRGBA(215, 000, 255),  # purple
              ]

    def __init__(self) -> None:
        self.i = 0

    def reset(self):
        self.i = 0

    def __iter__(self) -> None:
        '''iterator to run though all available colors'''
        return self.colors

    def __next__(self) -> ColorRGBA:
        '''get the next color in a loop, as follows:

        ```
        ci = ColorIterator()
        color1 = next(ci)
        color2 = next(ci)
        ...
        ```
        '''
        self.i = self.i + 1 if self.i < len(self.colors)-1 else 0
        return self.colors[self.i]
