[![PyPI version](https://ad.vgiscience.org/tagmaps/pypi.svg)](https://pypi.org/project/tagmaps/) [![pylint](https://ad.vgiscience.org/tagmaps/pylint.svg)](https://github.com/Sieboldianus/TagMaps) [![pipeline](https://gitlab.vgiscience.de/ad/tagmaps/badges/master/pipeline.svg)](https://github.com/Sieboldianus/TagMaps) [![Conda Version](https://img.shields.io/conda/vn/conda-forge/tagmaps.svg)](https://anaconda.org/conda-forge/tagmaps) [![Conda Pipeline](https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/tagmaps-feedstock?branchName=master)](https://dev.azure.com/conda-forge/feedstock-builds/_build?definitionId=6736&_a=summary) [![Documentation](https://ad.vgiscience.org/tagmaps/documentation.svg)](https://ad.vgiscience.org/tagmaps/docs/)


# Tag Maps

Spatio-Temporal Tag and Photo Location Clustering for generating Tag Maps

**Tag Maps** are similar to Tag Clouds, but Tag Maps use the spatial information that is attached to geotagged photographs, in addition to tag frequency, to visualize tags on a map.
This library uses the single-linkage tree that is available from [HDBSCAN](https://github.com/scikit-learn-contrib/hdbscan) to cut trees at a specific, automatic or user-defined distance for all available tags in the given dataset.
Afterwards, alpha shapes are generated as a means to allow 'soft' placement of tags on a map, according to their area of use. Two shapefiles are generated that can be used to visualize results, for example, in ESRI ArcGIS or Mapnik.

![Tag Map Example](https://ad.vgiscience.org/tagmaps/img6.png?raw=true)

Based on the papers:

> Dunkel, A. (2015). Visualizing the perceived environment using crowdsourced photo geodata. Landscape and Urban Planning, 142. [DOI](http://doi.org/10.1016/j.landurbplan.2015.02.022) / [PDF](http://alexanderdunkel.com/AuthorManuscript_Visualizing%20the%20perceived%20environment.pdf)

> Dunkel, A. (2016). Assessing the perceived environment through crowdsourced spatial photo content for application to the fields of landscape and urban planning. Thesis, TU Dresden Landscape and Environmental Planning. [DOI](https://nbn-resolving.org/urn:nbn:de:bsz:14-qucosa-207927) / [PDF](http://alexanderdunkel.com/Dissertation_AlexanderDunkel.pdf)

> Dunkel, A. (2020). Tag Maps in der Landschaftsplanung. In book: Handbuch Methoden Visueller Kommunikation in der Räumlichen Planung. [DOI](https://doi.org/10.1007/978-3-658-29862-3_8)

Overview of processing steps (Toronto High Park example):

* **a)** individual photo locations (raw data)
* **b)** photo locations combined to clusters
* **c)** tag location clustering (HDBSCAN) and alpha-shape generation
* **d)** soft placement of all relevant tag clusters using alpha shapes

![Tag Map Example](https://ad.vgiscience.org/tagmaps/tagmaps_steps.png?raw=true)

The label placement based on descending importance is currently implemented in [ArcGIS](https://ad.vgiscience.org/tagmaps/docs/user-guide/tutorial/#arcmap) and [Mapnik](https://ad.vgiscience.org/tagmaps/docs/user-guide/mapnik/). See the folder [resources](resources/) for information regarding ArcGIS and a [Jupyter Notebook for Mapnik](https://ad.vgiscience.org/tagmaps-mapnik-jupyter/01_mapnik-tagmaps.html). [The following animation](https://wwwpub.zih.tu-dresden.de/~s7398234/map_000_4k.webm) illustrates the ArcMap label placement algorithm for the TU Dresden Campus.

![Label Placement Example](resources/label_placement.gif?raw=true)

## Installation

The recommended way to install the package is with `conda install tagmaps -c conda-forge`.

For a detailed guide to setup tagmaps package in Windows 10, see the [documentation](https://ad.vgiscience.org/tagmaps/docs/user-guide/installation/) .

## Documentation

See the [tagmaps documentation](https://ad.vgiscience.org/tagmaps/docs/) for additional information, guides and tutorials. There is also an external [API reference](https://ad.vgiscience.org/tagmaps/docs/api/tagmaps_.html) available.

## Quickstart

1. Clone `resources` folder somewhere locally
   - `git clone https://github.com/Sieboldianus/TagMaps.git && cd TagMaps && git filter-branch --subdirectory-filter resources`
2. Place geotagged data in `/01_Input` sub-folder
   - information on how to structure data is available in the [documentation](https://ad.vgiscience.org/tagmaps/docs/user-guide/use-your-own-data/)
3. Run `tagmaps` within folder `resources`. Output files will be saved to `/02_Output`
   - 2 shapefiles in auto-selected UTM projection, one containing all tag cluster and one with the overall location clusters
3. Visualize shapefiles, e.g. using ESRI ArcGIS
   - download `BasemapLayout_World.mxd` from [resources folder](/resources/) and replace missing links with 2 resulting shape-files in `/02_Output`
   - adjust minimum and maximum font sizes, weighting formula or other metrics to your needs.

**Some background**:

Tag Maps package can be used with any tagged & spatially referenced data, but it has been specifically developed with Social Media data in mind (Flickr, Twitter etc.).
There are two ways to load input data:

1. Unfiltered raw data
   - Use `tagmaps.add_record(record)` where record is of type `PostStructure` (see [shared_structure.py](src/tagmaps/classes/shared_structure.py))
   - How you clean up data totally depends on the type, have a look at LoadData class in [load_data.py](src/tagmaps/classes/load_data.py) for Twitter and  Flickr cleanup
2. Filtered data
   - the result from 1 is a `UserPostLocation` (UPL), which is a reference of type 'CleanedPost'. A UPL means that all posts of a single user at a single coordinate are merged,
     e.g. a reduced list of terms, tags and emoji based on global occurrence (i.e. no duplicates).

3. The filtered data that is used for tagmaps can be exported using `tagmaps.write_cleaned_data()`.
   Since this will remove all terms/tags/emoji that do not appear in the top 1000 (e.g.) occurring global list of terms,
   this will produce a highly pseudonymized set of information, with only collectively relevant terms remaining.
   The default value (1000) can be adjusted using the `max_items` argument, e.g. the smaller max_items, the higher is the effect of anonymization/generalization.

## Code

The code has been completely refactored in January 2019, but there are still some missing pieces.
Particularly the API (that is: `import tagmaps`) is still in an early stage. See method main() in [**main**.py](src/tagmaps/__main__.py)
for examples on how to use tag maps package.

## Resources

- Check out [this album on Flickr](https://www.flickr.com/photos/64974314@N08/albums/72157628868173205) with some more Tag Maps examples
- There's also an semi-interactive interface to explore some Tag Maps [here](http://maps.alexanderdunkel.com/)
- Check out my blog [here](http://blog.alexanderdunkel.com/) with some background information
- A [Jekyll-Reveal presentation](https://ad.vgiscience.org/tagmaps_intro/) on theory & background

## Contributors

Some future goals:

- include topic modeling
- improve automatic detection of general vs specific tags for an area (e.g. chi square)
- improve unit testing (pytest) for tagmaps package
- move from tkinter interface to browser based solution

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

> [_Mapnik_](https://mapnik.org/)
> Mapnik combines pixel-perfect image output with lightning-fast cartographic algorithms, backing OpenStreetMap

## License

GNU GPLv3

## Changelog & Download

This is a high-level summary of version progress. See [CHANGELOG.md](CHANGELOG.md) for a full list of changes.

2022-05-10: **TagMaps v0.22.0**

- the project has finally migrated to a `pyproject.toml`-only based packaging system, as described in the [declarative config (pyproject.toml)](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
- the code structure now follows the [src-layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout).
- fiona was pinned to `1.8.22` in conda until [#213](https://github.com/conda-forge/fiona-feedstock/issues/213) (Windows installations only) is solved

2022-07-27: **TagMaps v0.21.0**

- Add export to Mapnik ([`9db0d0d`](https://github.com/Sieboldianus/TagMaps/commit/9db0d0dc0a266f9eef7c3aac5bf663337c096f80)), enable with `--mapnik_export`
- See a [jupyter lab notebook](https://ad.vgiscience.org/tagmaps-mapnik-jupyter/01_mapnik-tagmaps.html) that illustrates visualization of tag map data in [Mapnik](https://mapnik.org/)

2021-02-22: **TagMaps v0.20.10**

- fix emoji grapheme detection issue with `emoji>=1.01`
- several fixes in cx-freeze build, re-compile with python 3.9

2020-01-24: **TagMaps v0.20.4**

- mainly improvements of type annotations and code legibility
- include type hints in [api-docs](https://ad.vgiscience.org/tagmaps/docs/api/tagmaps_.html)
- migration from namedtuples to (awesome) new dataclass from Python 3.7
(this is the minimum requirement from v0.20.2 onwards)
- fix projection resulting in flipped geometries for pyproj>2.0.0
- fix various other small bugs

2019-05-08: **TagMaps v0.17.6**

- as of this version, tagmaps package is available on [conda-forge](<https://anaconda.org/conda-forge/tagmaps>)
- fixed a bug with newer versions of pyproj (>2.0.0) that would result in very slow projection performance

2019-03-08: **TagMaps v0.17.4**

- First version of public API, e.g. load tagmaps to other packages with `import tagmaps` or `from tagmaps import TagMaps`
- Refactor of LoadData and PrepareData in separate classes, use of contextmanager/ pipeline generator
- Improved generation of Alpha Shapes
- Basic system integration test pipeline
- Jupyter Notebook compatibility

2019-01-23: **TagMaps v0.11.1**

- complete refactor of code with improved encapsulation, code now largely follows PEP conventions
- bugfix: emoji handling now accurately recognizes grapheme clusters consisting of multiple unicode codepoints.
- interface: add feature to filter based on toplists for tags, emoji and locations
- added sample CC-BY dataset

2018-01-31: **TagMaps v0.9.2**

- because Tag Maps can be generated from local to regional to continental scale, finding an algorithm that fits all was not straight forward. The current implementation will produce shapes for all of these scales without any user input.
- this alpha shape implementation is motivated from [Kevin Dwyer/ Sean Gillies](http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/) great base code
- auto-projection from geographic to projected Coordinate System: select the most suitable UTM Zone for projecting data.

2018-01-17: **TagMaps v0.9.1**

- first build with python
- initial commit, still lots of unnecessary comments/code parts left in code

2010-03-30: **TagMaps v0.0.1**

- first implementation of tagmaps concept in ArcGIS Model Builder

[//]: # "Readme formatting based on https://gist.github.com/PurpleBooth/109311bb0361f32d87a2"
