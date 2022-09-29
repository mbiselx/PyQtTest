# PyQtTest

This is a personal testing ground for trying stuff out, and for working on my `l337 pR0GrAMm1N' 5K1LL5`. As a consequence, things are not documented very well, and some choices may seem suboptimal. 

## Installing 

The module is organized as an installable package, mostly so I could test making and installable package - but also because it's nice to be able to `import PyQtTest` from anywhere. 
It can be installed locally by running the following in the root folder : 
```bash
pip install -e . 
```
The `-e` flag is used to make the package 'editable'.


## Items of Intrest

1. [Resource Manager](src/PyQtTest/resources/images/__init__.py) : access module resources easily
2. [Image Segmenting](src/PyQtTest/widgets/hit_marker/image_segmentor.py) : break and image down into segments and colorize an image by segment
3. [Reloadable Widgets](src/PyQtTest/widgets/utils/reloadable_widget.py) : reload a widget from source at runtime - useful for *very* rapid prototyping