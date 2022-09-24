#!/usr/bin/env python3
'''
The image resource module for the project

Author  :   Michael Biselx
Date    :   09.2022
Project :   PyQtTest
'''
import os


def list_all_files(ext: 'str | list[str] | None' = None) -> 'dict[str, str]':
    '''
    list all the files in the directory

    parameters : 
    * ext   :   (optional) the extension to filter for

    returns : 
    * files :   a dictionary containing [file-name, path-to-file]
    '''
    files: 'dict[str, str]' = {}

    if ext is not None and not hasattr(ext, '__iter__'):
        ext = [ext]

    here = os.sep.join(__file__.split('/')[:-1])
    for dirpath, _, filenames in os.walk(here):
        for file in filenames:
            if ext is None or any([file.lower().endswith('.'+e) for e in ext]):
                files[file] = os.path.join(dirpath, file)

    return files


def get_path_to_file(file: str) -> str:
    '''
    get the path to a particular file

    parameters : 
    * file  :   the name of the reqested file

    returns : 
    * path-to-file 
    '''
    try:
        return list_all_files()[file]
    except KeyError:
        here = os.sep.join(__file__.split('/')[:-1])
        raise FileNotFoundError(
            f"could not find '{file}' in '{here}'")


if __name__ == '__main__':

    files = list_all_files()

    maxtab = len(max(files, key=len))//5 + 1

    for file, path in files.items():
        tabs = (maxtab - len(file)//5)*'\t'
        print(f"* {file} :{tabs}{path}")
