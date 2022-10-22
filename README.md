# PyQtTest

This is a personal testing ground for trying stuff out, and for working on my `l337 pR0GrAMm1N' 5K1LL5`. As a consequence, things are not documented very well, and some choices may seem suboptimal. 

## Installing 

The module is organized as an installable package, mostly so I could test making and installable package - but also because it's nice to be able to `import PyQtTest` from anywhere. 
It can be installed locally by running the following in the root folder : 
```bash
pip install -e . 
```
The `-e` flag is used to make the package 'editable'.


## Items of Note

1. [Resource Manager](src/PyQtTest/resources/images/__init__.py) : access module resources easily
2. [Image Segmenting](src/PyQtTest/widgets/hit_marker/image_segmentor.py) : break and image down into segments and colorize an image by segment. The segments can also be labled.
3. [Reloadable Widgets](src/PyQtTest/widgets/utils/reloadable_widget.py) : reload a widget from source at runtime - useful for *very* rapid prototyping. Also allows the quick reloading of the Qt stylesheet. 
4. [Navball Widget](src/PyQtTest/widgets/hud/navball_pyqtgraph.py) : a 3D ball drawn on a transparent background - could be used to represent the attitude of a vehicle (like in [Kerball Space Programm](https://wiki.kerbalspaceprogram.com/wiki/Navball)). Still a bit rough and needs some work before it's ready.


## Gallery 

| <img src="https://user-images.githubusercontent.com/62802642/197333006-ad02a63b-d307-41e1-be56-086eb1b38dc5.png" alt="segmentation" /> | <img src="https://user-images.githubusercontent.com/62802642/197334022-e99b31d2-7955-460d-99e4-b572dc2052a8.png" alt="reloading" /> | 
| --- | --- |
| The image segmentation widget (left is input image, right is segmented, labeled & clickable image). | The reloadable widget being used with the image segmentation widget |


| <img src="https://user-images.githubusercontent.com/62802642/197334036-38c4546f-6057-4cd2-89d3-2ef36bdd7ff5.png" alt="stylesheets" /> | <img src="https://user-images.githubusercontent.com/62802642/197332031-8adf8a84-b8e7-4921-890f-9553071f43f6.png" alt="navball" /> |
| --- | --- |
| Messing around with stylesheets is trivial thanks to the reloadable widget! 😄 |  The 3D navball widget on a transparent background. |

