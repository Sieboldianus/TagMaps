# -*- coding: utf-8 -*-

"""
Module for tag maps alpha shapes generation
"""

from __future__ import absolute_import

import math
from decimal import Decimal
from collections import namedtuple

import logging
import numpy as np
import pyproj

from scipy.spatial import Delaunay  # pylint: disable=E0611
import shapely.geometry as geometry
from shapely.ops import cascaded_union, polygonize

from tagmaps.classes.compile_output import Compile

# results will be compiled as namedtuple
AlphaShapesAndMeta = namedtuple(
    'AlphaShapesAndMeta',
    'shape post_count views user_count item_name item_totalcount '
    'weightsv1 weightsv2 weightsv3 shapetype')


class AlphaShapes():
    """Converts (cluster) point clouds to shapes"""
    @staticmethod
    def get_single_cluster_shape(
            item, single_post,
            cluster_distance: float, proj_transformer):
        """Get Shapes for items with no clusters
        Will return a buffer based on cluster distance
        """
        shapetype = "Single cluster"
        # project lat/lng to UTM
        point_x, point_y = proj_transformer.transform(
            single_post.lng, single_post.lat)
        pcoordinate = geometry.Point(point_x, point_y)
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
        single_cluster_result = AlphaShapesAndMeta(
            result_polygon, 1, max(single_post.post_views_count,
                                   single_post.post_like_count), 1, str(item[0]),
            item[1], 1, 1, 1, shapetype
        )
        return single_cluster_result

    @staticmethod
    def get_cluster_shape(
            item, clustered_post_guids,
            cleaned_post_dict,
            cluster_distance: float,
            local_saturation_check,
            proj_transformer):
        """Returns alpha shapes and tag_area (sqm) for a point cloud"""
        # we define a new list of Temp Alpha Shapes outside the loop,
        # so that it is not overwritten each time
        alphashapes_and_meta_tmp = list()
        item_area = 0

        for post_guids in clustered_post_guids:
            # for each cluster for this toptag
            posts = [cleaned_post_dict[x]
                     for x in post_guids]
            post_count = len(post_guids)
            unique_user_count = len(
                set([post.user_guid for post in posts]))
            sum_views = sum(
                [post.post_views_count for post in posts])
            # needs to be moved to CompileOutput:
            weightsv1 = Compile.get_weight(
                1, post_count, unique_user_count)

            weightsv2 = Compile.get_weight(
                2, post_count, unique_user_count)
            weightsv3 = Compile.get_weight(
                3, post_count, unique_user_count)
            distinct_locations = {post.loc_id
                                  for post in posts}
            # simple list comprehension with projection:
            points = [geometry.Point(
                proj_transformer.transform(
                    float(location.split(':')[1]), float(location.split(':')[0]))
            ) for location in distinct_locations]

            # get poly shape from points
            result = AlphaShapes._get_poly(points, cluster_distance)
            result_polygon = result[0]
            shapetype = result[1]

            # Geom, Join_Count, Views,  COUNT_User,ImpTag,TagCountG,HImpTag
            if result_polygon is not None and not result_polygon.is_empty:
                if local_saturation_check:
                    item_area += result_polygon.area
                alphashapedata = AlphaShapesAndMeta(
                    result_polygon, post_count, sum_views,
                    unique_user_count, item[0], item[1],
                    weightsv1, weightsv2, weightsv3,
                    shapetype)
                alphashapes_and_meta_tmp.append(alphashapedata)
        if alphashapes_and_meta_tmp:
            # finally sort and append all
            # cluster shapes for this tag
            alphashapes_and_meta_tmp = sorted(
                alphashapes_and_meta_tmp, key=lambda x: -x[6])
        AlphaShapesArea = namedtuple(
            'AlphaShapesArea', 'alphashape item_area')
        return AlphaShapesArea(alphashapes_and_meta_tmp, item_area)

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
        if not isinstance(poly_shape, bool) and poly_shape.is_empty:
            # try again with centered axis reduced alpha
            poly_shape = AlphaShapes.alpha_shape(
                points, alpha=(cluster_distance/startalpha), centeraxis=True)
        # if not poly_shape.is_empty:
        # print("Success")
        # check type comparison here
        if (isinstance(poly_shape, geometry.multipolygon.MultiPolygon)
                or isinstance(poly_shape, bool)):
            for i in range(1, 6):
                # try decreasing alpha
                # ** means cube
                alpha = startalpha + (startalpha * (i**i))
                # /100000
                poly_shape = AlphaShapes.alpha_shape(
                    points, alpha=cluster_distance/alpha)
                if not (isinstance(poly_shape,
                                   geometry.multipolygon.MultiPolygon)
                        and not isinstance(poly_shape, bool)):
                    shapetype = "Multipolygon Alpha Shape /" + \
                        str(alpha)
                    break
            if (isinstance(poly_shape, geometry.multipolygon.MultiPolygon)
                    or isinstance(poly_shape, bool)):
                # try increasing alpha
                for i in range(1, 6):
                    # try decreasing alpha
                    alpha = startalpha / (i*i)
                    # /100000
                    poly_shape = AlphaShapes.alpha_shape(
                        points, alpha=cluster_distance/alpha)
                    if not (isinstance(
                            poly_shape, geometry.multipolygon.MultiPolygon)
                            and not isinstance(poly_shape, bool)):
                        shapetype = "Multipolygon Alpha Shape /" + \
                            str(alpha)
                        break
            if isinstance(poly_shape, geometry.multipolygon.MultiPolygon):
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
        if (isinstance(poly_shape, bool)
                or poly_shape.is_empty or
                AlphaShapes._few_polyinpoints(points, poly_shape)):
            shapetype = ("BoolAlpha/Empty -> Fallback "
                         "to PointCloud Convex Hull")
            # convex hull
            poly_shape = point_collection.convex_hull
        # Finally do a buffer to smooth alpha
        poly_shape = poly_shape.buffer(
            cluster_distance/4, resolution=3)
        # result_polygon = result_polygon.buffer(
        #   min(distXLng,distYLat)/100,resolution=3)
        return poly_shape, shapetype

    @staticmethod
    def _few_polyinpoints(points, poly):
        """Check how many of original points are in Alpha

        Because some QHull Delauney return a small Alpha Shape that
        does not include most points, this is a fallback solution.
        Better solution would be to revise QHull Delauney/Alpha,
        but even with centered axis, this issue remains (see alpha_shape).
        """
        p_count = 1
        for point in points:
            if point.within(poly):
                p_count += 1
        perc = p_count/(len(points)/100)
        if perc < 50:
            return True
        return False

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
              isinstance(poly_shape, geometry.point.Point)
              or poly_shape is None):
            poly_shape, shapetype = AlphaShapes._get_poly_one(
                point_collection, cluster_distance)
        # final check for multipolygon
        if (isinstance(poly_shape, geometry.multipolygon.MultiPolygon)
                or poly_shape.is_empty):
            # usually not executed
            poly_shape = poly_shape.convex_hull
            shapetype = "Convex Hull Final Fallback"

        return poly_shape, shapetype

    @staticmethod
    def alpha_shape(points, alpha, centeraxis=None):
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

        Notes:
        see also floating point resolution issue:
        https://stackoverflow.com/questions/8071382/points-left-out-when-nearby-in-scipy-spatial-delaunay

        Consider replace with shapely.Delauney
        http://kuanbutts.com/2017/08/17/delaunay-triangulation/
        """
        if centeraxis is None:
            centeraxis = False
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

        # qhull_options = 'Qt'
        # #To avoid this error,
        # joggle the data by specifying the
        # 'QJ' option to the DELAUNAY function.see:
        # https://de.mathworks.com/matlabcentral/answers/94438-why-does-the-delaunay-function-in-matlab-7-0-r14-produce-an-error-when-passed-colinear-points?s_tid=gn_loc_drop

        if centeraxis:
            # Center axis for avoiding floating point precision issues
            norm_co = coords[0]
            coords = coords - norm_co
        tri = Delaunay(coords)
        # print problematic points:
        # print(tri.coplanar)
        # tri = Delaunay(coords,qhull_topions='QJ')
        # #Version 3.1 added triangulated output ('Qt').
        # It should be used for Delaunay triangulations
        # instead of using joggled input ('QJ').
        edges = set()
        edge_points = []
        # loop over triangles:
        # vert_ia, ib, ic = indices of corner points of the
        # triangle
        for vert_ia, vert_ib, vert_ic in tri.vertices:
            pa_v = coords[vert_ia]
            pb_v = coords[vert_ib]
            pc_v = coords[vert_ic]
            # Lengths of sides of triangle
            a_val = math.sqrt((pa_v[0]-pb_v[0])**2 + (pa_v[1]-pb_v[1])**2)
            b_val = math.sqrt((pb_v[0]-pc_v[0])**2 + (pb_v[1]-pc_v[1])**2)
            c_val = math.sqrt((pc_v[0]-pa_v[0])**2 + (pc_v[1]-pa_v[1])**2)
            # Semiperimeter of triangle
            s_res = (a_val + b_val + c_val)/2.0
            # Area of triangle by Heron's formula
            try:
                area = math.sqrt(
                    s_res*(s_res-a_val)*(s_res-b_val)*(s_res-c_val))
            except ValueError:
                return False
            if area == 0:
                return False
            circum_r = a_val*b_val*c_val/(4.0*area)
            # Here's the radius filter.
            # print circum_r
            if circum_r < 1.0/alpha:
                add_edge(edges, edge_points, coords, vert_ia, vert_ib)
                add_edge(edges, edge_points, coords, vert_ib, vert_ic)
                add_edge(edges, edge_points, coords, vert_ic, vert_ia)

        if centeraxis:
            # return to original axis center
            edge_points = [np.array(
                [edgepoint[0]+norm_co, edgepoint[1]+norm_co]
            ) for edgepoint in edge_points]

        mmulti_line_str = geometry.MultiLineString(edge_points)
        triangles = list(polygonize(mmulti_line_str))
        return cascaded_union(triangles)  # , edge_points
        # return geometry.polygon.asPolygon(edge_points,holes=None)
