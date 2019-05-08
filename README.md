![PyPI version](https://ad.vgiscience.org/tagmaps/pypi.svg) ![pylint](https://ad.vgiscience.org/tagmaps/pylint.svg) ![pipeline](https://ad.vgiscience.org/tagmaps/pipeline.svg) ![conda](https://anaconda.org/sieboldianus/tagmaps/badges/version.svg)

# Tag Maps

Spatio-Temporal Tag and Photo Location Clustering for generating Tag Maps

**Tag Maps** are similar to Tag Clouds, but Tag Maps use the spatial information that is attached to geotagged photographs, in addition to tag frequency, to visualize tags on a map.
This Library uses the single-linkage tree that is available from [HDBSCAN](https://github.com/scikit-learn-contrib/hdbscan) to cut trees at a specific user-defined distance for all available tags in the given dataset.
Afterwards, Alpha Shapes are generated as a means to allow 'soft' placement of tags on a map, according to their area of use. Two Shapefiles are generated that can be used to visualize results, for example, in ESRI ArcGIS.

![Tag Map Example](https://ad.vgiscience.org/tagmaps/img6.png?raw=true)

Based on the papers:

> Dunkel, A. (2015). Visualizing the perceived environment using crowdsourced photo geodata. Landscape and Urban Planning, 142. [DOI](http://doi.org/10.1016/j.landurbplan.2015.02.022) / [PDF](http://alexanderdunkel.com/AuthorManuscript_Visualizing%20the%20perceived%20environment.pdf)

> Dunkel, A. (2016). Assessing the perceived environment through crowdsourced spatial photo content for application to the fields of landscape and urban planning. Thesis, TU Dresden Landscape and Environmental Planning. [PDF](http://alexanderdunkel.com/Dissertation_AlexanderDunkel.pdf)

## Installation

1. The easiest way for Windows users is to download the newest pre-compiled build from [releases](../../releases) and run `tagmaps.exe`
2. For all other OS, the recommended way is to install with `pip install tagmaps`
3. For devs, if conda package manager is available, use `conda env create -f environment.yml`

## Quickstart

1. Place geotagged data in `/01_Input` subfolder
   - example data is available in the pre-compiled build zip-file above
2. Output files will be saved in `/02_Output` (2 shapefiles in auto-selected UTM projection, one containing all tag cluster and one with the overall location clusters)
3. Visualize shapefiles, e.g. using ESRI ArcGIS (I haven't tried other GIS Software such as QGIS, but it should theoretically be possible..)
   - download `BasemapLayout_World.mxd` from [resources folder](/resources/BasemapLayout_World.mxd) and replace missing links with 2 resulting Shapefiles in `/02_Output`
   - adjust minimum and maximum Font Sizes, Weighting Formula or other metrics to your needs.

**Some background**:

Tag Maps Package can be used with any tagged & spatially referenced data, but it has been specifically deveoped with Social Media data in mind (Flickr, Twitter etc.).
There're two ways to feed input data:

1. Unfiltered raw data
   - Use `tagmaps.add_record(record)` where record is of type `PostStructure` (see [shared_structure.py](/classes/shared_structure.py))
   - How you clean up data totally depends on the type, have a look at LoadData class in [load_data.py](/classes/load_data.py) for Twitter and Flickr cleanup
2. Filtered data
   - the result from 1 is a `UserPostLocation` (**UPL**), which is a reference of type 'CleanedPost'. A UPL simply has all posts of a single user at a single coordinate merged,
     e.g. a reduced list of terms, tags and emoji based on global occurrence (i.e. no duplicates).
   - there're other metrics used throughout the package:
     - **UPL** - User post location
     - **UC** - User count
     - **PC** - Post count
     - **PTC** - Total tag count ("Post Tag Count")
     - **PEC** - Total emoji count
     - **UD** - User days (counting distinct users per day)
     - **DTC** - Total distinct tags
     - **DEC** - Total distinct emoji
     - **DLC** - Total distinct locations
3. The filtered data that is used for tagmaps can be exported using `tagmaps.write_cleaned_data()`.
   Since this will remove all terms/tags/emoji that do not appear in the top 1000 (e.g.) occurring global list of terms,
   this will produce a highly pseudo-anonymized set of information, with only collectively relevant terms remaining.
   The default value (1000) can be adjusted using `max_items` arg, e.g. the smaller max_items, the higher is the effect of anonymization/generalization.

## Tutorial

There's a tutorial available [here](https://ad.vgiscience.org/tagmaps_tutorial) that guides though the process of generating Tag Maps.
Please bring your own data or use a sample from the [YFCC100M Flickr Commons Dataset](https://multimediacommons.wordpress.com/yfcc100m-core-dataset/).

## Code

The code has been completely refactored in January 2019, but there are still some missing pieces.
Particularly the API (that is: `import tagmaps`) is still in an early stage. See method main() in [**main**.py](/tagmaps/__main__.py)
for examples on how to use tag maps package.

## Resources

- Check out [this album on Flickr](https://www.flickr.com/photos/64974314@N08/albums/72157628868173205) with some more Tag Maps examples
- There's also an semi-interactive interface to explore some Tag Maps [here](http://maps.alexanderdunkel.com/)
- Check out my blog [here](http://blog.alexanderdunkel.com/) with some background information
- A [Jekyll-Reveal presentation](https://ad.vgiscience.org/tagmaps_intro/) on theory & background

## Contributors

Some future goals:

- include topic modeling
- improve automatic detection of general vs specific tags for an area
- include mapping/visualization step (replace ArcGIS)

## Built With

This project includes and makes use of several other projects/libraries/frameworks:

> [_Alpha Shapes_](http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/) Kevin Dwyer/ Sean Gillies  
> Generating Concave Hull for Point Clouds

> [_HDBSCAN_](https://github.com/scikit-learn-contrib/hdbscan) McInnes, J. Healy, S. Astels - BSD licensed  
> A high performance implementation of HDBSCAN clustering.

> [_Shapely_](https://github.com/Toblerity/Shapely)  
> Manipulation and analysis of geometric objects

> [_SciPy and Convex Hull_](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html#scipy.spatial.ConvexHull)  
> Simple shapes for point clusters are generated using SciPy's excellent Convex Hull functions

> [_Fiona_](https://github.com/Toblerity/Fiona)  
> OGR's neat and nimble API for Python programmers.

## License

GNU GPLv3

## Changelog & Download

2019-05-08: TagMaps v.0.17.5

- as of this version, tagmaps package is available on Anaconda Cloud

2019-03-08: [**TagMaps v0.17.4**](https://cloudstore.zih.tu-dresden.de/index.php/s/AcfL5ZkRhPas0O4/download)

- First version of public API, e.g. load tagmaps to other packages with `import tagmaps` or `from tagmaps import TagMaps`
- Refactor of LoadData and PrepareData in separate classes, use of contextmanager/ pipeline generator
- Improved generation of Alpha Shapes
- Basic system integration test pipeline
- Jupyter Notebook compatibility

2019-01-23: [**TagMaps v0.11.1**](https://cloudstore.zih.tu-dresden.de/index.php/s/QhKT3Pj9fk4H9ns/download)

- complete refactor of code with improved encapsulation, code now largely follows PEP conventions
- bugfix: emoji handling now accurately recognizes grapheme clusters consisting of multiple unicode codepoints.
- interface: add feature to filter based on toplists for tags, emoji and locations
- added sample CC-BY dataset

2018-01-31: [**TagMaps v0.9.2**](https://cloudstore.zih.tu-dresden.de/index.php/s/8EFfeJcpNCStQ9X/download)

- Because Tag Maps can be generated from local to regional to continental scale, finding an algorythm that fits all was not straight forward. The current implementation will produce shapes for all of these scales without any user input.
- This Final Alpha Shape Implementation is motivated from [Kevin Dwyer/ Sean Gillies](http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/) great base code
- Implementation of Auto-Projection from Geographic to Projected Coordinate System. The code will select the most suitable UTM Zone for projecting data.

2018-01-17: **TagMaps v0.9.1**

- First build
- Initial commit, still lots of unnecessary comments/code parts left in code

[//]: # "Readme formatting based on https://gist.github.com/PurpleBooth/109311bb0361f32d87a2"
