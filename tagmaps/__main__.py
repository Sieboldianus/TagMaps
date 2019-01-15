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
from tagmaps.classes.interface import UserInterface
from tagmaps.classes.cluster import ClusterGen
from tagmaps.classes.shared_structure \
    import PostStructure, CleanedPost
from tagmaps.classes.load_data import LoadData
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
    total_distinct_locations = len(lbsn_data.distinct_locations_set)
    log.info(
        f'\nTotal user count: {len(lbsn_data.locations_per_userid_dict)} (UC)')
    log.info(f'Total post count: {lbsn_data.stats.count_glob:02d} (PC)')
    log.info(f'Total tag count (PTC): {lbsn_data.stats.count_tags_global}')
    log.info(f'Total emoji count (PEC): {lbsn_data.stats.count_emojis_global}')
    log.info(f'Total user post locations (UPL): '
             f'{len(lbsn_data.distinct_userlocations_set)}')
    log.info(lbsn_data.bounds.get_bound_report())

    if (cfg.cluster_tags or cfg.cluster_emoji):
        log.info("\n########## STEP 2 of 6: Tag Ranking ##########")

        prepared_data = lbsn_data.get_prepared_data()

        log.info(f"Total unique tags: {prepared_data.total_unique_tags}")
        log.info(f"Total unique emoji: {prepared_data.total_unique_emoji}")
        log.info(
            f'Total tags count for cleaned (tmax) tags list '
            f'(Top {prepared_data.tmax}): {prepared_data.total_tag_count}.')
        log.info(
            f'Total emoji count for cleaned (tmax) emoji list '
            f'(Top {prepared_data.emax}): {prepared_data.total_emoji_count}.')

        top_tags_list = prepared_data.top_tags_list
        if cfg.statistics_only is False:
            # restart time monitoring for actual cluster step
            now = time.time()
            log.info(
                "\n########## STEP 3 of 6: Tag Location Clustering ##########")

            cluster_tag_data = ClusterGen(
                lbsn_data.bounds,
                cleaned_post_dict,
                prepared_data.top_tags_list,
                total_distinct_locations,
                prepared_data.tmax)
            cluster_emoji_data = ClusterGen(
                lbsn_data.bounds,
                cleaned_post_dict,
                prepared_data.top_emoji_list,
                total_distinct_locations,
                prepared_data.emax)
            user_intf = UserInterface(cluster_tag_data,
                                      cluster_emoji_data)
            user_intf.start()

