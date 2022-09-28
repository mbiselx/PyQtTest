#!/usr/bin/env python3
'''
The widgets module contains all the widgets for the project

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

__all__ = [
    'WidgetMaker',  # this is a generically useful widget, and should be avaibale from here

    # submodules
    'utils',
    'resources',
    'hud'
]

from .utils.utility_widgets import WidgetMaker
