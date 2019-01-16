# -*- coding: utf-8 -*-

"""
Module for tag maps clustering methods
"""

import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import hdbscan
import pyproj
from collections import defaultdict
from typing import List, Set, Dict, Tuple, Optional, TextIO
import shapely.geometry as geometry
from multiprocessing.pool import ThreadPool
from tagmaps.classes.utils import Utils, AnalysisBounds
from tagmaps.classes.shared_structure import CleanedPost

pool = ThreadPool(processes=1)
sns.set_context('poster')
sns.set_style('white')


class ClusterGen():
    """Cluster module for tags, emoji and post locations
    """

    def __init__(self, bounds: AnalysisBounds,
                 cleaned_post_dict: Dict[str, CleanedPost],
                 top_tags_list: List[Tuple[str, int]],
                 total_distinct_locations: int,
                 tmax: int):
        self.tnum = 0
        self.tmax = tmax
        self.bounds = bounds
        self.cleaned_post_dict = cleaned_post_dict
        self.cleaned_post_list = list(cleaned_post_dict.values())
        self.top_tags_list = top_tags_list
        self.total_distinct_locations = total_distinct_locations
        self.autoselect_clusters = False
        self.sel_colors = None
        self.number_of_clusters = None
        self.mask_noisy = None
        self.clusterer = None
        # set initial analysis bounds
        self._update_bounds()
        self.bound_points_shapely = (
            geometry.MultiPoint([
                (self.bounds.lim_lng_min, self.bounds.lim_lat_min),
                (self.bounds.lim_lng_max, self.bounds.lim_lat_max)
            ])
        )

    def _update_bounds(self):
        """Update analysis rectangle boundary based on

        cleaned posts list."""
        df = pd.DataFrame(self.cleaned_post_list)
        points = df.as_matrix(['lng', 'lat'])
        (self.bounds.lim_lat_min,
         self.bounds.lim_lat_max,
         self.bounds.lim_lng_min,
         self.bounds.lim_lng_max) = Utils.get_rectangle_bounds(points)

    def _select_postguids(self, tag: str) -> Tuple[List[str], int]:
        """Select all posts that have a specific tag (or emoji)

        Args:
            tag: tag for selecting posts

        Returns:
            Tuple[List[str], int]: list of post_guids and
                                   number of distinct locations
        """
        distinct_localloc_count = set()
        selected_postguids_list = list()
        for cleaned_photo_location in self.cleaned_post_list:
            if (tag in (cleaned_photo_location.hashtags) or
                    (tag in cleaned_photo_location.post_body)):
                selected_postguids_list.append(cleaned_photo_location.guid)
                distinct_localloc_count.add(cleaned_photo_location.loc_id)
        return selected_postguids_list, len(distinct_localloc_count)

    def _getselect_postguids(self, tag: str, silent: bool = True) -> List[str]:
        """Get list of post guids with specific tag

        Args:
            tag: tag for selecting posts
        """
        (selected_postguids_list,
         distinct_localloc_count) = self._select_postguids(tag)
        perc_oftotal_locations = (
            distinct_localloc_count /
            (self.total_distinct_locations/100)
        )
        # if silent:
        #     if tag in prepared_data.top_emoji_list:
        #         text = unicode_name(toptag[0])
        # else:
        text = tag
        if silent:
            return selected_postguids_list
        print(f'({self.tnum} of {self.tmax}) '
              f'Found {len(selected_postguids_list)} posts (UPL) '
              f'for tag \'{text}\' ({perc_oftotal_locations:.0f}% '
              f'of total distinct locations in area)', end=" ")
        return selected_postguids_list

    def _getselect_posts(self,
                         selected_postguids_list: List[str]
                         ) -> List[CleanedPost]:
        selected_posts_list = [self.cleaned_post_dict[x]
                               for x in selected_postguids_list]
        return selected_posts_list

    def _get_np_points(self,
                       tag: str = None,
                       silent: bool = None
                       ) -> np.ndarray:
        """Gets numpy array of selected points from tags with latlng

        Args:
            tag: tag to select posts
            silent: if true, no console output (interface mode)

        Returns:
            points: A list of lat/lng points to map
            selected_postguids_list: List of selected post guids
        """
        # no log reporting for selected points
        if silent is None:
            silent = False

        selected_postguids_list = self._getselect_postguids(
            tag, silent=silent)
        # clustering
        if len(selected_postguids_list) < 2:
            return [], selected_postguids_list
        selected_posts_list = self._getselect_posts(
            selected_postguids_list)
        # only used for tag clustering,
        # otherwise (photo location clusters),
        # global vars are used (df, points)
        df = pd.DataFrame(selected_posts_list)
        # converts pandas data to numpy array
        # (limit by list of column-names)
        points = df.as_matrix(['lng', 'lat'])
        # only return preview fig without clustering
        return points

    def cluster_points(self, points,
                       cluster_distance: float,
                       min_span_tree: bool = False,
                       preview_mode: bool = False):
        # cluster data
        # conversion to radians for HDBSCAN
        # (does not support decimal degrees)
        tag_radians_data = np.radians(points)
        # for each tag in overallNumOfUsersPerTag_global.most_common(1000)
        # (descending), calculate HDBSCAN Clusters
        # min_cluster_size default - 5% optimum:
        min_cluster_size = max(
            2, int(((len(points))/100)*5))
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            gen_min_span_tree=min_span_tree,
            allow_single_cluster=True, min_samples=1)
        # clusterer = hdbscan.HDBSCAN(
        #                   min_cluster_size=minClusterSize,
        #                   gen_min_span_tree=True,
        #                   min_samples=1)
        # clusterer = hdbscan.HDBSCAN(
        #                   min_cluster_size=10,
        #                   metric='haversine',
        #                   gen_min_span_tree=False,
        #                   allow_single_cluster=True)
        # clusterer = hdbscan.robust_single_linkage_.RobustSingleLinkage(
        #                   cut=0.000035)
        # srsl_plt = hdbscan.robust_single_linkage_.plot()
        # Start clusterer on different thread
        # to prevent GUI from freezing, see:
        # http://stupidpythonideas.blogspot.de/2013/10/why-your-gui-app-freezes.html
        # https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
        # if preview_mode:
        #    #on preview_mode command line operation,
        #    #don't use multiprocessing
        #    clusterer = fit_cluster(clusterer,tagRadiansData)
        # else:
        with warnings.catch_warnings():
            # disable joblist multithread warning
            warnings.simplefilter('ignore', UserWarning)
            async_result = pool.apply_async(
                Utils.fit_cluster, (self.clusterer, tag_radians_data))
            self.clusterer = async_result.get()
            # clusterer.fit(tagRadiansData)
            # updateNeeded = False
        if self.autoselect_clusters:
            cluster_labels = self.clusterer.labels_  # auto selected clusters
        else:
            # min_cluster_size:
            # 0.000035 without haversine: 223 m (or 95 m for 0.000015)
            cluster_labels = self.clusterer.single_linkage_tree_.get_clusters(
                Utils.get_radians_from_meters(
                    cluster_distance), min_cluster_size=2)
        # exit function in case final processing loop (no figure generating)
        if not preview_mode:
            return cluster_labels

        self.mask_noisy = (cluster_labels == -1)
        # len(sel_labels)
        self.number_of_clusters = len(
            np.unique(cluster_labels[~self.mask_noisy]))  # nopep8 false positive? pylint: disable=E1130
        # palette = sns.color_palette("hls", )
        # palette = sns.color_palette(None, len(sel_labels))
        # #sns.color_palette("hls", ) #sns.color_palette(None, 100)
        palette = sns.color_palette("husl", self.number_of_clusters+1)
        # clusterer.labels_ (best selection) or sel_labels (cut distance)
        self.sel_colors = [palette[x] if x >= 0
                           else (0.5, 0.5, 0.5)
                           # for x in clusterer.labels_ ]
                           for x in cluster_labels]
        # no need to return actual clusters if in manual mode
        # self.mask_noisy, self.number_of_clusters and
        # self.sel_colors will be used to gen preview map
        return None