#            noClusterPhotos_perTag_DictOfLists = defaultdict(list)
#            clustersPerTag = defaultdict(list)
#            if proceedClusting:
#                # Proceed with clustering all tags
#                # data always in lat/lng WGS1984
#                crs_wgs = pyproj.Proj(init='epsg:4326')
#                if cfg.override_crs is None:
#                    #Calculate best UTM Zone SRID/EPSG Code
#                    input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
#                    input_lat_center = bound_points_shapely.centroid.coords[0][1]
#                    epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
#                    crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}')
#                project = lambda x, y: pyproj.transform(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init=f'epsg:{epsg_code}'), x, y)
#                #geom_proj = transform(project, alphaShapeAndMeta[0])
#
#                if cfg.local_saturation_check:
#                    clusters, selected_post_guids = cluster_tag(prepared_data.single_mostused_tag, None, True)
#                    numpy_selectedPhotoList_Guids = np.asarray(selected_post_guids)
#                    mask_noisy = (clusters == -1)
#                    number_of_clusters = len(np.unique(clusters[~mask_noisy]))
#                    print(f'--> {number_of_clusters} cluster.')
#                    clusterPhotosGuidsList = []
#                    for x in range(number_of_clusters):
#                        currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
#                        clusterPhotosGuidsList.append(currentClusterPhotoGuids)
#                    noClusterPhotos_perTag_DictOfLists[prepared_data.single_mostused_tag[0]] = list(numpy_selectedPhotoList_Guids[clusters==-1])
#                    # Sort descending based on size of cluster: https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
#                    clusterPhotosGuidsList.sort(key=len, reverse=True)
#                    if not len(clusterPhotosGuidsList) == 0:
#                        clustersPerTag[prepared_data.single_mostused_tag[0]] = clusterPhotosGuidsList
#                global tnum
#                tnum = 1
#                for toptag in top_tags_list:
#                    if cfg.local_saturation_check and tnum == 1 and toptag[0] in clustersPerTag:
#                        #skip toptag if already clustered due to local saturation
#                        continue
#                    clusters, selected_post_guids = cluster_tag(toptag, None, True)
#                    #print("baseDataList: ")
#                    #print(str(type(selectedPhotoList)))
#                    #for s in selectedPhotoList[:2]:
#                    #    print(*s)
#                    #print("resultData: ")
#                    ##for s in clusters[:2]:
#                    ##    print(*s)
#                    #print(str(type(clusters)))
#                    #print(clusters)
#                    #clusters contains the cluster values (-1 = no cluster, 0 maybe, >0 = cluster
#                    # in the same order, selectedPhotoList contains all original photo data, thus clusters[10] and selectedPhotoList[10] refer to the same photo
#
#                    numpy_selectedPhotoList_Guids = np.asarray(selected_post_guids)
#                    mask_noisy = (clusters == -1)
#                    if len(selected_post_guids) == 1:
#                        number_of_clusters = 0
#                    else:
#                        number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
#                    #if number_of_clusters > 200:
#                    #    log.info("--> Too many, skipped for this scale.")
#                    #    continue
#                    if not number_of_clusters == 0:
#                        print(f'--> {number_of_clusters} cluster.')
#                        tnum += 1
#                        photo_num = 0
#                        #clusternum_photolist = zip(clusters,selectedPhotoList)
#                        #clusterPhotosList = [[] for x in range(number_of_clusters)]
#                        clusterPhotosGuidsList = []
#                        for x in range(number_of_clusters):
#                            currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
#                            clusterPhotosGuidsList.append(currentClusterPhotoGuids)
#                        noClusterPhotos_perTag_DictOfLists[toptag[0]] = list(numpy_selectedPhotoList_Guids[clusters==-1])
#                        # Sort descending based on size of cluster: https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
#                        clusterPhotosGuidsList.sort(key=len, reverse=True)
#                        if not len(clusterPhotosGuidsList) == 0:
#                            clustersPerTag[toptag[0]] = clusterPhotosGuidsList
#                    else:
#                        print("--> No cluster.")
#                        noClusterPhotos_perTag_DictOfLists[toptag[0]] = list(numpy_selectedPhotoList_Guids)
#                    #for x in clusters:
#                    #    #photolist = []
#                    #    if x >= 0: # no clusters: x = -1
#                    #        clusterPhotosList[x].append([selectedPhotoList[photo_num]])
#                    #        #clusterPhotosArray_dict[x].add(selectedPhotoList[photo_num])
#                    #    else:
#                    #        noClusterPhotos_perTag_DictOfLists[toptag[0]].append(selectedPhotoList[photo_num])
#                    #    photo_num+=1
#
#                    #print("resultList: ")
#                    #for s in clusterPhotosList[:2]:
#                    #    print(*s)
#                    #print(str(toptag) + " - Number of clusters: " + str(len(clusterPhotosList)) + " Photo num: " + str(photo_num))
#
#                    #plt.autoscale(enable=True)
#
#                    #if tnum == 50:
#                    #    break
#                        #plt.savefig('foo.png')
#                        #sys.exit()
#                sys.stdout.flush()
#                log.info("########## STEP 4 of 6: Generating Alpha Shapes ##########")
#                #if (tnum % 50 == 0):#modulo: if division has no remainder, force update cmd output
#                #sys.stdout.flush()
#                #for each cluster of points, calculate boundary shape and add statistics (HImpTag etc.)
#                listOfAlphashapesAndMeta = []
#                tnum = 0
#                if cfg.local_saturation_check:
#                    #calculate total area of Top1-Tag for 80% saturation check for lower level tags
#                    saturationExcludeCount = 0
#                    clusterPhotoGuidList = clustersPerTag.get(prepared_data.single_mostused_tag[0], None)
#                    #print("Toptag: " + str(singleMostUsedtag[0]))
#                    if clusterPhotoGuidList is None:
#                        sys.exit(f'No Photos found for toptag: {singleMostUsedtag}')
#                    toptagArea = Utils.generateClusterShape(toptag,clusterPhotoGuidList,cleaned_post_dict,crs_wgs,crs_proj,clusterTreeCuttingDist,cfg.local_saturation_check)[1]
#                for toptag in top_tags_list:
#                    tnum += 1
#                    clusterPhotoGuidList = clustersPerTag.get(toptag[0], None)
#                    #Generate tag Cluster Shapes
#                    if clusterPhotoGuidList:
#                        listOfAlphashapesAndMeta_tmp,tagArea = Utils.generateClusterShape(toptag,clusterPhotoGuidList,cleaned_post_dict,crs_wgs,crs_proj,clusterTreeCuttingDist,cfg.local_saturation_check)
#                        if cfg.local_saturation_check and not tagArea == 0 and not tnum == 1:
#                            localSaturation = tagArea/(toptagArea/100)
#                            #print("Local Saturation for Tag " + toptag[0] + ": " + str(round(localSaturation,0)))
#                            if localSaturation > 60:
#                                #skip tag entirely due to saturation (if total area > 80% of total area of toptag clusters)
#                                #print("Skipped: " + toptag[0] + " due to saturation (" + str(round(localSaturation,0)) + "%).")
#                                saturationExcludeCount += 1
#                                continue #next toptag
#
#                        if len(listOfAlphashapesAndMeta_tmp) > 0:
#                            listOfAlphashapesAndMeta.extend(listOfAlphashapesAndMeta_tmp)
#
#                    singlePhotoGuidList = noClusterPhotos_perTag_DictOfLists.get(toptag[0], None)
#                    if singlePhotoGuidList:
#                        shapetype = "Single cluster"
#                        #print("Single: " + str(len(singlePhotoGuidList)))
#                        photos = [cleaned_post_dict[x] for x in singlePhotoGuidList]
#                        for single_photo in photos:
#                            #project lat/lng to UTM
#                            x, y = pyproj.transform(crs_wgs, crs_proj, single_photo.lng, single_photo.lat)
#                            pcoordinate = geometry.Point(x, y)
#                            result_polygon = pcoordinate.buffer(clusterTreeCuttingDist/4,resolution=3) #single dots are presented as buffer with 0.5% of width-area
#                            #result_polygon = pcoordinate.buffer(min(distXLng,distYLat)/100,resolution=3)
#                            if result_polygon is not None and not result_polygon.is_empty:
#                                listOfAlphashapesAndMeta.append((result_polygon,1,max(single_photo.post_views_count,single_photo.post_like_count),1,str(toptag[0]),toptag[1],1,1,1,shapetype))
#                log.info(f'{len(listOfAlphashapesAndMeta)} Alpha Shapes. Done.')
#                if cfg.local_saturation_check and not saturationExcludeCount == 0:
#                    log.info(f'Excluded {saturationExcludeCount} Tags on local saturation check.')
#                ##Output Boundary Shapes in merged Shapefile##
#                log.info("########## STEP 5 of 6: Writing Results to Shapefile ##########")
#
#               ##Calculate best UTM Zone SRID/EPSG Code
#               #input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
#               #input_lat_center = bound_points_shapely.centroid.coords[0][1]
#               #epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
#               #project = lambda x, y: pyproj.transform(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:{0}'.format(epsg_code)), x, y)
#
#                # Define polygon feature geometry
#                schema = {
#                    'geometry': 'Polygon',
#                    'properties': {'Join_Count': 'int',
#                                   'Views': 'int',
#                                   'COUNT_User': 'int',
#                                   'ImpTag': 'str',
#                                   'TagCountG': 'int',
#                                   'HImpTag': 'int',
#                                   'Weights': 'float',
#                                   'WeightsV2': 'float',
#                                   'WeightsV3': 'float',
#                                   #'shapetype': 'str',
#                                   'emoji': 'int'},
#                }
#
#                #Normalization of Values (1-1000 Range), precalc Step:
#                #######################################
#                weightsv1_range = [x[6] for x in listOfAlphashapesAndMeta] #get the n'th column out for calculating the max/min
#                weightsv2_range = [x[7] for x in listOfAlphashapesAndMeta]
#                weightsv3_range = [x[8] for x in listOfAlphashapesAndMeta]
#                weightsv1_min = min(weightsv1_range)
#                weightsv1_max = max(weightsv1_range)
#                weightsv2_min = min(weightsv2_range)
#                weightsv2_max = max(weightsv2_range)
#                weightsv3_min = min(weightsv3_range)
#                weightsv3_max = max(weightsv3_range)
#                #precalc
#                #https://stats.stackexchange.com/questions/70801/how-to-normalize-data-to-0-1-range
#                weightsv1_mod_a = (1000-1)/(weightsv1_max-weightsv1_min)
#                weightsv1_mod_b = 1000 - weightsv1_mod_a * weightsv1_max
#                weightsv2_mod_a = (1000-1)/(weightsv2_max-weightsv2_min)
#                weightsv2_mod_b = 1000 - weightsv2_mod_a * weightsv2_max
#                weightsv3_mod_a = (1000-1)/(weightsv3_max-weightsv3_min)
#                weightsv3_mod_b = 1000 - weightsv3_mod_a * weightsv3_max
#                #######################################
#                # Write a new Shapefile
#                # WGS1984
#                if (cfg.cluster_tags == False and cfg.cluster_emoji == True):
#                    shapefileName = "allEmojiCluster"
#                else:
#                    shapefileName = "allTagCluster"
#                with fiona.open(f'02_Output/{shapefileName}.shp', mode='w', encoding='UTF-8', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
#                    # Normalize Weights to 0-1000 Range
#                    idx = 0
#                    for alphaShapeAndMeta in listOfAlphashapesAndMeta:
#                        if idx == 0:
#                            HImP = 1
#                        else:
#                            if listOfAlphashapesAndMeta[idx][4] != listOfAlphashapesAndMeta[idx-1][4]:
#                                HImP = 1
#                            else:
#                                HImP = 0
#                        #emoName = unicode_name(alphaShapeAndMeta[4])
#                        #Calculate Normalized Weights Values based on precalc Step
#                        if not alphaShapeAndMeta[6] == 1:
#                            weight1_normalized = weightsv1_mod_a * alphaShapeAndMeta[6] + weightsv1_mod_b
#                        else:
#                            weight1_normalized = 1
#                        if not alphaShapeAndMeta[7] == 1:
#                            weight2_normalized = weightsv2_mod_a * alphaShapeAndMeta[7] + weightsv2_mod_b
#                        else:
#                            weight2_normalized = 1
#                        if not alphaShapeAndMeta[8] == 1:
#                            weight3_normalized = weightsv3_mod_a * alphaShapeAndMeta[8] + weightsv3_mod_b
#                        else:
#                            weight3_normalized = 1
#                        idx += 1
#                        #project data
#                        #geom_proj = transform(project, alphaShapeAndMeta[0])
#                        #c.write({
#                        #    'geometry': geometry.mapping(geom_proj),
#                        if cfg.cluster_emoji and alphaShapeAndMeta[4] in prepared_data.top_emoji_list:
#                            emoji = 1
#                            ImpTagText = ""
#                        else:
#                            emoji = 0
#                            ImpTagText = f'{alphaShapeAndMeta[4]}'
#                        c.write({
#                            'geometry': geometry.mapping(alphaShapeAndMeta[0]),
#                            'properties': {'Join_Count': alphaShapeAndMeta[1],
#                                           'Views': alphaShapeAndMeta[2],
#                                           'COUNT_User': alphaShapeAndMeta[3],
#                                           'ImpTag': ImpTagText,
#                                           'TagCountG': alphaShapeAndMeta[5],
#                                           'HImpTag': HImP,
#                                           'Weights': weight1_normalized,
#                                           'WeightsV2': weight2_normalized,
#                                           'WeightsV3': weight3_normalized,
#                                           #'shapetype': alphaShapeAndMeta[9],
#                                           'emoji': emoji},
#                        })
#                if cfg.cluster_emoji:
#                    with open("02_Output/emojiTable.csv", "w", encoding='utf-8') as emojiTable:
#                        emojiTable.write("FID,Emoji\n")
#                        idx = 0
#                        for alphaShapeAndMeta in listOfAlphashapesAndMeta:
#                            if alphaShapeAndMeta[4] in prepared_data.top_emoji_list:
#                                ImpTagText = f'{alphaShapeAndMeta[4]}'
#                            else:
#                                ImpTagText = ""
#                            emojiTable.write(f'{idx},{ImpTagText}\n')
#                            idx += 1
#
#    else:
#        print(f'\nUser abort.')
#    if abort == False and cfg.cluster_photos == True:
#        log.info("########## STEP 6 of 6: Calculating Overall Photo Location Clusters ##########")
#
#        #if not 'clusterTreeCuttingDist' in locals():
#        #global clusterTreeCuttingDist
#        if clusterTreeCuttingDist == 0:
#            clusterTreeCuttingDist = int(input("Specify Cluster (Cut) Distance:\n"))
#        selected_post_guids = []
#        #if not 'cleanedPhotoList' in locals():
#        #global cleanedPhotoList
#        if len(cleaned_post_list) == 0:
#            cleaned_post_list = list(cleaned_post_dict.values())
#        for cleaned_photo_location in cleaned_post_list:
#            selected_post_guids.append(cleaned_photo_location.guid)
#        selectedPhotoList = cleaned_post_list
#        df = pd.DataFrame(selectedPhotoList)
#        points = df.as_matrix(['lng','lat'])
#        tagRadiansData = np.radians(points)
#        clusterer = hdbscan.HDBSCAN(min_cluster_size=2,gen_min_span_tree=False,allow_single_cluster=False,min_samples=1)
#        #clusterer.fit(tagRadiansData)
#        with warnings.catch_warnings():
#            #disable joblist multithread warning
#            warnings.simplefilter('ignore', UserWarning)
#            async_result = pool.apply_async(Utils.fit_cluster, (clusterer, tagRadiansData))
#            clusterer = async_result.get()
#        clusters = clusterer.single_linkage_tree_.get_clusters(Utils.get_radians_from_meters(clusterTreeCuttingDist/8), min_cluster_size=2)
#        listOfPhotoClusters = []
#        numpy_selectedPhotoList_Guids = np.asarray(selected_post_guids)
#        mask_noisy = (clusters == -1)
#        number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
#        print(f'--> {number_of_clusters} Photo cluster.')
#        #clusternum_photolist = zip(clusters,selectedPhotoList)
#        #clusterPhotosList = [[] for x in range(number_of_clusters)]
#        clusterPhotosGuidsList = []
#        for x in range(number_of_clusters):
#            currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
#            clusterPhotosGuidsList.append(currentClusterPhotoGuids)
#        noClusterPhotos = list(numpy_selectedPhotoList_Guids[clusters==-1])
#        clusterPhotosGuidsList.sort(key=len,reverse=True)
#        if cfg.cluster_tags is False:
#            #detect projection if not already
#            lim_y_min,lim_y_max,lim_x_min,lim_x_max = Utils.get_rectangle_bounds(points)
#            bound_points_shapely = geometry.MultiPoint([(lim_x_min, lim_y_min), (lim_x_max, lim_y_max)])
#            crs_wgs = pyproj.Proj(init='epsg:4326') #data always in lat/lng WGS1984
#            if cfg.override_crs is None:
#                #Calculate best UTM Zone SRID/EPSG Code
#                input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
#                input_lat_center = bound_points_shapely.centroid.coords[0][1]
#                epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
#                crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}')
#        for photo_cluster in clusterPhotosGuidsList:
#            photos = [cleaned_post_dict[x] for x in photo_cluster]
#            uniqueUserCount = len(set([photo.user_guid for photo in photos]))
#            #get points and project coordinates to suitable UTM
#            points = [geometry.Point(pyproj.transform(crs_wgs, crs_proj, photo.lng, photo.lat))
#                      for photo in photos]
#            point_collection = geometry.MultiPoint(list(points))
#            result_polygon = point_collection.convex_hull #convex hull
#            result_centroid = result_polygon.centroid
#            if result_centroid is not None and not result_centroid.is_empty:
#                listOfPhotoClusters.append((result_centroid,uniqueUserCount))
#            #clusterPhotoGuidList = clustersPerTag.get(None, None)
#        #noclusterphotos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
#        for photoGuid_noCluster in noClusterPhotos:
#            photo = cleaned_post_dict[photoGuid_noCluster]
#            x, y = pyproj.transform(crs_wgs, crs_proj, photo.lng, photo.lat)
#            pcenter = geometry.Point(x, y)
#            if pcenter is not None and not pcenter.is_empty:
#                listOfPhotoClusters.append((pcenter,1))
#        # Define a polygon feature geometry with one attribute
#        schema = {
#            'geometry': 'Point',
#            'properties': {'Join_Count': 'int'},
#        }
#
#        # Write a new Shapefile
#        # WGS1984
#        with fiona.open('02_Output/allPhotoCluster.shp', mode='w', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
#            ## If there are multiple geometries, put the "for" loop here
#            idx = 0
#            for photoCluster in listOfPhotoClusters:
#                idx += 1
#                c.write({
#                    'geometry': geometry.mapping(photoCluster[0]),
#                    'properties': {'Join_Count': photoCluster[1]},
#                    })
#    print("Writing log file..")
#    later = time.time()
#    hours, rem = divmod(later-now, 3600)
#    minutes, seconds = divmod(rem, 60)
#    difference = int(later - now)
#    log.info(f'\nDone.\n{int(hours):0>2} Hours {int(minutes):0>2} Minutes and {seconds:05.2f} Seconds passed.')
#    #log_texts_list.append(reportMsg)
#    #with open(log_file, "w", encoding='utf-8') as logfile_a:
#    #    for logtext in log_texts_list:
#    #        logfile_a.write(logtext)
#    #print(reportMsg)
    input("Press any key to exit...")
    sys.exit()


if __name__ == "__main__":
    main()
