Tag Maps
=============
Spatio-Temporal Tag and Photo Location Clustering for generating Tag Maps

**Tag Maps** are similar to Tag Clouds, but Tag Maps use the spatial information that is attached to geotagged photographs, in addition to tag frequency, to visualize tags on a map.
This Library uses the single-linkage tree that is available from [HDBSCAN](https://github.com/scikit-learn-contrib/hdbscan) to cut trees at a specific user-defined distance for all available tags in the given dataset. 
Afterwards, Alpha Shapes are generated as a means to 'soft' placement of tags on a map, according to their area of use. Two Shapefiles are generated that can be used to visualize maps, for example, in ArcGIS. 

```diff
- Please be advised: This repository contains, in its current form, 
- Python code that is very difficult to read or contribute to. 
- I intend to put more work into structuring code ...as soon as more time is available.
```

![Tag Map Example](/resources/img6.png?raw=true)

## Installation

1. The easiest way for Windows users is to download the Pre-compiled build that is available [here](https://cloudstore.zih.tu-dresden.de/index.php/s/8EFfeJcpNCStQ9X/download) (315MB!) and run `generateTagClusters.exe`
    - you can also compile the program yourself using the `setup.py` with [cx_Freeze](https://anthony-tuininga.github.io/cx_Freeze/): run `python cx_setup.py build`
    - or simple run `generateTagClusters.py` if you have Python and all dependencies installed
2. Place geotagged photo data in `/01_Input` subfolder
    - example files/format are available in the Pre-compiled build zip-file above
3. Output files will be saved in `/02_Output` (2 Shapefiles in WGS1984 projection, one containing all Tag Cluster and one with the Photo Location Clusters)
4. Visualize Shapefiles using ArcGIS (I haven't tried other GIS Software such as QGIS, but it should theoretically be possible..)
    - download `BasemapLayout_World.mxd` from [resources folder](/resources/BasemapLayout_World.mxd) and replace missing links with 2 resulting Shapefiles in `/02_Output`
    - adjust minimum and maximum Font Sizes, Weighting Formula or other metrics to your needs. There are two Power Point files available which explain the complete process: [Tag Clustering](/resources/01_TagMaps.pptx) and [Photo Location Clustering](/resources/02_PhotoDensityMaps.pptx)

## Code

At the moment, the code is pretty messy. I wrote this in less than a week, without any other contributors in mind. I will work on this when there's more time available..

## Resources

* Check out [this album on Flickr](https://www.flickr.com/photos/64974314@N08/albums/72157628868173205) with some more Tag Maps examples 
* There's also an semi-interactive interface to explore some Tag Maps [here](http://maps.alexanderdunkel.com/)
* Check out my blog [here](http://blog.alexanderdunkel.com/) with some background information


## Contributors

* todo: future goals, extending scope of program beyond Flickr photo data (include Twitter & Instagram, for example)

## Built With
This project includes and makes use of several other projects/libraries/frameworks:

>[*Alpha Shapes*](http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/) Kevin Dwyer/ Sean Gillies
>>Generating Concave Hull for Point Clouds

>[*HDBSCAN*](https://github.com/scikit-learn-contrib/hdbscan) McInnes, J. Healy, S. Astels - BSD licensed
>> A high performance implementation of HDBSCAN clustering.

>[*Shapely*](https://github.com/Toblerity/Shapely)
>> Manipulation and analysis of geometric objects

>[*SciPy and Convex Hull*](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html#scipy.spatial.ConvexHull)
>> Simple shapes for point clusters are generated using SciPy's excellent Convex Hull functions  

## License

GNU GPLv3

## Changelog & Download

2018-01-31: [**TagMaps v0.9.2**](https://cloudstore.zih.tu-dresden.de/index.php/s/8EFfeJcpNCStQ9X/download)

* Because Tag Maps can be generated from local to regional to continental scale, finding an algorythm that fits all was not straight forward. The current implementation will produce shapes for all of these scales without any user input.
* This Final Alpha Shape Implementation is motivated from [Kevin Dwyer/ Sean Gillies](http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/) great base code
* Implementation of Auto-Projection from Geographic to Projected Coordinate System. The code will select the most suitable UTM Zone for projecting data.

2018-01-17: **TagMaps v0.9.1**

* First build
* Initial commit, still lots of unnecessary comments/code parts left in code

[//]: # (Readme formatting based on https://gist.github.com/PurpleBooth/109311bb0361f32d87a2) 
