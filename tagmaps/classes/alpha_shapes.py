# -*- coding: utf-8 -*-

"""
Module for tag maps alpha shapes generation
"""

import sys
import math
import pyproj
import numpy as np
from decimal import Decimal
from typing import List, Set, Dict, Tuple
from math import radians, cos, sin, asin, sqrt
import shapely.geometry as geometry
from shapely.ops import transform, cascaded_union, polygonize
from descartes import PolygonPatch
from scipy.spatial import Delaunay
from fiona.crs import from_epsg
from tagmaps.classes.utils import Utils


class AlphaShapes():

    @staticmethod
    def _get_best_utmzone(bound_points_shapely: geometry.MultiPoint):
        """Calculate best UTM Zone SRID/EPSG Code
        Args:
        True centroid (coords may be multipoint)"""
        input_lon_center = bound_points_shapely.centroid.coords[0][0]
        input_lat_center = bound_points_shapely.centroid.coords[0][1]
        epsg_code = AlphaShapes._convert_wgs_to_utm(
            input_lon_center, input_lat_center)
        crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}')
        return crs_proj, epsg_code

    @staticmethod
    def _convert_wgs_to_utm(lon: float, lat: float):
        """"[summary]"

        Args:
            lon: latitude
            lat: longitude

        Returns:
            [type]: [description]

        Notes:
        # https://stackoverflow.com/questions/40132542/get-a-cartesian-projection-accurate-around-a-lat-lng-pair
        """

        utm_band = str((math.floor((lon + 180) / 6) % 60) + 1)
        if len(utm_band) == 1:
            utm_band = '0'+utm_band
        if lat >= 0:
            epsg_code = '326' + utm_band
        else:
            epsg_code = '327' + utm_band
        return epsg_code

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
        alphashapes_and_meta_tmp = []
        # points = []
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
            # calculate different weighting formulas
            # weightsv1 = 1+ photoCount *(
            #   sqrt(1/( photoCount / uniqueUserCount )**3)
            #   )
            # -> Standard weighting formula
            # (x**y means x raised to the power y);
            # +1 to UserCount: prevent 1-2
            # Range from being misaligned
            # weightsv2 = 1+ photoCount *(
            #   sqrt(1/( photoCount / uniqueUserCount )**2)
            # )
            weightsv1 = post_count * (
                sqrt(1/(post_count / (unique_user_count+1))**3))
            # -> Standard weighting formula
            # (x**y means x raised to the power y);
            # +1 to UserCount: prevent 1-2
            # Range from being misaligned
            weightsv2 = post_count * (
                sqrt(1/(post_count / (unique_user_count+1))**2))
            # -> less importance on User_Count in correlation
            # to photo count [Join_Count];
            # +1 to UserCount: prevent 1-2
            # Range from being misaligned
            weightsv3 = sqrt(
                (post_count+(2*sqrt(post_count)))*2)
            # -> Ignores User_Count,
            # this will emphasize individual
            # and very active users
            # points = [geometry.Point(photo.lng, photo.lat)
            #          for photo in photos]
            # instead of lat/lng for each photo,
            # we use photo_locID to identify a
            # list of distinct locations
            distinct_locations = set([post.loc_id
                                      for post in posts])
            # simple list comprehension without projection:
            # points = [geometry.Point(
            #               Decimal(location.split(':')[1]),
            #               Decimal(location.split(':')[0]))
            #           for location in distinctLocations]
            points = [geometry.Point(
                pyproj.transform(
                    crs_wgs,
                    crs_proj,
                    Decimal(location.split(':')[1]),
                    Decimal(location.split(':')[0])))
                for location in distinct_locations]
            point_collection = geometry.MultiPoint(
                list(points))
            result_polygon = None

            if len(points) >= 5:
                if len(points) < 10:
                    # convex hull for small point clouds:
                    result_polygon = point_collection.convex_hull
                    result_polygon = result_polygon.buffer(
                        cluster_distance/4, resolution=3)
                    shapetype = "between 5 and 10 points_convexHull"
                    # result_polygon = result_polygon.buffer(
                    #   min(distXLng,distYLat)/100,resolution=3)
                else:
                    if len(points) > 500:
                        startalpha = 1000000
                    elif len(points) > 200:
                        startalpha = 10000
                    else:
                        startalpha = 9000
                    # concave hull/alpha shape /50000:
                    result_polygon = AlphaShapes.alpha_shape(
                        points, alpha=cluster_distance/startalpha)
                    shapetype = "Initial Alpha Shape + Buffer"
                    # check type comparison here
                    if (type(result_polygon) is geometry.multipolygon.MultiPolygon
                            or isinstance(result_polygon, bool)):
                        # repeat generating alpha shapes with
                        # smaller alpha value if Multigon is
                        # generated
                        # smaller alpha values mean less
                        # granularity of resulting polygon
                        # but too large alpha may result
                        # in empty polygon
                        # (this branch is sometimes
                        # executed for larger scales)
                        for i in range(1, 6):
                            # try decreasing alpha
                            # ** means cube
                            alpha = startalpha + (startalpha * (i**i))
                            # /100000
                            result_polygon = AlphaShapes.alpha_shape(
                                points, alpha=cluster_distance/alpha)
                            if (type(result_polygon) is not geometry.multipolygon.MultiPolygon
                                    and not isinstance(result_polygon, bool)):
                                shapetype = "Multipolygon Alpha Shape /" + \
                                    str(alpha)
                                break
                        if (type(result_polygon) is geometry.multipolygon.MultiPolygon
                                or isinstance(result_polygon, bool)):
                            # try increasing alpha
                            for i in range(1, 6):
                                # try decreasing alpha
                                alpha = startalpha / (i*i)
                                # /100000
                                result_polygon = AlphaShapes.alpha_shape(
                                    points, alpha=cluster_distance/alpha)
                                if (type(result_polygon) is not geometry.multipolygon.MultiPolygon
                                        and not isinstance(result_polygon, bool)):
                                    shapetype = "Multipolygon Alpha Shape /" + \
                                        str(alpha)
                                    break
                        if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                            shapetype = "Multipolygon Alpha Shape -> Convex Hull"
                            # if still of type multipolygon,
                            # try to remove holes and do a convex_hull
                            result_polygon = result_polygon.convex_hull
                        # OR: in case there was a problem with generating
                        # alpha shapes
                        # (circum_r = a*b*c/(4.0*area)
                        # --> ZeroDivisionError: float division by zero)
                        # this branch is rarely executed
                        # for large point clusters where
                        # alpha is perhaps set too small
                        elif (isinstance(result_polygon, bool)
                              or result_polygon.is_empty):
                            shapetype = "BoolAlpha -> Fallback to PointCloud Convex Hull"
                            # convex hull
                            result_polygon = point_collection.convex_hull
                    # Finally do a buffer to smooth alpha
                    result_polygon = result_polygon.buffer(
                        cluster_distance/4, resolution=3)
                    # result_polygon = result_polygon.buffer(
                    #   min(distXLng,distYLat)/100,resolution=3)
            elif 2 <= len(points) < 5:
                shapetype = "between 2 and 5 points_buffer"
                # calc distance between points, see
                # http://www.mathwarehouse.com/algebra/distance_formula/index.php
                # bdist = math.sqrt(
                #   (points[0].coords.xy[0][0]-points[1].coords.xy[0][0])**2
                # + (points[0].coords.xy[1][0]-points[1].coords.xy[1][0])**2)
                # print(str(bdist))

                # single dots are presented as buffer with 0.5% of width-area:
                result_polygon = point_collection.buffer(
                    cluster_distance/4, resolution=3)
                result_polygon = result_polygon.convex_hull
                # result_polygon = point_collection.buffer(
                #   min(distXLng,distYLat)/100,resolution=3)
                # #single dots are presented as buffer with 0.5% of width-area
            elif (len(points) == 1 or
                  type(result_polygon) is geometry.point.Point
                  or result_polygon is None):
                shapetype = "1 point cluster"
                # single dots are presented as buffer
                # with 0.5% of width-area
                result_polygon = point_collection.buffer(
                    cluster_distance/4, resolution=3)
                # result_polygon = point_collection.buffer(
                # min(distXLng,distYLat)/100,resolution=3)
                # #single dots are presented as buffer
                # with 0.5% of width-area
            # final check for multipolygon
            if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                # usually not executed
                result_polygon = result_polygon.convex_hull
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
