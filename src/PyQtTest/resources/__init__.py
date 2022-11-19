#!/usr/bin/env python3
'''
The resource module for the project

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''
from os import sep as __separator

# rename the generic file handlers
from .images import get_path_to_file as get_path_to_img
from .stylesheets import get_path_to_file as get_path_to_stylesheet
from .templates import get_path_to_file as get_path_to_template

# the resources directory
resource_folder = __separator.join(__file__.replace(
    '/', __separator).split(__separator)[:-1])

# the resource sub-directories
image_folder = __separator.join([resource_folder, 'images'])
image_label_folder = __separator.join([resource_folder, 'image_labels'])
stylesheet_folder = __separator.join([resource_folder, 'stylesheets'])
template_folder = __separator.join([resource_folder, 'templates'])
