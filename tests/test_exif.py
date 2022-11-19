#!/usr/bin/env python3
'''
A file used for testing

Author  :   Michael Biselx
Date    :   10.2022
Project :   PyQtTest
'''
import os
import numpy as np
import logging
import typing

from PIL import Image, ExifTags
from PyQtTest.resources import get_path_to_img


class DataTypes:
    class DataType:
        size: int = 0

        @staticmethod
        def convert(bytestr: bytes, byteorder: str) -> 'int | float | str':
            return None

    class UnsignedByte:
        size: int = 1

        @staticmethod
        def convert(bytestr: bytes, byteorder) -> int:
            return int.from_bytes(bytestr, byteorder, signed=False)

    class ASCII:
        size: int = 1

        @staticmethod
        def convert(bytestr: bytes, byteorder) -> str:
            return bytestr.decode('ascii', 'ignore')

    class UnsignedShort(UnsignedByte):
        size: int = 2

    class UnsignedLong(UnsignedByte):
        size: int = 4

    class UnsignedRational:
        size: int = 8

        @staticmethod
        def convert(bytestr: bytes, byteorder) -> float:
            num = int.from_bytes(bytestr[:4], byteorder, signed=False)
            den = int.from_bytes(bytestr[4:], byteorder, signed=False)
            return num/den

    class SignedByte:
        size: int = 1

    class SignedShort:
        size: int = 2

    class SignedLong:
        size: int = 4

    class SignedRational:
        size: int = 8

    class Float:
        size: int = 4

    class Double:
        size: int = 8


class ExifParser:

    type_lookup: 'list[DataTypes.DataType]' = [
        None,
        DataTypes.UnsignedByte,
        DataTypes.ASCII,
        DataTypes.UnsignedShort,
        DataTypes.UnsignedLong,
        DataTypes.UnsignedRational,
        DataTypes.SignedByte,
        None,
        DataTypes.SignedShort,
        DataTypes.SignedLong,
        DataTypes.SignedRational,
        DataTypes.Float,
        DataTypes.Double,
    ]

    def __init__(self) -> None:
        self.ptr = 0
        self.exif: bytes
        self.byteorder: str

    def parse_entry(self, entry: bytes, entry_ptr: int, data_ptr: int) -> 'tuple[int, type[DataTypes.DataType], int|float|str]':
        if len(entry) != 12:
            raise ValueError(
                f"bad entry length. expected 12, got {len(entry)}")
        tag = DataTypes.UnsignedShort.convert(entry[:2], self.byteorder)
        dtype = self.type_lookup[DataTypes.UnsignedShort.convert(
            entry[2:4], self.byteorder)]
        count = DataTypes.UnsignedShort.convert(entry[4:8], self.byteorder)
        if dtype.size * count > 4:
            offset = DataTypes.UnsignedLong.convert(entry[8:], self.byteorder)
            data = dtype.convert(
                self.exif[self.ptr+offset: self.ptr+offset+dtype.size*count], self.byteorder)
            logging.debug(
                f"tag: {ExifTags.TAGS[tag]} ({tag}) - "
                f"type: {dtype.__name__} - "
                f"data location : {offset} - "
                f"with data: {data}")
        else:
            data = dtype.convert(entry[8:], self.byteorder)
            logging.debug(
                f"tag: {ExifTags.TAGS[tag]} ({tag}) - "
                f"type: {dtype.__name__} - "
                f"value: {data}")
        return tag, dtype, data

    def parse_exif(self, exif: bytes):
        self.ptr = 0
        self.exif = exif
        if exif.startswith(b'Exif\00\00'):  # skip Adobe Exif signature
            self.ptr += 6

        byte_reference = self.ptr

        self.byteorder = 'big' if exif[self.ptr: self.ptr +
                                       2] == b'MM' else 'little'
        logging.debug(f"using {self.byteorder}-endian")

        big_tiff = int.from_bytes(
            exif[self.ptr+2: self.ptr+4], self.byteorder) > 42
        logging.debug(f"using {'Big' if big_tiff else 'normal'} TIFF")

        if big_tiff:
            offset = int.from_bytes(
                exif[self.ptr+4: self.ptr+12], self.byteorder)
            raise NotImplementedError("BifTIFF")
        else:
            offset = int.from_bytes(
                exif[self.ptr+4: self.ptr+8], self.byteorder)
        logging.debug(f"offset to first tag is {offset} bytes")

        # parse Image File Directory
        idf_ptr = byte_reference+offset
        nb_entries = DataTypes.UnsignedShort.convert(
            exif[idf_ptr:idf_ptr+2], self.byteorder)
        logging.debug(f"there are {nb_entries} entries in this IFD")

        # parse entries
        for i in range(nb_entries):
            entry_ptr = idf_ptr + 2 + 12*i
            tag, type, data = self.parse_entry(
                entry=exif[entry_ptr:entry_ptr+12])


if __name__ == '__main__':
    print(f"running '{__file__.split('/')[-1]}'")

    data_folder = os.sep.join([*__file__.split('/')[:-1], 'data'])
    # img = Image.open(os.sep.join(
    #     [data_folder, '2022-11-15-22-22-21_webcam.jpg']))
    # img = Image.open(os.sep.join(
    #     [data_folder, 'exif_test.jpg']))
    img = Image.open(os.sep.join(
        [data_folder, '2022_11_15_17_30_38_capture_with_raw.jpeg']))

    # img_exif = dict((ExifTags.TAGS[key] if key in ExifTags.TAGS else key, val)
    #                 for key, val in img.getexif().items())
    # print(*img_exif.items(), sep='\n')

    # print(img.info['exif'])
    logging.basicConfig(level=logging.DEBUG)

    ExifParser().parse_exif(img.info['exif'])
