# -*- coding: utf-8 -*-

"""
Module for tag maps clustering methods
"""

import logging
import sys
import warnings
from collections import defaultdict
from multiprocessing.pool import ThreadPool
from typing import Any, Dict, List, Optional, Set, TextIO, Tuple

import fiona
import numpy as np
import pandas as pd
import pyproj
import seaborn as sns
import shapely.geometry as geometry

from tagmaps.classes.alpha_shapes import AlphaShapes
from tagmaps.classes.shared_structure import (EMOJI, LOCATIONS, TAGS,
                                              AnalysisBounds, CleanedPost,
                                              ClusterType, PreparedData)
from tagmaps.classes.utils import Utils

with warnings.catch_warnings():
    # disable:
    # parallel.py:268: DeprecationWarning:
    # check_pickle is deprecated in joblib 0.12
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import hdbscan

pool = ThreadPool(processes=1)
sns.set_context('poster')
sns.set_style('white')


class ClusterGen():
    """Cluster methods for tags, emoji and post locations
    """

    def __init__(self, bounds: AnalysisBounds,
                 cleaned_post_dict: Dict[str, CleanedPost],
                 cleaned_post_list: List[CleanedPost],
                 top_list: List[Tuple[str, int]],
                 total_distinct_locations: int,
                 cluster_type: ClusterType = TAGS,
                 # topitem: Tuple[str, int] = None,
                 local_saturation_check: bool = True):
        self.cls_type = cluster_type
        self.tnum = 0
        self.tmax = len(top_list)
        self.bounds = bounds
        self.cluster_distance = ClusterGen._init_cluster_dist(
            self.bounds, self.cls_type)
        self.cleaned_post_dict = cleaned_post_dict
        self.cleaned_post_list = cleaned_post_list
        self.top_list = top_list
        self.top_item = top_list[0]
        self.total_distinct_locations = total_distinct_locations
        self.autoselect_clusters = False
        self.sel_colors = None
        self.number_of_clusters = None
        self.mask_noisy = None
        self.clusterer = None
        self.local_saturation_check = local_saturation_check
        # storing cluster results:
        self.single_items_dict = defaultdict(list)
        self.clustered_items_dict = defaultdict(list)
        self.clustered_guids_all: List[str] = list()
        self.none_clustered_guids: List[str] = list()
        # set initial analysis bounds
        self._update_bounds()
        self.bound_points_shapely = Utils._get_shapely_bounds(
            self.bounds)
        # data always in lat/lng WGS1984
        self.crs_wgs = pyproj.Proj(init='epsg:4326')
        self.crs_proj, __ = Utils._get_best_utmzone(
            self.bound_points_shapely)

    @classmethod
    def new_clusterer(cls,
                      clusterer_type: ClusterType,
                      bounds: AnalysisBounds,
                      cleaned_post_dict: Dict[str, CleanedPost],
                      cleaned_post_list: List[CleanedPost],
                      prepared_data: PreparedData,
                      local_saturation_check: bool):
        """Create new clusterer from type and input data

        Args:
            clusterer_type (ClusterType): Either Tags,
                Locations or Emoji
            bounds (LoadData.AnalysisBounds): Analaysis spatial boundary
            cleaned_post_dict (Dict[str, CleanedPost]): Dict of cleaned posts
            prepared_data (LoadData.PreparedData): Statistics data

        Returns:
            clusterer (ClusterGen): A new clusterer of ClusterType
        """
        if clusterer_type == TAGS:
            top_list = prepared_data.top_tags_list
        elif clusterer_type == EMOJI:
            top_list = prepared_data.top_emoji_list
        elif clusterer_type == LOCATIONS:
            top_list = prepared_data.top_locations_list
        else:
            raise ValueError("Cluster Type unknown.")

        clusterer = cls(
            bounds=bounds,
            cleaned_post_dict=cleaned_post_dict,
            cleaned_post_list=cleaned_post_list,
            top_list=top_list,
            total_distinct_locations=prepared_data.total_unique_locations,
            cluster_type=clusterer_type,
            local_saturation_check=local_saturation_check)
        return clusterer

    @staticmethod
    def _init_cluster_dist(bounds: AnalysisBounds,
                           cls_type: ClusterType) -> float:
        """Get initial cluster distance from analysis bounds.

        - 7% of research area width/height (max) = optimal
        - default value #223.245922725 #= 0.000035 radians dist
        """
        dist_y = Utils.haversine(bounds.lim_lng_min,
                                 bounds.lim_lat_min,
                                 bounds.lim_lng_min,
                                 bounds.lim_lat_max)
        dist_x = Utils.haversine(bounds.lim_lng_min,
                                 bounds.lim_lat_min,
                                 bounds.lim_lng_max,
                                 bounds.lim_lat_min)
        cluster_distance = (min(dist_x, dist_y)/100)*7
        if cls_type == LOCATIONS:
            # since location clustering includes
            # all data, use reduced default distance
            cluster_distance = cluster_distance/8
        return cluster_distance

    def _update_bounds(self):
        """Update analysis rectangle boundary based on

        cleaned posts list."""
        df = pd.DataFrame(self.cleaned_post_list)
        # get columns lng, lat
        # convert to numpy ndarray
        # (List of [lng, lat] lists)
        points = df.loc[:, ['lng', 'lat']].to_numpy()
        (self.bounds.lim_lat_min,
         self.bounds.lim_lat_max,
         self.bounds.lim_lng_min,
         self.bounds.lim_lng_max) = Utils.get_rectangle_bounds(points)

    def _select_postguids(self, item: str) -> Tuple[List[str], int]:
        """Select all posts that have a specific item

        Args:
            item: tag, emoji, location

        Returns:
            Tuple[List[str], int]: list of post_guids and
                                   number of distinct locations
        """
        distinct_localloc_count = set()
        selected_postguids_list = list()
        for cleaned_photo_location in self.cleaned_post_list:
            if self.cls_type == TAGS:
                self._filter_tags(
                    item, cleaned_photo_location,
                    selected_postguids_list,
                    distinct_localloc_count)
            elif self.cls_type == EMOJI:
                self._filter_emoji(
                    item, cleaned_photo_location,
                    selected_postguids_list,
                    distinct_localloc_count)
            elif self.cls_type == LOCATIONS:
                self._filter_locations(
                    item, cleaned_photo_location,
                    selected_postguids_list,
                    distinct_localloc_count)
            else:
                raise ValueError(f"Clusterer {self.cls_type} unknown.")
        return selected_postguids_list, len(distinct_localloc_count)

    @staticmethod
    def _filter_tags(
            item: str,
            cleaned_photo_location: CleanedPost,
            selected_postguids_list: List[str],
            distinct_localloc_count: Set[str]):
        if (item in (cleaned_photo_location.hashtags) or
                (item in cleaned_photo_location.post_body)):
            selected_postguids_list.append(
                cleaned_photo_location.guid)
            distinct_localloc_count.add(
                cleaned_photo_location.loc_id)

    @staticmethod
    def _filter_emoji(
            item: str,
            cleaned_photo_location: CleanedPost,
            selected_postguids_list: List[str],
            distinct_localloc_count: Set[str]):
        if item in cleaned_photo_location.emoji:
            selected_postguids_list.append(
                cleaned_photo_location.guid)
            distinct_localloc_count.add(
                cleaned_photo_location.loc_id)

    @staticmethod
    def _filter_locations(
            item: str,
            cleaned_photo_location: CleanedPost,
            selected_postguids_list: List[str],
            distinct_localloc_count: Set[str]):
        if item == cleaned_photo_location.loc_id:
            selected_postguids_list.append(
                cleaned_photo_location.guid)
            distinct_localloc_count.add(
                cleaned_photo_location.loc_id)

    def _getselect_postguids(self, item: str,
                             silent: bool = True) -> List[str]:
        """Get list of post guids with specific item

        Args:
            item: tag, emoji, location
        """
        query_result = self._select_postguids(item)
        selected_postguids_list = query_result[0]
        distinct_localloc_count = query_result[1]

        if silent:
            return selected_postguids_list
        # console reporting
        if self.cls_type == EMOJI:
            item_text = Utils._get_emojiname(item)
        else:
            item_text = item
        type_text = self.cls_type.rstrip('s')
        perc_oftotal_locations = (
            distinct_localloc_count /
            (self.total_distinct_locations/100)
        )
        perc_text = ""
        if perc_oftotal_locations >= 1:
            perc_text = (f'(found in {perc_oftotal_locations:.0f}% '
                         f'of DLC in area)')
        print(f'({self.tnum} of {self.tmax}) '
              f'Found {len(selected_postguids_list)} posts (UPL) '
              f'for {type_text} \'{item_text}\' '
              f'{perc_text}', end=" ")
        return selected_postguids_list

    def _getselect_posts(self,
                         selected_postguids_list: List[str]
                         ) -> List[CleanedPost]:
        selected_posts_list = [self.cleaned_post_dict[x]
                               for x in selected_postguids_list]
        return selected_posts_list

    def _get_np_points_guids(self,
                             item: str = None,
                             silent: bool = None,
                             sel_all: bool = None
                             ) -> np.ndarray:
        """Gets numpy array of selected points with latlng containing _item

        Args:
            item: tag, emoji, location
            silent: if true, no console output (interface mode)

        Returns:
            points: A list of lat/lng points to map
            selected_postguids_list: List of selected post guids
        """
        # no log reporting for selected points
        if silent is None:
            silent = False
        if sel_all is None:
            sel_all = False
        if sel_all:
            # select all post guids
            selected_postguids_list = list()
            for cleaned_post in self.cleaned_post_list:
                selected_postguids_list.append(
                    cleaned_post.guid)
            selected_posts_list = self.cleaned_post_list
        else:
            selected_postguids_list = self._getselect_postguids(
                item, silent=silent)
            # clustering
            if len(selected_postguids_list) < 2:
                # return empty list of points
                return [], selected_postguids_list
            selected_posts_list = self._getselect_posts(
                selected_postguids_list)
        # only used for tag clustering,
        # otherwise (photo location clusters),
        # global vars are used (df, points)
        df = pd.DataFrame(selected_posts_list)
        # converts pandas data to numpy array
        # (limit by list of column-names)
        points = df.loc[:, ['lng', 'lat']].to_numpy()
        # only return preview fig without clustering
        return points, selected_postguids_list

    def _get_np_points(self,
                       item: str = None,
                       silent: bool = None
                       ) -> np.ndarray:
        """Wrapper that only returns points for _get_np_points_guids"""
        points, __ = self._get_np_points_guids(item, silent)
        if len(points) > 0:
            return points

    def _cluster_points(self, points,
                        min_span_tree: bool = None,
                        preview_mode: bool = None,
                        min_cluster_size: int = None,
                        allow_single_cluster: bool = True):
        if min_span_tree is None:
            min_span_tree = False
        if preview_mode is None:
            preview_mode = False
        if allow_single_cluster is None:
            allow_single_cluster = True
        # cluster data
        # conversion to radians for HDBSCAN
        # (does not support decimal degrees)
        tag_radians_data = np.radians(points)  # pylint: disable=E1111
        # for each tag in overallNumOfUsersPerTag_global.most_common(1000)
        # (descending), calculate HDBSCAN Clusters
        # min_cluster_size default - 5% optimum:
        if min_cluster_size is None:
            min_cluster_size = max(
                2, int(((len(points))/100)*5))
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            gen_min_span_tree=min_span_tree,
            allow_single_cluster=allow_single_cluster,
            min_samples=1)
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
                ClusterGen._fit_cluster, (self.clusterer, tag_radians_data))
            self.clusterer = async_result.get()
            # clusterer.fit(tagRadiansData)
            # updateNeeded = False
        if self.autoselect_clusters:
            cluster_labels = self.clusterer.labels_  # auto selected clusters
        else:
            # min_cluster_size:
            # 0.000035 without haversine: 223 m (or 95 m for 0.000015)
            cluster_labels = self.clusterer.single_linkage_tree_.get_clusters(
                Utils._get_radians_from_meters(
                    self.cluster_distance), min_cluster_size=2)
        # exit function in case of
        # final processing loop (no figure generating)
        if not preview_mode:
            return cluster_labels
        # verbose reporting if preview mode
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

    def _cluster_item(self, sel_item: Tuple[str, int]):
        """Cluster specific item"""

        result = self._get_np_points_guids(
            item=sel_item[0], silent=False)
        points = result[0]
        selected_post_guids = result[1]
        if len(selected_post_guids) < 2:
            return
        clusters = self._cluster_points(
            points=points, preview_mode=False)
        return clusters, selected_post_guids

    def _cluster_all_items(self):
        """Cluster all items (e.g. all locations)"""
        result = self._get_np_points_guids(
            silent=False, sel_all=True)
        points = result[0]
        selected_post_guids = result[1]
        # min_cluster_size = 2 (LOCATIONS)
        # do not allow clusters with one item
        if len(selected_post_guids) < 2:
            return
        clusters = self._cluster_points(
            points=points, preview_mode=False,
            min_cluster_size=2, allow_single_cluster=False)
        return clusters, selected_post_guids

    @staticmethod
    def _get_cluster_guids(clusters, selected_post_guids):
        """Returns two lists: clustered and non clustered guids"""
        clustered_guids = list()
        np_selected_post_guids = np.asarray(selected_post_guids)
        mask_noisy = (clusters == -1)
        if len(selected_post_guids) == 1:
            number_of_clusters = 0
        else:
            number_of_clusters = len(np.unique(clusters[~mask_noisy]))
        if number_of_clusters == 0:
            print("--> No cluster.")
            none_clustered_guids = list(np_selected_post_guids)
        else:
            print(f'--> {number_of_clusters} cluster.')
            for x in range(number_of_clusters):
                current_clustered_guids = np_selected_post_guids[clusters == x]
                clustered_guids.append(current_clustered_guids)
            none_clustered_guids = list(np_selected_post_guids[clusters == -1])
            # Sort descending based on size of cluster
            # https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
            clustered_guids.sort(key=len, reverse=True)
        return clustered_guids, none_clustered_guids

    def _get_update_clusters(self, item: Tuple[str, int] = None,
                             single_items_dict=None,
                             cluster_items_dict=None,
                             itemized: bool = None):
        """Get clusters for items and write results to dicts"""
        if itemized is None:
            # default
            itemized = True
        if itemized:
            cluster_results = self._cluster_item(item)
        else:
            cluster_results = self._cluster_all_items()
        if not cluster_results:
            print("--> No cluster (all locations removed).")
            return
        clusters = cluster_results[0]
        selected_post_guids = cluster_results[1]
        # get clustered guids/ non-clustered guids
        result = self._get_cluster_guids(clusters, selected_post_guids)
        clustered_guids = result[0]
        none_clustered_guids = result[1]
        if itemized:
            self.single_items_dict[item[0]] = none_clustered_guids
            if not len(clustered_guids) == 0:
                self.clustered_items_dict[item[0]] = clustered_guids
            # dicts modified in place, no need to return
            return
        else:
            self.clustered_guids_all = clustered_guids
            self.none_clustered_guids = none_clustered_guids

    def get_overall_clusters(self):
        """Get clusters for all items attached to self

        Updates results as two lists:
            self.clustered_guids_all
            self.none_clustered_guids
        """
        # update in case of locations removed
        # self.cleaned_post_list = list(
        #     self.cleaned_post_dict.values())
        self._get_update_clusters(itemized=False)

    def get_itemized_clusters(self):
        """Get itemized clusters for top_list attached to self

        Updates results as two Dict of Lists:
            self.single_items_dict
            self.clustered_items_dict
        """
        # update in case of items
        # have been removed from top_list
        self.tmax = len(self.top_list)
        # get clusters for top item
        if self.local_saturation_check:
            self._get_update_clusters(
                item=self.top_item)
        self.tnum = 0
        # get remaining clusters
        for item in self.top_list:
            if (self.local_saturation_check and
                    self.tnum == 0 and
                    self.top_item in self.clustered_items_dict):
                # skip topitem if already
                # clustered due to local saturation
                continue
            self.tnum += 1
            self._get_update_clusters(
                item=item)
        # logging.getLogger("tagmaps").info(
        #    f'{len(self.clustered_items)} '
        #    f'{self.cls_type.rstrip("s")} clusters.\n'
        #    f'{len(self.single_items)} without neighbors.')
        # flush console output once
        sys.stdout.flush()

    def get_cluster_centroids(self):
        """Get centroids for clustered data"""
        itemized = False
        resultshapes_and_meta = list()
        for post_cluster in self.clustered_guids_all:
            posts = [self.cleaned_post_dict[x] for x in post_cluster]
            unique_user_count = len(set([post.user_guid for post in posts]))
            # get points and project coordinates to suitable UTM
            points = [geometry.Point(
                pyproj.transform(self.crs_wgs, self.crs_proj,
                                 post.lng, post.lat)
            ) for post in posts]
            point_collection = geometry.MultiPoint(list(points))
            # convex hull enough for calculating centroid
            result_polygon = point_collection.convex_hull
            result_centroid = result_polygon.centroid
            if result_centroid is not None and not result_centroid.is_empty:
                resultshapes_and_meta.append(
                    (result_centroid, unique_user_count)
                )
        # noclusterphotos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
        for no_cluster_post in self.none_clustered_guids:
            post = self.cleaned_post_dict[no_cluster_post]
            x, y = pyproj.transform(self.crs_wgs, self.crs_proj,
                                    post.lng, post.lat)
            p_center = geometry.Point(x, y)
            if p_center is not None and not p_center.is_empty:
                resultshapes_and_meta.append((p_center, 1))
        sys.stdout.flush()
        # log.debug(f'{resultshapes_and_meta[:10]}')
        return resultshapes_and_meta, self.cls_type, itemized

    def _get_item_clustershapes(
            self,
            item: Tuple[str, int]) -> Tuple[List[Tuple[Any]], float]:
        """Get Cluster Shapes from a list of coordinates
        for a given item"""
        clustered_post_guids = self.clustered_items_dict.get(
            item[0], None)
        if not clustered_post_guids:
            return None, 0
        result = AlphaShapes.get_cluster_shape(
            item, clustered_post_guids, self.cleaned_post_dict,
            self.crs_wgs, self.crs_proj, self.cluster_distance,
            self.local_saturation_check)
        cluster_shapes = result[0]
        cluster_shapes_area = result[1]
        return cluster_shapes, cluster_shapes_area

    def _get_item_clusterarea(
            self,
            item: Tuple[str, int]) -> float:
        """Wrapper: only get cluster shape area for item"""
        __, cluster_shapes_area = self._get_item_clustershapes(item)
        return cluster_shapes_area

    @staticmethod
    def _is_saturated_item(
            item_area: float,
            topitem_area: float):
        """Skip item entirely if saturated, i.e.
        if total area > 80%
        of top item cluster area

        Args:
            item_area: item cluster area
            topitem_area: top item cluster area
        """
        local_saturation = item_area/(topitem_area/100)
        # print("Local Saturation for Tag " + self.top_item "
        #       "+ ": " + str(round(localSaturation,0)))
        if local_saturation > 60:
            return True
        else:
            return False

    def _get_item_shapeslist(self, item, topitem_area, tnum):
        """Get all item shapes for item clusters"""
        resultshapes_and_meta_tmp = list()
        result = self._get_item_clustershapes(item)
        shapes_tmp = result[0]
        item_area = result[1]
        if (self.local_saturation_check
                and not item_area == 0
                and not tnum == 1):
            if self._is_saturated_item(item_area,
                                       topitem_area):
                # next item
                return None
        # append result
        if shapes_tmp and len(shapes_tmp) > 0:
            resultshapes_and_meta_tmp.extend(
                shapes_tmp)
        # get shapes for single items (non-clustered)
        none_clustered_guids = self.single_items_dict.get(
            item[0], None)
        if not none_clustered_guids:
            return resultshapes_and_meta_tmp
        posts = [self.cleaned_post_dict[x]
                 for x in none_clustered_guids]
        for single_post in posts:
            shapes_single_tmp = AlphaShapes._get_single_cluster_shape(
                item, single_post, self.crs_wgs,
                self.crs_proj, self.cluster_distance)
            if not shapes_single_tmp:
                continue
            # Use append, since always single Tuple
            resultshapes_and_meta_tmp.append(
                shapes_single_tmp)
        return resultshapes_and_meta_tmp

    def get_cluster_shapes(self):
        """For each cluster of points,
        calculate boundary shape and
        add statistics (HImpTag etc.)

        Returns results as shapes_and_meta
        = list(), ClusterType, itemized = bool
        """
        itemized = True
        saturation_exclude_count = 0
        shapes_and_meta = list()
        tnum = 0
        topitem_area = None
        if self.local_saturation_check:
            # calculate total area of Top1-Tag
            # for 80% saturation check for lower level tags
            topitem_area = self._get_item_clusterarea(
                self.top_item)
            if topitem_area == 0:
                raise ValueError(
                    f'Something went wrong: '
                    f'Could not get area for Top item '
                    f'{self.top_item}')
        for item in self.top_list:
            tnum += 1
            shapes_tmp = self._get_item_shapeslist(
                item, topitem_area, tnum)
            if shapes_tmp is None:
                saturation_exclude_count += 1
                continue
            if len(shapes_tmp) == 0:
                continue
            shapes_and_meta.extend(shapes_tmp)
        logging.getLogger("tagmaps").info(
            f'{len(shapes_and_meta)} '
            f'alpha shapes. Done.')
        if saturation_exclude_count > 0:
            logging.getLogger("tagmaps").info(
                f'Excluded {saturation_exclude_count} '
                f'{self.cls_type.rstrip("s")} on local saturation check.')
        return shapes_and_meta, self.cls_type, itemized

    @staticmethod
    def _fit_cluster(clusterer, data):
        """Perform HDBSCAN clustering from features or distance matrix.

        Args:
            clusterer ([type]): HDBScan clusterer
            data ([type]): A feature array (points)

        Returns:
            [type]: Clusterer
        """

        clusterer.fit(data)
        return clusterer
