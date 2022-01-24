## Resources

This folder contains additonal resources and layout files for creating Tagmaps.

### ArcGIS/ArcPro visualization templates

Templates for visualizing clustered data with ESRI ArcMap/ArcPro.

Note: I am not a big fan of ESRI, but so far, the visualization of labels for tagmaps
has only implemented in ArcGIS/ArcPro.

The `*.mxd` ArcMap and `*.aprx` ArcProject files contain prepared label
expressions to visualize clustered tagmap data, which is customized to the output 
shapefiles produces by this Python package.

See additional information in the [docs](https://ad.vgiscience.org/tagmaps/docs/user-guide/tutorial/#arcmap).

### Additional data

The folder `00_Config` contains default column mappings for CSV files, used in the 
tagmaps package.

The folder `01_Input` contains a sample data file with pseudonymized Creative Commons Flickr images,
which can be used to test the tagmaps package.

### Notes for using `*.mxd` and `*.aprx` files

**Fix missing data source:**

1. Open these files and go to Layer Properties (Layers `HImp`, `Other`, `Top10`)
2. Under Tab Source, select "Set Data Source" 
3. Point it to the output shapefile from the tagmaps python package (`allTagCluster.shp`)

Do not select "Repair Data Source", this will remove any prepared layer symbology.

**Fix Regional settings:**

The VBScript Label Expression are somewhat depend on the chosen locale (e.g. point or 
comma decimal separators). If you have problems with visualizing labels,
select English as your local in Windows > Regional Settings and restart ArcPro.

From `Basemap_World_ArcProV290.aprx` onwards, this has been fixed and changing
locales should not be necessary.

The label expression changed from:
```
"<ACP><BOL><FNT name='Arial' size='" &  5+[Weights]*0.18 & "'>" & [ImpTag] & "</FNT></BOL></ACP>"
```
(VBScript)

to
```
"<ACP><BOL><FNT name='Arial' size='" +  str(5 + (float([Weights].replace(",","."))) * 0.18) + "'>" + [ImpTag] + "</FNT></BOL></ACP>"
```
(Python)

