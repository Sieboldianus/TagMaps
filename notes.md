## Clustering:

https://github.com/scikit-learn-contrib/hdbscan

## Generating Shapes:

2017-10-12: Delaunay Triangulation used in "A Geometric Pattern-Based Method to Build Hierarchies of Geo-Referenced Tags"
see "D:\03_EvaVGI\08_Literatur\IN\2017-08-18_HierarchyTag_Geometry_Pattern\4211a546.pdf"
see https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.Delaunay.html
	Parameters: 		points : ndarray of floats, shape (npoints, ndim)
    
see also (Alpha Shapes):
        https://plot.ly/python/alpha-shapes/
        https://stackoverflow.com/questions/41268547/estimating-an-area-of-an-image-generated-by-a-set-of-points-alpha-shapes
        
or, if all points are seperated beforehand, HULL is also possible, simply generating a boundary shape for all input points:
        https://stackoverflow.com/questions/44685052/boundary-points-from-a-set-of-coordinates
        `
        import numpy as np
        from scipy.spatial import ConvexHull
        allPoints=np.column_stack((LATS,LONGS))
        hullPoints = ConvexHull(allPoints)
        `
        or concave hull: http://ubicomp.algoritmi.uminho.pt/local/concavehull.html
        https://github.com/mlaloux/Python--alpha-shape_concave_hull
        http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/ !!
# Single executable python file

https://stackoverflow.com/questions/11436777/is-there-a-way-to-embed-dependencies-within-a-python-script
https://stackoverflow.com/questions/5458048/how-to-make-a-python-script-standalone-executable-to-run-without-any-dependency
**py2exe**:
    http://docs.python-guide.org/en/latest/shipping/freezing/