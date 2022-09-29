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


# define some colors
red = ColorRGBA(255, 000, 000)
gold = ColorRGBA(255, 215, 000)
lime = ColorRGBA(000, 255, 000)
green = ColorRGBA(000, 180, 000)
turquoise = ColorRGBA(000, 215, 255)
blue = ColorRGBA(000, 000, 255)
purple = ColorRGBA(160, 000, 215)
magenta = ColorRGBA(255, 000, 255)
white = ColorRGBA(255, 255, 255)
gray = ColorRGBA(90, 90, 90)
black = ColorRGBA(0, 0, 0)
transparent = ColorRGBA(0, 0, 0, 0)


class ColorIterator():
    '''automatically iterate though colors'''
    colors = [red, gold, lime, green, blue, purple]

    def __init__(self) -> None:
        self.i = -1

    def reset(self) -> None:
        self.i = -1

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
