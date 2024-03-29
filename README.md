# PyQtTest

This is a personal testing ground for trying stuff out, and for working on my `l337 pR0GrAMm1N' 5K1LL5`. As a consequence, things are not documented very well, and some choices may seem suboptimal. 

NOTE: contrary to good common standard, the `test_*.py` files in [`./tests`](./tests/) are not unittest, but rather 'demos', meant for manally testing. I should probably change this.

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
4. [Navball Widget](src/PyQtTest/widgets/hud/navball_pyqtgraph.py) : a 3D ball drawn on a transparent background - could be used to represent the attitude of a vehicle (like in [Kerball Space Programm](https://wiki.kerbalspaceprogram.com/wiki/Navball)). Still a bit rough and needs some work before it's ready. Maybe I'll continue working on it someday -- but today is not that day.
5. [Tape Indicator Flight Instrument](src/PyQtTest/widgets/flight_indicators/tape_indicator.py) : a simple but versatile widget implementing a tape (or drum) indicator, useful for displaying unbounded analog values.
6. [Artificial Horizon Flight Instrument](src/PyQtTest/widgets/flight_indicators/artificial_horizon.py) : a simple artificial horizon widget that comes in two styles: dashboard-style and HUD-style. Can be connected to the laptop orientation sensor for extra fun.
7. [Form Generation](src/PyQtTest/widgets/form_generation/form_generation.py) : parses a JSON or YAML file into a QT Form, and places the output of the form into a JSON/YAML compatible dictionary on request.

## Gallery 

| <img src="https://user-images.githubusercontent.com/62802642/197333006-ad02a63b-d307-41e1-be56-086eb1b38dc5.png" alt="segmentation" /> | <img src="https://user-images.githubusercontent.com/62802642/197334022-e99b31d2-7955-460d-99e4-b572dc2052a8.png" alt="reloading" /> | 
| --- | --- |
| The image segmentation widget (left is input image, right is segmented, labeled & clickable image). | The reloadable widget being used with the image segmentation widget |


| <img src="https://user-images.githubusercontent.com/62802642/197334036-38c4546f-6057-4cd2-89d3-2ef36bdd7ff5.png" alt="stylesheets" /> | <img src="https://user-images.githubusercontent.com/62802642/197332031-8adf8a84-b8e7-4921-890f-9553071f43f6.png" alt="navball" /> |
| --- | --- |
| Messing around with stylesheets is trivial thanks to the reloadable widget! 😄 |  The 3D navball widget on a transparent background. |

| ![tape_vt](https://user-images.githubusercontent.com/62802642/197356883-918362e3-cd59-4c14-a924-085b7f0ee704.png) | ![tape_hz](https://user-images.githubusercontent.com/62802642/197356895-99b10609-b585-4fa8-a1b2-e970ff337dff.png) | ![artificial_hz_opaque](https://user-images.githubusercontent.com/62802642/197356918-000d5345-548a-494d-88c7-ab039b7323dc.png) | ![artificial_hz_HUD](https://user-images.githubusercontent.com/62802642/197356931-af796da6-e24b-4e77-b60d-d89d46c3bd09.png) |
| --- | --- | --- | --- |
| The tape indicator widget being tested in a vertical mode. | The tape indicator widget being tested in a horizontal mode. | The dashboard-style artificial horizon widget being tested. | The HUD-style artificial horizon widget being tested (with a professional looking font!) |
