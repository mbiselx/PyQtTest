#!/usr/bin/env python3
'''
A module containing different utility widgets for quick prototyping

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''


class ColorIterator():
    '''automatically iterate though colors'''
    colors = [(255, 255, 255),  # white
              (255, 000, 000),  # red
              (255, 215, 000),  # gold
              (000, 255, 000),  # lime
              (000, 255, 215),  # forest
              (000, 000, 255),  # blue
              (215, 000, 255),  # purple
              ]

    def __init__(self) -> None:
        self.i = 0

    def reset(self):
        self.i = 0

    def __iter__(self) -> None:
        '''iterator to run though all available colors'''
        return self.colors

    def __next__(self) -> 'tuple[int, int, int]':
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