def cluster_all(self):
    """Cluster all data attached to self
    """
    noClusterPhotos_perTag_DictOfLists = defaultdict(list)
    clustersPerTag = defaultdict(list)
    # Proceed with clustering all tags
    # data always in lat/lng WGS1984
    crs_wgs = pyproj.Proj(init='epsg:4326')
    if cfg.override_crs is None:
        # Calculate best UTM Zone SRID/EPSG Code
        # True centroid (coords may be multipoint):
        input_lon_center = self.bound_points_shapely.centroid.coords[0][0]
        input_lat_center = self.bound_points_shapely.centroid.coords[0][1]
        epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
        crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}')
    project = lambda x, y: pyproj.transform(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init=f'epsg:{epsg_code}'), x, y)
    #geom_proj = transform(project, alphaShapeAndMeta[0])

    if cfg.local_saturation_check:
        clusters, selected_post_guids = cluster_tag(prepared_data.single_mostused_tag, None, True)
        numpy_selectedPhotoList_Guids = np.asarray(selected_post_guids)
        mask_noisy = (clusters == -1)
        number_of_clusters = len(np.unique(clusters[~mask_noisy]))
        print(f'--> {number_of_clusters} cluster.')
        clusterPhotosGuidsList = []
        for x in range(number_of_clusters):
            currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
            clusterPhotosGuidsList.append(currentClusterPhotoGuids)
        noClusterPhotos_perTag_DictOfLists[prepared_data.single_mostused_tag[0]] = list(numpy_selectedPhotoList_Guids[clusters==-1])
        # Sort descending based on size of cluster: https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
        clusterPhotosGuidsList.sort(key=len, reverse=True)
        if not len(clusterPhotosGuidsList) == 0:
            clustersPerTag[prepared_data.single_mostused_tag[0]] = clusterPhotosGuidsList
    global tnum
    tnum = 1
    for toptag in top_tags_list:
        if cfg.local_saturation_check and tnum == 1 and toptag[0] in clustersPerTag:
            #skip toptag if already clustered due to local saturation
            continue
        clusters, selected_post_guids = cluster_tag(toptag, None, True)
        #print("baseDataList: ")
        #print(str(type(selectedPhotoList)))
        #for s in selectedPhotoList[:2]:
        #    print(*s)
        #print("resultData: ")
        ##for s in clusters[:2]:
        ##    print(*s)
        #print(str(type(clusters)))
        #print(clusters)
        #clusters contains the cluster values (-1 = no cluster, 0 maybe, >0 = cluster
        # in the same order, selectedPhotoList contains all original photo data, thus clusters[10] and selectedPhotoList[10] refer to the same photo

        numpy_selectedPhotoList_Guids = np.asarray(selected_post_guids)
        mask_noisy = (clusters == -1)
        if len(selected_post_guids) == 1:
            number_of_clusters = 0
        else:
            number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
        #if number_of_clusters > 200:
        #    log.info("--> Too many, skipped for this scale.")
        #    continue
        if not number_of_clusters == 0:
            print(f'--> {number_of_clusters} cluster.')
            tnum += 1
            photo_num = 0
            #clusternum_photolist = zip(clusters,selectedPhotoList)
            #clusterPhotosList = [[] for x in range(number_of_clusters)]
            clusterPhotosGuidsList = []
            for x in range(number_of_clusters):
                currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
                clusterPhotosGuidsList.append(currentClusterPhotoGuids)
            noClusterPhotos_perTag_DictOfLists[toptag[0]] = list(numpy_selectedPhotoList_Guids[clusters==-1])
            # Sort descending based on size of cluster: https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
            clusterPhotosGuidsList.sort(key=len, reverse=True)
            if not len(clusterPhotosGuidsList) == 0:
                clustersPerTag[toptag[0]] = clusterPhotosGuidsList
        else:
            print("--> No cluster.")
            noClusterPhotos_perTag_DictOfLists[toptag[0]] = list(numpy_selectedPhotoList_Guids)
        #for x in clusters:
        #    #photolist = []
        #    if x >= 0: # no clusters: x = -1
        #        clusterPhotosList[x].append([selectedPhotoList[photo_num]])
        #        #clusterPhotosArray_dict[x].add(selectedPhotoList[photo_num])
        #    else:
        #        noClusterPhotos_perTag_DictOfLists[toptag[0]].append(selectedPhotoList[photo_num])
        #    photo_num+=1

        #print("resultList: ")
        #for s in clusterPhotosList[:2]:
        #    print(*s)
        #print(str(toptag) + " - Number of clusters: " + str(len(clusterPhotosList)) + " Photo num: " + str(photo_num))

        #plt.autoscale(enable=True)

        #if tnum == 50:
        #    break
            #plt.savefig('foo.png')
            #sys.exit()
    sys.stdout.flush()
    log.info("########## STEP 4 of 6: Generating Alpha Shapes ##########")
    #if (tnum % 50 == 0):#modulo: if division has no remainder, force update cmd output
    #sys.stdout.flush()
    #for each cluster of points, calculate boundary shape and add statistics (HImpTag etc.)
    listOfAlphashapesAndMeta = []
    tnum = 0
    if cfg.local_saturation_check:
        #calculate total area of Top1-Tag for 80% saturation check for lower level tags
        saturationExcludeCount = 0
        clusterPhotoGuidList = clustersPerTag.get(prepared_data.single_mostused_tag[0], None)
        #print("Toptag: " + str(singleMostUsedtag[0]))
        if clusterPhotoGuidList is None:
            sys.exit(f'No Photos found for toptag: {singleMostUsedtag}')
        toptagArea = Utils.generateClusterShape(toptag,clusterPhotoGuidList,cleaned_post_dict,crs_wgs,crs_proj,clusterTreeCuttingDist,cfg.local_saturation_check)[1]
    for toptag in top_tags_list:
        tnum += 1
        clusterPhotoGuidList = clustersPerTag.get(toptag[0], None)
        #Generate tag Cluster Shapes
        if clusterPhotoGuidList:
            listOfAlphashapesAndMeta_tmp,tagArea = Utils.generateClusterShape(toptag,clusterPhotoGuidList,cleaned_post_dict,crs_wgs,crs_proj,clusterTreeCuttingDist,cfg.local_saturation_check)
            if cfg.local_saturation_check and not tagArea == 0 and not tnum == 1:
                localSaturation = tagArea/(toptagArea/100)
                #print("Local Saturation for Tag " + toptag[0] + ": " + str(round(localSaturation,0)))
                if localSaturation > 60:
                    #skip tag entirely due to saturation (if total area > 80% of total area of toptag clusters)
                    #print("Skipped: " + toptag[0] + " due to saturation (" + str(round(localSaturation,0)) + "%).")
                    saturationExcludeCount += 1
                    continue #next toptag

            if len(listOfAlphashapesAndMeta_tmp) > 0:
                listOfAlphashapesAndMeta.extend(listOfAlphashapesAndMeta_tmp)

        singlePhotoGuidList = noClusterPhotos_perTag_DictOfLists.get(toptag[0], None)
        if singlePhotoGuidList:
            shapetype = "Single cluster"
            #print("Single: " + str(len(singlePhotoGuidList)))
            photos = [cleaned_post_dict[x] for x in singlePhotoGuidList]
            for single_photo in photos:
                #project lat/lng to UTM
                x, y = pyproj.transform(crs_wgs, crs_proj, single_photo.lng, single_photo.lat)
                pcoordinate = geometry.Point(x, y)
                result_polygon = pcoordinate.buffer(clusterTreeCuttingDist/4,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                #result_polygon = pcoordinate.buffer(min(distXLng,distYLat)/100,resolution=3)
                if result_polygon is not None and not result_polygon.is_empty:
                    listOfAlphashapesAndMeta.append((result_polygon,1,max(single_photo.post_views_count,single_photo.post_like_count),1,str(toptag[0]),toptag[1],1,1,1,shapetype))
    log.info(f'{len(listOfAlphashapesAndMeta)} Alpha Shapes. Done.')
    if cfg.local_saturation_check and not saturationExcludeCount == 0:
        log.info(f'Excluded {saturationExcludeCount} Tags on local saturation check.')
    ##Output Boundary Shapes in merged Shapefile##
    log.info("########## STEP 5 of 6: Writing Results to Shapefile ##########")

    #Calculate best UTM Zone SRID/EPSG Code
    input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
    input_lat_center = bound_points_shapely.centroid.coords[0][1]
    epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
    project = lambda x, y: pyproj.transform(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:{0}'.format(epsg_code)), x, y)

    # Define polygon feature geometry
    schema = {
        'geometry': 'Polygon',
        'properties': {'Join_Count': 'int',
                       'Views': 'int',
                       'COUNT_User': 'int',
                       'ImpTag': 'str',
                       'TagCountG': 'int',
                       'HImpTag': 'int',
                       'Weights': 'float',
                       'WeightsV2': 'float',
                       'WeightsV3': 'float',
                       #'shapetype': 'str',
                       'emoji': 'int'},
    }

    #Normalization of Values (1-1000 Range), precalc Step:
    #######################################
    weightsv1_range = [x[6] for x in listOfAlphashapesAndMeta] #get the n'th column out for calculating the max/min
    weightsv2_range = [x[7] for x in listOfAlphashapesAndMeta]
    weightsv3_range = [x[8] for x in listOfAlphashapesAndMeta]
    weightsv1_min = min(weightsv1_range)
    weightsv1_max = max(weightsv1_range)
    weightsv2_min = min(weightsv2_range)
    weightsv2_max = max(weightsv2_range)
    weightsv3_min = min(weightsv3_range)
    weightsv3_max = max(weightsv3_range)
    #precalc
    #https://stats.stackexchange.com/questions/70801/how-to-normalize-data-to-0-1-range
    weightsv1_mod_a = (1000-1)/(weightsv1_max-weightsv1_min)
    weightsv1_mod_b = 1000 - weightsv1_mod_a * weightsv1_max
    weightsv2_mod_a = (1000-1)/(weightsv2_max-weightsv2_min)
    weightsv2_mod_b = 1000 - weightsv2_mod_a * weightsv2_max
    weightsv3_mod_a = (1000-1)/(weightsv3_max-weightsv3_min)
    weightsv3_mod_b = 1000 - weightsv3_mod_a * weightsv3_max
    #######################################
    # Write a new Shapefile
    # WGS1984
    if (cfg.cluster_tags == False and cfg.cluster_emoji == True):
        shapefileName = "allEmojiCluster"
    else:
        shapefileName = "allTagCluster"
    with fiona.open(f'02_Output/{shapefileName}.shp', mode='w', encoding='UTF-8', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
        # Normalize Weights to 0-1000 Range
        idx = 0
        for alphaShapeAndMeta in listOfAlphashapesAndMeta:
            if idx == 0:
                HImP = 1
            else:
                if listOfAlphashapesAndMeta[idx][4] != listOfAlphashapesAndMeta[idx-1][4]:
                    HImP = 1
                else:
                    HImP = 0
            #emoName = unicode_name(alphaShapeAndMeta[4])
            #Calculate Normalized Weights Values based on precalc Step
            if not alphaShapeAndMeta[6] == 1:
                weight1_normalized = weightsv1_mod_a * alphaShapeAndMeta[6] + weightsv1_mod_b
            else:
                weight1_normalized = 1
            if not alphaShapeAndMeta[7] == 1:
                weight2_normalized = weightsv2_mod_a * alphaShapeAndMeta[7] + weightsv2_mod_b
            else:
                weight2_normalized = 1
            if not alphaShapeAndMeta[8] == 1:
                weight3_normalized = weightsv3_mod_a * alphaShapeAndMeta[8] + weightsv3_mod_b
            else:
                weight3_normalized = 1
            idx += 1
            #project data
            #geom_proj = transform(project, alphaShapeAndMeta[0])
            #c.write({
            #    'geometry': geometry.mapping(geom_proj),
            if cfg.cluster_emoji and alphaShapeAndMeta[4] in prepared_data.top_emoji_list:
                emoji = 1
                ImpTagText = ""
            else:
                emoji = 0
                ImpTagText = f'{alphaShapeAndMeta[4]}'
            c.write({
                'geometry': geometry.mapping(alphaShapeAndMeta[0]),
                'properties': {'Join_Count': alphaShapeAndMeta[1],
                               'Views': alphaShapeAndMeta[2],
                               'COUNT_User': alphaShapeAndMeta[3],
                               'ImpTag': ImpTagText,
                               'TagCountG': alphaShapeAndMeta[5],
                               'HImpTag': HImP,
                               'Weights': weight1_normalized,
                               'WeightsV2': weight2_normalized,
                               'WeightsV3': weight3_normalized,
                               #'shapetype': alphaShapeAndMeta[9],
                               'emoji': emoji},
            })
    if cfg.cluster_emoji:
        with open("02_Output/emojiTable.csv", "w", encoding='utf-8') as emojiTable:
            emojiTable.write("FID,Emoji\n")
            idx = 0
            for alphaShapeAndMeta in listOfAlphashapesAndMeta:
                if alphaShapeAndMeta[4] in prepared_data.top_emoji_list:
                    ImpTagText = f'{alphaShapeAndMeta[4]}'
                else:
                    ImpTagText = ""
                emojiTable.write(f'{idx},{ImpTagText}\n')
                idx += 1
