# -*- coding: utf-8 -*-

"""
Module for tag maps alpha shapes generation
"""

import logging
import math
import sys
from decimal import Decimal
from math import asin, cos, radians, sin, sqrt
from typing import Dict, List, Set, Tuple

import numpy as np
import pyproj
import shapely.geometry as geometry
from descartes import PolygonPatch
from fiona.crs import from_epsg
from scipy.spatial import Delaunay  # pylint: disable=E0611
from shapely.ops import cascaded_union, polygonize, transform

from tagmaps.classes.shared_structure import AnalysisBounds
from tagmaps.classes.utils import Utils


class AlphaShapes():

    @staticmethod
    def _get_single_cluster_shape(
            item, single_post, crs_wgs,
            crs_proj, cluster_distance):
        """Get Shapes for items with no clusters
        Will return a buffer based on cluster distance
        """
        shapetype = "Single cluster"
        # project lat/lng to UTM
        x, y = pyproj.transform(
            crs_wgs, crs_proj,
            single_post.lng, single_post.lat)
        pcoordinate = geometry.Point(x, y)
        # single dots are presented
        # as buffers with 0.5% of width-area
        result_polygon = pcoordinate.buffer(
            cluster_distance/4,
            resolution=3)
        # result_polygon = pcoordinate.buffer(
        #   min(distXLng,distYLat)/100,
        #   resolution=3)
        if (result_polygon is None or
                result_polygon.is_empty):
            return None
        # append statistics for item with no cluster
        result_tuple = (
            result_polygon, 1,
            max(single_post.post_views_count,
                single_post.post_like_count),
            1, str(item[0]),
            item[1], 1, 1, 1, shapetype)
        return result_tuple

    @staticmethod
    def get_cluster_shape(
            item, clustered_post_guids,
            cleaned_post_dict,
            crs_wgs, crs_proj,
            cluster_distance: float,
            local_saturation_check):
        """Returns alpha shapes and tag_area (sqm) for a point cloud"""
        # we define a new list of Temp Alpha Shapes outside the loop,
        # so that it is not overwritten each time
        alphashapes_and_meta_tmp = list()
        tag_area = 0
        for post_guids in clustered_post_guids:
            # for each cluster for this toptag
            posts = [cleaned_post_dict[x]
                     for x in post_guids]
            post_count = len(post_guids)
            unique_user_count = len(
                set([post.user_guid for post in posts]))
            sum_views = sum(
                [post.post_views_count for post in posts])

            weightsv1 = Utils._get_weight(
                1, post_count, unique_user_count)

            weightsv2 = Utils._get_weight(
                2, post_count, unique_user_count)
            weightsv3 = Utils._get_weight(
                3, post_count, unique_user_count)
            distinct_locations = set([post.loc_id
                                      for post in posts])
            # simple list comprehension with projection:
            points = [geometry.Point(
                      pyproj.transform(
                          crs_wgs,
                          crs_proj,
                          Decimal(location.split(':')[1]),
                          Decimal(location.split(':')[0])))
                      for location in distinct_locations]
            # get poly shape from points
            result = AlphaShapes._get_poly(points, cluster_distance)
            result_polygon = result[0]
            shapetype = result[1]
            # Geom, Join_Count, Views,  COUNT_User,ImpTag,TagCountG,HImpTag
            if result_polygon is not None and not result_polygon.is_empty:
                if local_saturation_check:
                    tag_area += result_polygon.area
                alphashapes_and_meta_tmp.append(
                    (result_polygon, post_count, sum_views,
                     unique_user_count, item[0], item[1],
                     weightsv1, weightsv2, weightsv3,
                     shapetype))
        if len(alphashapes_and_meta_tmp) > 0:
            # finally sort and append all
            # cluster shapes for this tag
            alphashapes_and_meta_tmp = sorted(
                alphashapes_and_meta_tmp, key=lambda x: -x[6])
        return alphashapes_and_meta_tmp, tag_area

    @staticmethod
    def _get_poly_five_to_ten(
            point_collection, cluster_distance):
        """ convex hull for small point clouds"""
        result_polygon = point_collection.convex_hull
        result_polygon = result_polygon.buffer(
            cluster_distance/4, resolution=3)
        shapetype = "between 5 and 10 points_convexHull"
        # result_polygon = result_polygon.buffer(
        #   min(distXLng,distYLat)/100,resolution=3)
        return result_polygon, shapetype

    @staticmethod
    def _get_poly_two_to_five(
            point_collection, cluster_distance):
        """ convex hull for tiny point clouds"""
        shapetype = "between 2 and 5 points_buffer"
        # calc distance between points, see
        # http://www.mathwarehouse.com/algebra/distance_formula/index.php
        # bdist = math.sqrt(
        #   (points[0].coords.xy[0][0]-points[1].coords.xy[0][0])**2
        # + (points[0].coords.xy[1][0]-points[1].coords.xy[1][0])**2)
        # print(str(bdist))
        # single dots are presented as buffer with 0.5% of width-area:
        poly_shape = point_collection.buffer(
            cluster_distance/4, resolution=3)
        poly_shape = poly_shape.convex_hull
        # result_polygon = point_collection.buffer(
        #   min(distXLng,distYLat)/100,resolution=3)
        # #single dots are presented as buffer with 0.5% of width-area
        return poly_shape, shapetype

    @staticmethod
    def _get_poly_larger_ten(
            points, pointcount,
            cluster_distance,
            point_collection):
        """ Get poly for larger point clouds
        This is still recursive trial & error

        Repeat generating alpha shapes with
        smaller alpha value if Multigon is
        generated. Smaller alpha values mean
        less granularity of resulting polygon,
        but too large alpha may result
        in empty polygon
        (this branch is sometimes
        executed for larger scales)
        """
        if pointcount > 500:
            startalpha = 1000000
        elif pointcount > 200:
            startalpha = 10000
        else:
            startalpha = 9000
        # concave hull/alpha shape /50000:
        poly_shape = AlphaShapes.alpha_shape(
            points, alpha=cluster_distance/startalpha)
        shapetype = "Initial Alpha Shape + Buffer"
        # check type comparison here
        if (type(poly_shape) is geometry.multipolygon.MultiPolygon
                or isinstance(poly_shape, bool)):
            for i in range(1, 6):
                # try decreasing alpha
                # ** means cube
                alpha = startalpha + (startalpha * (i**i))
                # /100000
                poly_shape = AlphaShapes.alpha_shape(
                    points, alpha=cluster_distance/alpha)
                if (type(poly_shape) is not
                        geometry.multipolygon.MultiPolygon
                        and not isinstance(poly_shape, bool)):
                    shapetype = "Multipolygon Alpha Shape /" + \
                        str(alpha)
                    break
            if (type(poly_shape) is
                    geometry.multipolygon.MultiPolygon
                    or isinstance(poly_shape, bool)):
                # try increasing alpha
                for i in range(1, 6):
                    # try decreasing alpha
                    alpha = startalpha / (i*i)
                    # /100000
                    poly_shape = AlphaShapes.alpha_shape(
                        points, alpha=cluster_distance/alpha)
                    if (type(poly_shape) is not
                            geometry.multipolygon.MultiPolygon
                            and not isinstance(poly_shape, bool)):
                        shapetype = "Multipolygon Alpha Shape /" + \
                            str(alpha)
                        break
            if type(poly_shape) is geometry.multipolygon.MultiPolygon:
                shapetype = "Multipolygon Alpha Shape -> Convex Hull"
                # if still of type multipolygon,
                # try to remove holes and do a convex_hull
                poly_shape = poly_shape.convex_hull
            # OR: in case there was a problem with generating
            # alpha shapes
            # (circum_r = a*b*c/(4.0*area)
            # --> ZeroDivisionError: float division by zero)
            # this branch is rarely executed
            # for large point clusters where
            # alpha is perhaps set too small
            elif (isinstance(poly_shape, bool)
                  or poly_shape.is_empty):
                shapetype = "BoolAlpha -> Fallback "
                "to PointCloud Convex Hull"
                # convex hull
                poly_shape = point_collection.convex_hull
        # Finally do a buffer to smooth alpha
        poly_shape = poly_shape.buffer(
            cluster_distance/4, resolution=3)
        # result_polygon = result_polygon.buffer(
        #   min(distXLng,distYLat)/100,resolution=3)
        return poly_shape, shapetype

    @staticmethod
    def _get_poly_one(
            point_collection, cluster_distance):
        shapetype = "1 point cluster"
        # single dots are presented as buffer
        # with 0.5% of width-area
        poly_shape = point_collection.buffer(
            cluster_distance/4, resolution=3)
        # result_polygon = point_collection.buffer(
        # min(distXLng,distYLat)/100,resolution=3)
        # #single dots are presented as buffer
        # with 0.5% of width-area
        return poly_shape, shapetype

    @staticmethod
    def _get_poly(points, cluster_distance):
        """Get polygon/shape for collection
        of geooordinates (points)

        Returns:
        Shape (Polygon)
        Shapetype (Approach of Shape-Gen)
        """
        point_collection = geometry.MultiPoint(
            list(points))
        poly_shape = None
        pointcount = len(points)
        if pointcount >= 5:
            if pointcount < 10:
                poly_shape, shapetype = AlphaShapes._get_poly_five_to_ten(
                    point_collection, cluster_distance)
            else:
                poly_shape, shapetype = AlphaShapes._get_poly_larger_ten(
                    points, pointcount, cluster_distance, point_collection)
        elif 2 <= pointcount < 5:
            poly_shape, shapetype = AlphaShapes._get_poly_two_to_five(
                point_collection, cluster_distance)
        elif (pointcount == 1 or
              type(poly_shape) is geometry.point.Point
              or poly_shape is None):
            poly_shape, shapetype = AlphaShapes._get_poly_one(
                point_collection, cluster_distance)
        # final check for multipolygon
        if type(poly_shape) is geometry.multipolygon.MultiPolygon:
            # usually not executed
            poly_shape = poly_shape.convex_hull
        return poly_shape, shapetype

    @staticmethod
    def alpha_shape(points, alpha):
        """
        Alpha Shapes Code by KEVIN DWYER, see
        http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/
            Compute the alpha shape (concave hull) of a set
            of points.
            @param points: Iterable container of points.
            @param alpha: alpha value to influence the
                gooeyness of the border. Smaller numbers
                don't fall inward as much as larger numbers.
                Too large, and you lose everything!

        with minor adaptions to Tag Maps clustering.
        """
        if len(points) < 4:
            # When you have a triangle,
            # there is no sense
            # in computing an alpha shape.
            return geometry.MultiPoint(
                list(points)).convex_hull

        def add_edge(edges, edge_points, coords, i, j):
            """
            Add a line between the i-th and j-th points,
            if not in the list already
            """
            if (i, j) in edges or (j, i) in edges:
                # already added
                return
            edges.add((i, j))
            edge_points.append(coords[[i, j]])
        coords = np.array([point.coords[0]
                           for point in points])

        # print(str(len(coords)))
        # ,qhull_o}ptions = 'QJ')
        # #To avoid this error,
        # joggle the data by specifying the
        # 'QJ' option to the DELAUNAY function.see:
        # https://de.mathworks.com/matlabcentral/answers/94438-why-does-the-delaunay-function-in-matlab-7-0-r14-produce-an-error-when-passed-colinear-points?s_tid=gn_loc_drop
        tri = Delaunay(coords)
        # tri = Delaunay(coords,{'QJ'})
        # #Version 3.1 added triangulated output ('Qt').
        # It should be used for Delaunay triangulations
        # instead of using joggled input ('QJ').
        edges = set()
        edge_points = []
        # loop over triangles:
        # ia, ib, ic = indices of corner points of the
        # triangle
        for ia, ib, ic in tri.vertices:
            pa = coords[ia]
            pb = coords[ib]
            pc = coords[ic]
            # Lengths of sides of triangle
            a = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
            b = math.sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
            c = math.sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)
            # Semiperimeter of triangle
            s = (a + b + c)/2.0
            # Area of triangle by Heron's formula
            try:
                area = math.sqrt(s*(s-a)*(s-b)*(s-c))
            except ValueError:
                return False
            if area == 0:
                return False
            circum_r = a*b*c/(4.0*area)
            # Here's the radius filter.
            # print circum_r
            if circum_r < 1.0/alpha:
                add_edge(edges, edge_points, coords, ia, ib)
                add_edge(edges, edge_points, coords, ib, ic)
                add_edge(edges, edge_points, coords, ic, ia)
        m = geometry.MultiLineString(edge_points)
        triangles = list(polygonize(m))
        return cascaded_union(triangles)  # , edge_points
        # return geometry.polygon.asPolygon(edge_points,holes=None)
