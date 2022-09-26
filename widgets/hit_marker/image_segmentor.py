#!/usr/bin/env python3
'''
A submodule for segmenting a jpg image

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''

import cv2
import numpy as np

try:
    from ..resources import get_path_to_img
except:  # for the demo
    from sys import path
    from os.path import dirname
    path.append(dirname(dirname(path[0])))
    from widgets.resources import get_path_to_img


def segment_image(img_path) -> 'tuple[int, np.ndarray]':
    '''
    takes a dark image on bright background

    @parameters:
    * `img_path` : path to the image file

    @returns :
    * `(nb_lbls, labels)` : the number of labels in the image,
            as well as the labeled image
    '''

    # get image in grayscale
    img_g = cv2.cvtColor(cv2.imread(img_path),
                         cv2.COLOR_BGR2GRAY)

    # binarize
    _, img_b = cv2.threshold(img_g, 0, 255,
                             cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # segment
    return cv2.connectedComponents(~img_b, ltype=cv2.CV_16U)


def color_image_by_segments(labels: np.ndarray, color_dict: 'dict[int, tuple[int, int, int, int]]') -> np.ndarray:
    '''
    colors an image based on given labels

    @parameters : 
    * `labels`: the labeled image
    * `color_dict` : a dictionary containing the colors by label

    @returns :
    * `img` : the colorized image
    '''
    img = np.zeros((*labels.shape, 4), dtype=np.uint8)

    for label, color in color_dict.items():
        img[np.where(labels == label)] = color if len(
            color) == 4 else (*color, 255)

    return cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)


############################################
#  DEMO
############################################

if __name__ == '__main__':

    n_lbls, labels = segment_image(get_path_to_img('car.jpg'))

    from widgets.plotting.utils import ColorIterator
    cs = dict(zip(range(0, n_lbls), ColorIterator().__iter__()))

    img_out = color_image_by_segments(labels, cs)

    cv2.imshow('demo', img_out)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
