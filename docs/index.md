![](https://ad.vgiscience.org/links/imgs/2019-05-23_emojimap_campus.png)

Spatio-Temporal Tag and Photo Location Clustering for generating Tag Maps

**Tag Maps** are similar to Tag Clouds, but Tag Maps use the spatial information that is attached to geotagged photographs, in addition to tag frequency, to visualize tags on a map.
This Library uses the single-linkage tree that is available from [HDBSCAN](https://github.com/scikit-learn-contrib/hdbscan) to cut trees at a specific, automatic or user-defined distance for all available tags in the given dataset.
Afterwards, Alpha Shapes are generated as a means to allow 'soft' placement of tags on a map, according to their area of use. Two Shapefiles are generated that can be used to visualize results, for example, in ESRI ArcGIS.