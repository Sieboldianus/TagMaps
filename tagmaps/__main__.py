#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Tag Maps Clustering

- will read in geotagged (lat/lng) decimal degree point data
- will generate HDBSCAN Cluster Hierarchy
- will output Alpha Shapes/Delauney for cluster cut at specific distance
"""

import re
import sys
import os
import csv
import fiona
from decimal import Decimal
from shapely.ops import transform
import pyproj
from fiona.crs import from_epsg
import copy
from time import sleep
import time
import datetime
import collections
from collections import namedtuple
from collections import Counter
from collections import defaultdict
from _csv import QUOTE_MINIMAL
from glob import glob
from typing import List, Set, Dict, Tuple, Optional, TextIO
from tagmaps.classes.shared_structure import EMOJI, LOCATIONS, TAGS
from tagmaps.classes.interface import UserInterface
from tagmaps.classes.cluster import ClusterGen
from tagmaps.classes.load_data import LoadData
from tagmaps.classes.alpha_shapes import AlphaShapes
from tagmaps.classes.compile_output import Compile
from tagmaps.classes.utils import Utils

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"

# from .utils import *
# Fiona needed for reading Shapefile

# import Proj, transform

# enable for map display
# from mpl_toolkits.basemap import Basemap
# from PIL import Image
# https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects
# alternative Shapefile module pure Python
# https://github.com/GeospatialPython/pyshp#writing-shapefiles
# import shapefile


def main():
    """Main tag maps function for direct execution of package

    - will read from 01_Input/ folder
    - will output clustered data to 02_Output/
    """

    # initialize logger and config
    cfg, log = Utils.init_main()
    lbsn_data = LoadData(cfg)

    print('\n')
    log.info("########## STEP 1 of 6: Data Cleanup ##########")
    lbsn_data.parse_input_records()
    # get current time
    now = time.time()
    # get cleaned data for use in clustering
    cleaned_post_dict = lbsn_data.get_cleaned_post_dict()
    # status report
    log.info(
        f'\nTotal user count: {len(lbsn_data.locations_per_userid_dict)} (UC)')
    log.info(f'Total post count: {lbsn_data.stats.count_glob:02d} (PC)')
    log.info(f'Total tag count (PTC): {lbsn_data.stats.count_tags_global}')
    log.info(f'Total emoji count (PEC): {lbsn_data.stats.count_emojis_global}')
    log.info(f'Total user post locations (UPL): '
             f'{len(lbsn_data.distinct_userlocations_set)}')
    log.info(lbsn_data.bounds.get_bound_report())

    # get prepared data for statistics and clustering
    prepared_data = lbsn_data.get_prepared_data()

    if (cfg.cluster_tags or cfg.cluster_emoji):
        log.info("\n########## STEP 2 of 6: Tag Ranking ##########")

        location_name_count = len(prepared_data.locid_locname_dict)
        if location_name_count > 0:
            log.info(
                f"Number of locations with names: "
                f"{location_name_count}")

        log.info(f"Total unique tags: {prepared_data.total_unique_tags}")
        log.info(f"Total unique emoji: {prepared_data.total_unique_emoji}")
        log.info(
            f"Total unique locations: {prepared_data.total_unique_locations}")
        log.info(
            f'Total tags count for the {prepared_data.tmax} '
            f'most used tags: {prepared_data.total_tag_count}.')
        log.info(
            f'Total emoji count for the {prepared_data.emax} '
            f'most used emoji: {prepared_data.total_emoji_count}.')

    if cfg.statistics_only is False:
        # restart time monitoring for monitoring of
        # actual cluster step
        now = time.time()
        log.info(
            "\n########## STEP 3 of 6: Tag & Emoji Location Clustering ##########")
        # initialize list of types to cluster
        cluster_types = list()
        if cfg.cluster_tags:
            cluster_types.append(TAGS)
        if cfg.cluster_emoji:
            cluster_types.append(EMOJI)
        if cfg.cluster_locations:
            cluster_types.append(LOCATIONS)
        # initialize clusterers
        clusterer_list = list()
        for cls_type in cluster_types:
            clusterer = ClusterGen.new_clusterer(
                clusterer_type=cls_type,
                bounds=lbsn_data.bounds,
                cleaned_post_dict=cleaned_post_dict,
                prepared_data=prepared_data,
                local_saturation_check=cfg.local_saturation_check
            )
            clusterer_list.append(clusterer)

        # get user input for cluster distances
        if not cfg.auto_mode:
            user_intf = UserInterface(
                clusterer_list,
                prepared_data.locid_locname_dict)
            user_intf.start()

        if cfg.auto_mode or user_intf.abort is False:
            for clusterer in clusterer_list:
                if clusterer.cls_type == LOCATIONS:
                    # skip location clustering for now
                    continue
                if clusterer.cls_type == TAGS:
                    log.info("Tag clustering: ")
                else:
                    log.info("Emoji clustering: ")
                clusterer.get_itemized_clusters()
            log.info(
                "########## STEP 4 of 6: Generating Alpha Shapes ##########")
            # store results for tags and emoji in one list
            shapes_and_meta_list = list()
            for clusterer in clusterer_list:
                if clusterer.cls_type == LOCATIONS:
                    # skip location clustering for now
                    continue
                cluster_shapes = clusterer.get_cluster_shapes()
                shapes_and_meta_list.append(cluster_shapes)
            log.info(
                "########## STEP 5 of 6: Writing Results to Shapefile ##########")
            Compile.write_shapes(
                bounds=lbsn_data.bounds,
                shapes_and_meta_list=shapes_and_meta_list)
        else:
            print(f'\nUser abort.')
    if cfg.cluster_locations and user_intf.abort is False:
        log.info(
            "\n########## STEP 6 of 6: Calculating Overall Location Clusters ##########")
        for clusterer in clusterer_list:
            if clusterer.cls_type == LOCATIONS:
                cluster_centroids = clusterer.get_cluster_centroids()
        Compile.write_centroids(
            bounds=lbsn_data.bounds,
            cluster_centroids=cluster_centroids)

    #
    #    #if not 'clusterTreeCuttingDist' in locals():
    #    #global clusterTreeCuttingDist
    #    if clusterTreeCuttingDist == 0:
    #        clusterTreeCuttingDist = int(input("Specify Cluster (Cut) Distance:\n"))
    #    selected_post_guids = []
    #    #if not 'cleanedPhotoList' in locals():
    #    #global cleanedPhotoList
    #    if len(cleaned_post_list) == 0:
    #        cleaned_post_list = list(cleaned_post_dict.values())
    #    for cleaned_photo_location in cleaned_post_list:
    #        selected_post_guids.append(cleaned_photo_location.guid)
    #    selectedPhotoList = cleaned_post_list
    #    df = pd.DataFrame(selectedPhotoList)
    #    points = df.as_matrix(['lng','lat'])
    #    tagRadiansData = np.radians(points)
    #    clusterer = hdbscan.HDBSCAN(min_cluster_size=2,gen_min_span_tree=False,allow_single_cluster=False,min_samples=1)
    #    #clusterer.fit(tagRadiansData)
    #    with warnings.catch_warnings():
    #        #disable joblist multithread warning
    #        warnings.simplefilter('ignore', UserWarning)
    #        async_result = pool.apply_async(Utils.fit_cluster, (clusterer, tagRadiansData))
    #        clusterer = async_result.get()
    #    clusters = clusterer.single_linkage_tree_.get_clusters(Utils.get_radians_from_meters(clusterTreeCuttingDist/8), min_cluster_size=2)
    #    listOfPhotoClusters = []
    #    numpy_selectedPhotoList_Guids = np.asarray(selected_post_guids)
    #    mask_noisy = (clusters == -1)
    #    number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
    #    print(f'--> {number_of_clusters} Photo cluster.')
    #    #clusternum_photolist = zip(clusters,selectedPhotoList)
    #    #clusterPhotosList = [[] for x in range(number_of_clusters)]
    #    clusterPhotosGuidsList = []
    #    for x in range(number_of_clusters):
    #        currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
    #        clusterPhotosGuidsList.append(currentClusterPhotoGuids)
    #    noClusterPhotos = list(numpy_selectedPhotoList_Guids[clusters==-1])
    #    clusterPhotosGuidsList.sort(key=len,reverse=True)
    #    if cfg.cluster_tags is False:
    #        #detect projection if not already
    #        lim_y_min,lim_y_max,lim_x_min,lim_x_max = Utils.get_rectangle_bounds(points)
    #        bound_points_shapely = geometry.MultiPoint([(lim_x_min, lim_y_min), (lim_x_max, lim_y_max)])
    #        crs_wgs = pyproj.Proj(init='epsg:4326') #data always in lat/lng WGS1984
    #        if cfg.override_crs is None:
    #            #Calculate best UTM Zone SRID/EPSG Code
    #            input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
    #            input_lat_center = bound_points_shapely.centroid.coords[0][1]
    #            epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
    #            crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}')
    #    for photo_cluster in clusterPhotosGuidsList:
    #        photos = [cleaned_post_dict[x] for x in photo_cluster]
    #        uniqueUserCount = len(set([photo.user_guid for photo in photos]))
    #        #get points and project coordinates to suitable UTM
    #        points = [geometry.Point(pyproj.transform(crs_wgs, crs_proj, photo.lng, photo.lat))
    #                  for photo in photos]
    #        point_collection = geometry.MultiPoint(list(points))
    #        result_polygon = point_collection.convex_hull #convex hull
    #        result_centroid = result_polygon.centroid
    #        if result_centroid is not None and not result_centroid.is_empty:
    #            listOfPhotoClusters.append((result_centroid,uniqueUserCount))
    #        #clusterPhotoGuidList = clustersPerTag.get(None, None)
    #    #noclusterphotos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
    #    for photoGuid_noCluster in noClusterPhotos:
    #        photo = cleaned_post_dict[photoGuid_noCluster]
    #        x, y = pyproj.transform(crs_wgs, crs_proj, photo.lng, photo.lat)
    #        pcenter = geometry.Point(x, y)
    #        if pcenter is not None and not pcenter.is_empty:
    #            listOfPhotoClusters.append((pcenter,1))
    #    # Define a polygon feature geometry with one attribute
    #    schema = {
    #        'geometry': 'Point',
    #        'properties': {'Join_Count': 'int'},
    #    }
#
    #    # Write a new Shapefile
    #    # WGS1984
    #    with fiona.open('02_Output/allPhotoCluster.shp', mode='w', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
    #        ## If there are multiple geometries, put the "for" loop here
    #        idx = 0
    #        for photoCluster in listOfPhotoClusters:
    #            idx += 1
    #            c.write({
    #                'geometry': geometry.mapping(photoCluster[0]),
    #                'properties': {'Join_Count': photoCluster[1]},
    #                })
    #print("Writing log file..")
    later = time.time()
    hours, rem = divmod(later-now, 3600)
    minutes, seconds = divmod(rem, 60)
    # difference = int(later - now)
    log.info(f'\nDone.\n{int(hours):0>2} Hours '
             f'{int(minutes):0>2} Minutes and '
             f'{seconds:05.2f} Seconds passed.')
    # log_texts_list.append(reportMsg)
    # with open(log_file, "w", encoding='utf-8') as logfile_a:
    #    for logtext in log_texts_list:
    #        logfile_a.write(logtext)
    # print(reportMsg)
    input("Press any key to exit...")
    sys.exit()


if __name__ == "__main__":
    main()
