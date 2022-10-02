#!/usr/bin/env python3
'''
The resource module for the project

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''
import os

# rename the generic file handlers
from .images import get_path_to_file as get_path_to_img

resource_folder = os.sep.join(__file__.replace('/', os.sep).split(os.sep)[:-1])
image_folder = os.sep.join([resource_folder, 'images'])
image_label_folder = os.sep.join([resource_folder, 'image_labels'])
