# -*- coding: utf-8 -*-

"""
Module for tag maps clustering methods
"""

from __future__ import absolute_import

import logging
import queue
import sys
import threading
from collections import defaultdict
from dataclasses import astuple, dataclass
from functools import wraps
from typing import Dict, List, Optional, Set, Tuple

import hdbscan
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shapely.geometry as geometry
from pyproj import Transformer  # pylint: disable=C0412
from shapely.ops import transform  # pylint: disable=C0412
from tagmaps.classes.alpha_shapes import (AlphaShapes, AlphaShapesAndMeta,
                                          AlphaShapesArea)
from tagmaps.classes.plotting import TPLT
from tagmaps.classes.prepare_data import PreparedStats
from tagmaps.classes.shared_structure import (EMOJI, LOCATIONS, POST_FIELDS,
                                              TAGS, TOPICS, AnalysisBounds,
                                              CleanedPost, ItemCounter)
from tagmaps.classes.utils import Utils

# init threaded cluster queue
cluster_queue = queue.Queue()

sns.set_context('poster')
sns.set_style('white')


@dataclass
class SelectedItems:
    guids: List[str]
    location_count: int


@dataclass
class Guids:
    clustered: List[str]
    nonclustered: List[str]


@dataclass
class SelItems:
    """List of coordinates (points) with related post_guids"""
    points: List[Optional[np.ndarray]]
    guids: List[str]


@dataclass
class ClusterResults:
    """List of post guids and assigned cluster labels (from HDBSCAN)"""
    clusters: Tuple[np.ndarray, Tuple[int, Optional[int]]]
    guids: List[str]
    points: Optional[List[np.ndarray]] = None
    colors: Optional[List[Tuple[float, float, float]]] = None
    mask_noisy: Optional[np.ndarray] = None
    cluster_count: Optional[int] = None

    def __iter__(self):
        return iter(astuple(self))


def store_in_queue(f):
    """Decorator to store function in threaded queue"""
    def wrapper(*args):
        cluster_queue.put(f(*args))
    return wrapper


@dataclass
class ClusterShapes:
    """Count of user per cluster centroid

    data: List of Tuples with
          (1) Point = cluster centroid and
          (2) int = user count
    cls_type: cluster type (TAGS, EMOJI, ..)
    itemized: bool
              False: Overall Location clusters
              True: Itemoized clusters (TAGS, EMOJI)
    """
    data: List[Tuple[geometry.Point, int]]
    cls_type: str
    itemized: bool

    def __iter__(self):
        return iter(astuple(self))


class ClusterGen():
    """Cluster methods for tags, emoji and post locations

    Note that there are three different projections used here:

    1. Input: Original Data in Decimal Degrees (WGS1984)
    2. Intermediate: Radians data converted from Decimal Degrees with
    np.radians(points) for use in HDBSCAN clustering
    3. Output: Projected coordinates based on auto-selected UTM Zone,
    for calculating Alpha Shapes and writing results to
    shapefile
    """
    class CGDec():
        """Decorators for class CG methods"""
        @staticmethod
        def input_topic_format(func):
            """Check if cluster type is topic and if,
                concat item list to string."""
            @wraps(func)
            def _wrapper(self, item, **kwargs):
                if self.cls_type == TOPICS:
                    if isinstance(item, list):
                        item = Utils.concat_topic(item)
                    elif not '-' in item:
                        raise ValueError(
                            "Please supply either list of terms, or"
                            "concatenate terms with '-' character.")
                return func(self, item, **kwargs)
            return _wrapper

    def __init__(self, bounds: AnalysisBounds,
                 cleaned_post_dict: Optional[Dict[str, CleanedPost]],
                 cleaned_post_list: Optional[List[CleanedPost]],
                 top_list: List[ItemCounter],
                 total_distinct_locations: int,
                 cluster_type: str = TAGS,
                 local_saturation_check: bool = False):
        self.cls_type = cluster_type
        self.bounds = bounds
        self.cluster_distance: float = ClusterGen._init_cluster_dist(
            self.bounds, self.cls_type)
        self.cleaned_post_dict = cleaned_post_dict
        self.cleaned_post_list = cleaned_post_list
        self.top_list = top_list
        self.top_item: Optional[ItemCounter]
        if self.top_list:
            self.top_item = top_list[0]  # TODO: check 2nd [0]
        else:
            self.top_item = None
        self.total_distinct_locations = total_distinct_locations
        self.autoselect_clusters = False  # no cluster distance needed
        self.clusterer = None
        self.local_saturation_check = local_saturation_check
        # storing cluster results:
        self.single_items_dict = defaultdict(list)
        self.clustered_items_dict = defaultdict(list)
        self.clustered_guids_all: List[str] = list()
        self.none_clustered_guids: List[str] = list()
        # get initial analysis bounds in Decimal Degrees
        # for calculating output UTM Zone Projection
        self._update_bounds()
        self.bound_points_shapely = Utils.get_shapely_bounds(
            self.bounds)
        # verify that PROJ_LIB exists,
        # only necessary for pyproj < 2.0.0
        # Utils.set_proj_dir()
        # input data always in lat/lng WGS1984
        # define input and UTM projections
        self.crs_wgs = "epsg:4326"
        self.crs_proj, __ = Utils.get_best_utmzone(
            self.bound_points_shapely)
        # define projection function ahead
        # for reasons of speed
        # always_xy ensures traditional order of
        # coordinates (lng, lat), see also:
        # https://gis.stackexchange.com/a/326919/33092
        self.proj_transformer = Transformer.from_crs(
            self.crs_wgs, self.crs_proj, always_xy=True)
        self.proj_transformer_back = Transformer.from_crs(
            self.crs_proj, self.crs_wgs, always_xy=True)

    @classmethod
    def new_clusterer(cls,
                      cls_type: str,
                      bounds: AnalysisBounds,
                      cleaned_post_dict: Optional[Dict[str, CleanedPost]],
                      cleaned_post_list: Optional[List[CleanedPost]],
                      cleaned_stats: Optional[Dict[str, PreparedStats]],
                      local_saturation_check: bool):
        """Create new clusterer from type and input data

        Args:
            cls_type (ClusterType): Either TAGS,
                LOCATIONS, TOPICS or EMOJI
            bounds (LoadData.AnalysisBounds): Analaysis spatial boundary
            cleaned_post_dict (Dict[str, CleanedPost]): Dict of cleaned posts
            prepared_data (LoadData.PreparedData): Statistics data

        Returns:
            clusterer (ClusterGen): A new clusterer of ClusterType
        """
        cls_cleaned_stats = cleaned_stats.get(cls_type)
        if not cls_cleaned_stats:
            raise ValueError("Cleaned_stats not initialized")
        clusterer = cls(
            bounds=bounds,
            cleaned_post_dict=cleaned_post_dict,
            cleaned_post_list=cleaned_post_list,
            top_list=cls_cleaned_stats.top_items_list,
            total_distinct_locations=cleaned_stats[
                LOCATIONS].total_unique_items,
            cluster_type=cls_type,
            local_saturation_check=local_saturation_check)
        return clusterer

    @staticmethod
    def _init_cluster_dist(bounds: AnalysisBounds,
                           cls_type: str) -> float:
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

        dataframe = pd.DataFrame(self.cleaned_post_list, columns=POST_FIELDS)
        # get columns lng, lat
        # convert to numpy ndarray
        # (List of [lng, lat] lists)
        points = dataframe.loc[:, ['lng', 'lat']].to_numpy()
        (self.bounds.lim_lat_min,
         self.bounds.lim_lat_max,
         self.bounds.lim_lng_min,
         self.bounds.lim_lng_max) = Utils.get_rectangle_bounds(points)

    def _select_postguids(self, item: Optional[str]) -> SelectedItems:
        """Select all posts that have a specific item

        Args:
            item: tag, emoji, location

        Returns:
            selected_items: list of post_guids and
                            number of distinct locations
        """
        distinct_localloc_count = set()
        selected_postguids_list = list()
        for cleaned_post_location in self.cleaned_post_list:
            if self.cls_type == TAGS:
                self._filter_tags(
                    item, cleaned_post_location,
                    selected_postguids_list,
                    distinct_localloc_count)
            elif self.cls_type == EMOJI:
                self._filter_emoji(
                    item, cleaned_post_location,
                    selected_postguids_list,
                    distinct_localloc_count)
            elif self.cls_type == LOCATIONS:
                self._filter_locations(
                    item, cleaned_post_location,
                    selected_postguids_list,
                    distinct_localloc_count)
            elif self.cls_type == TOPICS:
                self._filter_topics(
                    item, cleaned_post_location,
                    selected_postguids_list,
                    distinct_localloc_count)
            else:
                raise ValueError(f"Clusterer {self.cls_type} unknown.")
        selected_items = SelectedItems(
            selected_postguids_list, len(distinct_localloc_count))
        return selected_items

    @staticmethod
    def _filter_tags(
            item: Optional[str],
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
    def _filter_topics(
            item: Optional[str],
            cleaned_photo_location: CleanedPost,
            selected_postguids_list: List[str],
            distinct_localloc_count: Set[str]):
        """Check topics against tags, body and emoji"""
        item_list = Utils.split_topic(item)
        if (ClusterGen._compare_anyinlist(
                item_list, cleaned_photo_location.hashtags)
                or ClusterGen._compare_anyinlist(
                    item_list, cleaned_photo_location.post_body)
                or ClusterGen._compare_anyinlist(
                    item_list, cleaned_photo_location.emoji)):
            selected_postguids_list.append(
                cleaned_photo_location.guid)
            distinct_localloc_count.add(
                cleaned_photo_location.loc_id)

    @staticmethod
    def _compare_anyinlist(items, item_list):
        """Check if any term of topic is in list"""
        if any(x in items for x in item_list):
            return True
        return False

    @staticmethod
    def _filter_emoji(
            item: Optional[str],
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
            item: Optional[str],
            cleaned_photo_location: CleanedPost,
            selected_postguids_list: List[str],
            distinct_localloc_count: Set[str]):
        if item == cleaned_photo_location.loc_id:
            selected_postguids_list.append(
                cleaned_photo_location.guid)
            distinct_localloc_count.add(
                cleaned_photo_location.loc_id)

    def _getselect_postguids(self, item: Optional[str],
                             silent: bool = True) -> List[str]:
        """Get list of post guids with specific item

        Args:
            item: tag, emoji, location
        """
        sel_items = self._select_postguids(item)
        if silent:
            return sel_items.guids
        # console reporting
        if self.cls_type == EMOJI:
            item_text = Utils.get_emojiname(item)
        else:
            item_text = item
        type_text = self.cls_type.rstrip('s')
        perc_oftotal_locations = (
            sel_items.location_count /
            (self.total_distinct_locations/100)
        )
        perc_text = ""
        if perc_oftotal_locations >= 1:
            perc_text = (f'(found in {perc_oftotal_locations:.0f}% '
                         f'of DLC in area)')
        item_index_pos = self._get_toplist_index(item) + 1
        print(f"({item_index_pos} of {len(self.top_list)}) "
              f"Found {len(sel_items.guids)} posts (UPL) "
              f"for {type_text} '{item_text}' "
              f"{perc_text}", end=" ")
        return sel_items.guids

    def _get_toplist_index(self, item_text: Optional[str]) -> int:
        """Get Position of Item in Toplist"""
        try:
            index_pos = Utils.get_index_of_item(
                self.top_list, item_text)
        except ValueError:
            index_pos = 0
        return index_pos

    def _getselect_posts(self,
                         selected_postguids_list: List[str]
                         ) -> List[CleanedPost]:
        selected_posts_list = [self.cleaned_post_dict[x]
                               for x in selected_postguids_list]
        return selected_posts_list

    def get_np_points_guids(self, item: Optional[str] = None,
                            silent: bool = None, sel_all: bool = None
                            ) -> SelItems:
        """Gets numpy array of selected points with latlng containing _item

        Args:
            item: tag, emoji, location; or topic (list of terms)
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
                return SelItems([], selected_postguids_list)
            selected_posts_list = self._getselect_posts(
                selected_postguids_list)
        # only used for tag clustering,
        # otherwise (photo location clusters),
        # global vars are used (dataframe, points)
        dataframe = pd.DataFrame(selected_posts_list, columns=POST_FIELDS)
        # converts pandas data to numpy array
        # (limit by list of column-names)
        points = dataframe.loc[:, ['lng', 'lat']].to_numpy()
        # only return preview fig without clustering
        return SelItems(points, selected_postguids_list)

    def get_np_points(self, item: str = None, silent: bool = None
                      ) -> np.ndarray:
        """Wrapper that only returns points for _get_np_points_guids"""
        # decide if select all or specific item
        sel_all = bool(item is None)
        sel_items = self.get_np_points_guids(item, silent, sel_all)
        # ndarray.size: Number of elements in the array
        if len(sel_items.points) > 0 and sel_items.points.size:
            return sel_items.points

    def _cluster_points(self, points,
                        min_span_tree: bool = None,
                        preview_mode: bool = None,
                        min_cluster_size: int = None,
                        allow_single_cluster: bool = True):
        """Cluster points using HDBSCAN"""
        if min_span_tree is None:
            min_span_tree = False
        if preview_mode is None:
            preview_mode = False
        if allow_single_cluster is None:
            allow_single_cluster = True
        # conversion to radians for HDBSCAN
        tag_radians_data = np.radians(points)  # pylint: disable=E1111
        if min_cluster_size is None:
            min_cluster_size = max(
                2, int(((len(points))/100)*5))
        # init hdbscan clusterer
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            gen_min_span_tree=min_span_tree,
            allow_single_cluster=allow_single_cluster,
            min_samples=1)
        # Start clusterer on different thread
        # to prevent GUI from freezing
        t = threading.Thread(
            target=ClusterGen._fit_cluster,
            args=(clusterer, tag_radians_data),
            group=None,
            name="tm-clustering",
        )
        t.start()
        self.clusterer = cluster_queue.get()

        if self.autoselect_clusters:
            cluster_labels = self.clusterer.labels_
        else:
            cluster_labels = self.clusterer.single_linkage_tree_.get_clusters(
                Utils.get_radians_from_meters(
                    self.cluster_distance), min_cluster_size=2)
        # exit function in case of
        # final processing loop (no figure generating)
        if not preview_mode:
            return cluster_labels, None, None, None
        # verbose reporting if preview mode
        mask_noisy = (cluster_labels == -1)
        number_of_clusters = len(
            np.unique(cluster_labels[~mask_noisy]))  # nopep8 false positive? pylint: disable=E1130
        palette = sns.color_palette("husl", number_of_clusters+1)
        sel_colors = [palette[x] if x >= 0
                      else (0.5, 0.5, 0.5)
                      # for x in clusterer.labels_ ]
                      for x in cluster_labels]
        # return additional information in preview mode
        # for plotting
        return cluster_labels, sel_colors, mask_noisy, number_of_clusters

    def cluster_item(
            self, item: Optional[str],
            preview_mode=None) -> Optional[ClusterResults]:
        """Cluster specific item

        Args:
            item (str): The item to select and cluster
            preview_mode ([type], optional): Defaults to None. If True,
                sel_colors, mask_noisy, number_of_clusters will be returned,
                which can be used as additional information during plot

        Returns:
            clusters: The cluster labels returned from HDBSCAN
            selected_post_guids: All selected post guids for item
            points: numpy.ndarray of selected post coordinates (radians)
            sel_colors: color codes assigned to points for plotting clusters
            mask_noisy: number of clusters that were ambiguous (from HDBSCAN)
            number_of_clusters: number of identified clusters (from HDBSCAN)
        """
        if preview_mode is None:
            preview_mode = False
        sel_items = self.get_np_points_guids(
            item=item, silent=preview_mode)

        if len(sel_items.guids) < 2:
            # no need to cluster
            return None
        (clusters, sel_colors,
         mask_noisy, number_of_clusters) = self._cluster_points(
             points=sel_items.points, preview_mode=preview_mode)
        return ClusterResults(
            clusters, sel_items.guids,
            sel_items.points, sel_colors, mask_noisy, number_of_clusters)

    def _cluster_all_items(self):
        """Cluster all items (e.g. all locations)"""
        sel_items = self.get_np_points_guids(
            silent=False, sel_all=True)
        # min_cluster_size = 2 (LOCATIONS)
        # do not allow clusters with one item
        if len(sel_items.guids) < 2:
            return
        cluster_labels, _, _, _ = self._cluster_points(
            points=sel_items.points, preview_mode=False,
            min_cluster_size=2, allow_single_cluster=False)
        return ClusterResults(cluster_labels, sel_items.guids)

    @staticmethod
    def _get_cluster_guids(clusters, selected_post_guids) -> Guids:
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
            for cluster_x in range(number_of_clusters):
                current_clustered_guids = np_selected_post_guids[clusters == cluster_x]
                clustered_guids.append(current_clustered_guids)
            none_clustered_guids = list(np_selected_post_guids[clusters == -1])
            # Sort descending based on size of cluster
            # this is needed to later compute HImp Value (1 or 0)
            clustered_guids.sort(key=len, reverse=True)
        return Guids(clustered_guids, none_clustered_guids)

    def _get_update_clusters(self, item: Optional[str] = None,
                             single_items_dict=None,
                             cluster_items_dict=None,
                             itemized: bool = None):
        """Get clusters for items and write results to dicts"""
        if not single_items_dict:
            single_items_dict = self.single_items_dict
        if not cluster_items_dict:
            cluster_items_dict = self.clustered_items_dict
        if itemized is None:
            # default
            itemized = True
        if itemized:
            # clusters guids points colors mask_noisy cluster_count
            cluster = self.cluster_item(item)
        else:
            cluster = self._cluster_all_items()
        if not cluster:
            print("--> No cluster (all locations removed).")
            return
        # get clustered guids/ non-clustered guids
        guids = self._get_cluster_guids(cluster.clusters, cluster.guids)
        if itemized:
            single_items_dict[item] = guids.nonclustered
            if guids.clustered:
                cluster_items_dict[item] = guids.clustered
            # dicts modified in place, no need to return
            return
        else:
            self.clustered_guids_all = guids.clustered
            self.none_clustered_guids = guids.nonclustered

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
        # get clusters for top item
        if self.local_saturation_check:
            self._get_update_clusters(
                item=self.top_item.name)  # TODO: test .name
        tnum = 0
        # get remaining clusters
        for item in self.top_list:
            if (self.local_saturation_check and
                    tnum == 0):
                # skip topitem if already
                # clustered due to local saturation
                continue
            tnum += 1
            self._get_update_clusters(
                item=item.name)
        # logging.getLogger("tagmaps").info(
        #    f'{len(self.clustered_items)} '
        #    f'{self.cls_type.rstrip("s")} clusters.\n'
        #    f'{len(self.single_items)} without neighbors.')
        # flush console output once
        sys.stdout.flush()

    def get_all_cluster_centroids(self) -> ClusterShapes:
        """Get all centroids for clustered data

        Returns:
            PreparedStats: Results as named tuple
                        data: shapes and meta information
                        cls_type: ClusterGen [EMOJI, TAGS etc.)
                        itemized: bool
        """

        itemized = False
        cluster_guids = self.clustered_guids_all
        none_clustered_guids = self.none_clustered_guids
        resultshapes_and_meta = self.get_cluster_centroids(
            cluster_guids, none_clustered_guids)
        return ClusterShapes(resultshapes_and_meta, self.cls_type, itemized)

    def get_item_cluster_centroids(self, item, single_clusters=None):
        """Get centroids for item clustered data"""
        if single_clusters is None:
            single_clusters = True
        self._get_update_clusters(
            item=item)
        cluster_guids = self.clustered_items_dict[item]
        if single_clusters:
            none_clustered_guids = self.single_items_dict[item]
        else:
            none_clustered_guids = None
        resultshapes_and_meta = self.get_cluster_centroids(
            cluster_guids, none_clustered_guids)
        return resultshapes_and_meta

    def _proj_coords(self, lng: float, lat: float):
        """Project coordinates based on available packages

        pyproj.transformer needs pyproj > 2.0.0,
        which provides a more convenient and faster way to
        project many coordinates.
        """
        lng_proj, lat_proj = self.proj_transformer.transform(
            lng, lat)
        return lng_proj, lat_proj

    def get_cluster_centroids(
            self, clustered_guids,
            none_clustered_guids=None) -> List[Tuple[geometry.Point, int]]:
        """Get centroids for clustered data

        This method needs refactor, since it produces as sparse version of
        AlphaShapesAndMeta (only geometry and user_count) -> create specific
        dataclass
        """
        resultshapes_and_meta = list()
        for post_cluster in clustered_guids:
            posts = [self.cleaned_post_dict[x] for x in post_cluster]
            unique_user_count = len(set([post.user_guid for post in posts]))
            # get points and project coordinates to suitable UTM
            points = [geometry.Point(
                self._proj_coords(post.lng, post.lat)
            ) for post in posts]
            point_collection = geometry.MultiPoint(list(points))
            # convex hull enough for calculating centroid
            result_polygon = point_collection.convex_hull
            result_centroid = result_polygon.centroid
            if result_centroid is not None and not result_centroid.is_empty:
                resultshapes_and_meta.append(
                    (result_centroid, unique_user_count)
                )
        if not none_clustered_guids:
            return resultshapes_and_meta
        # noclusterphotos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
        for no_cluster_post in none_clustered_guids:
            post = self.cleaned_post_dict[no_cluster_post]
            x_point, y_point = self._proj_coords(
                post.lng, post.lat)
            p_center = geometry.Point(x_point, y_point)
            if p_center is not None and not p_center.is_empty:
                resultshapes_and_meta.append((p_center, 1))
        sys.stdout.flush()
        # log.debug(f'{resultshapes_and_meta[:10]}')
        return resultshapes_and_meta

    def _get_item_clustershapes(
            self,
            item: ItemCounter,
            cluster_guids=None) -> AlphaShapesArea:
        """Get Cluster Shapes from a list of coordinates
        for a given item"""
        if cluster_guids is None:
            cluster_guids = self.clustered_items_dict.get(
                item.name, None)
        if not cluster_guids:
            return AlphaShapesArea(None, 0)
        alphashapes_data = AlphaShapes.get_cluster_shape(
            item=item,
            clustered_post_guids=cluster_guids,
            cleaned_post_dict=self.cleaned_post_dict,
            cluster_distance=self.cluster_distance,
            local_saturation_check=self.local_saturation_check,
            proj_coords=self._proj_coords)
        return alphashapes_data

    def _get_item_clusterarea(
            self,
            item: ItemCounter) -> float:
        """Wrapper: only get cluster shape area for item"""
        alphashape_data = self._get_item_clustershapes(item)
        return alphashape_data.item_area

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

    def _get_item_shapeslist(
            self, item, topitem_area,
            tnum) -> Optional[List[List[AlphaShapesAndMeta]]]:
        """Get all item shapes for item clusters

        Note: A function ref to self._proj_coords is handed
        to AlphaShapes.get_single_cluster_shape(). Coordinates are then
        projected inside AlphaShapes Class, depending on the pyproj version.
        """
        resultshapes_and_meta_tmp = list()
        result = self._get_item_clustershapes(item)
        shapes_tmp = result.alphashape
        item_area = result.item_area
        if (self.local_saturation_check
                and item_area != 0
                and tnum != 1):
            if self._is_saturated_item(item_area,
                                       topitem_area):
                # next item
                return None
        # append result
        if shapes_tmp:
            resultshapes_and_meta_tmp.extend(
                shapes_tmp)
        # get shapes for single items (non-clustered)
        none_clustered_guids = self.single_items_dict.get(
            item.name, None)
        if not none_clustered_guids:
            return resultshapes_and_meta_tmp
        posts = [self.cleaned_post_dict[x]
                 for x in none_clustered_guids]
        for single_post in posts:
            shapes_single_tmp = AlphaShapes.get_single_cluster_shape(
                item, single_post, self.cluster_distance,
                self._proj_coords)
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
        if self.local_saturation_check and self.top_item:
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
            if not shapes_tmp:
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
    @store_in_queue
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

    @CGDec.input_topic_format
    def get_sel_preview(self, item):
        """Returns plt map for item selection preview"""
        points = self.get_np_points(
            item=item,
            silent=True)
        fig = TPLT.get_sel_preview(
            points, item, self.bounds, self.cls_type)
        return fig

    @CGDec.input_topic_format
    def get_cluster_centroid_data(
            self, item, zipped=None, projected=None, single_clusters=None):
        """Returns centroids for cluster selection based on item

        Args:
            item (str or list of str): Item to be selected
            zipped ([type], optional): Will merge centroids and user_count,
                                       defaults to False
            projected (bool, optional): Will return projected data (UTM),
                                        otherwise, centroids are returned
                                        in decimal degrees (WGS1984),
                                        defaults to False
            single_clusters: Return single item cluster centroids,
                                        defaults to True

        Returns:
            Tuple: [0] point (List of coordinate pairs),
                   [1] user_count (count of user_count per centroid)
        """
        if zipped is None:
            zipped = False
        if projected is None:
            projected = False
        if single_clusters is None:
            single_clusters = True
        shapes = self.get_item_cluster_centroids(
            item=item, single_clusters=single_clusters)
        points = [meta[0] for meta in shapes]
        user_count = [meta[1] for meta in shapes]
        if not projected:
            # AlphaShapes automatically projects data
            # to compute shapes. If no projection is
            # requested, we have to convert it back to
            # original WGS1984 decimal degrees data
            points = self._project_centroids_back(points)
        # extract centroid coordinates from
        # shapely geometry.Point
        latlng_list = [[point.x, point.y] for point in points]
        # convert coords to numpy.nd array
        points = np.array(latlng_list)
        if zipped:
            zip_list = []
            zip_list = list()
            x_id = 0
            for point in points:
                zip_list.append((point[0], point[1], user_count[x_id]))
                x_id += 1
            result = np.asarray(zip_list)
        else:
            result = (points, user_count)
        return result

    @CGDec.input_topic_format
    def get_cluster_centroid_preview(
            self, item, single_clusters=None) -> plt.figure:
        """Returns plt map for item selection cluster centroids"""
        if single_clusters is None:
            single_clusters = True
        points, user_count = self.get_cluster_centroid_data(
            item=item, single_clusters=single_clusters)
        fig = TPLT.get_centroid_preview(
            points, item, self.bounds, self.cls_type, user_count)
        return fig

    @CGDec.input_topic_format
    def get_cluster_preview(self, item) -> plt.figure:
        """Returns plt map for item cluster preview"""
        points = self.get_np_points(
            item=item,
            silent=True)
        self._cluster_points(
            points=points,
            preview_mode=True)

        clusters = self.cluster_item(
            item=item,
            preview_mode=True)
        if clusters is None:
            return
        fig = TPLT.get_cluster_preview(
            points=clusters.points, sel_colors=clusters.colors, item_text=item,
            bounds=self.bounds, mask_noisy=clusters.mask_noisy,
            cluster_distance=self.cluster_distance,
            number_of_clusters=clusters.cluster_count,
            auto_select_clusters=self.autoselect_clusters,
            cls_type=self.cls_type)
        return fig

    @CGDec.input_topic_format
    def get_clustershapes_preview(self, item) -> plt.figure:
        """Returns plt map for item cluster preview"""
        # selected post guids: all posts for item
        # points: numpy-points for plotting
        # clusters: hdbscan labels for clustered items
        item = ItemCounter(item, 0)
        result = self.cluster_item(
            item=item.name,
            preview_mode=True)
        if result is None:
            return print("No items found.")
        # cluster_guids: those guids that are clustered
        cluster_guids = self._get_cluster_guids(
            result.clusters, result.guids)

        shapes_and_area = self._get_item_clustershapes(
            item, cluster_guids.clustered)
        # get only shapely shapes, not usercount and other info

        shapes = [meta.shape for meta in shapes_and_area.alphashape]
        shapes_wgs = self._project_centroids_back(shapes)
        fig = TPLT.get_cluster_preview(
            points=result.points, sel_colors=result.colors, item_text=item.name,
            bounds=self.bounds, mask_noisy=result.mask_noisy,
            cluster_distance=self.cluster_distance,
            number_of_clusters=result.cluster_count,
            auto_select_clusters=self.autoselect_clusters,
            shapes=shapes_wgs, cls_type=self.cls_type)
        return fig

    def _project_centroids_back(self, shapes):
        """Proj shapes back to WGS1984 for plotting in matplotlib

        simple list comprehension with projection:
        """
        project = self.proj_transformer_back
        shapes_wgs = [(ClusterGen._project_geometry(
            shape, project)) for shape in shapes]
        return shapes_wgs

    @staticmethod
    def _project_geometry(geom_shape, project):
        # geom_shape_proj = project.transform(geom_shape)
        geom_shape_proj = transform(project.transform, geom_shape)
        return geom_shape_proj

    def get_singlelinkagetree_preview(self, item):
        """Returns figure for single linkage tree from HDBSCAN clustering"""
        if self.cls_type == TOPICS:
            item = Utils.concat_topic(item)
        cluster_results = self.cluster_item(
            item=item,
            preview_mode=True)
        axis = self.clusterer.single_linkage_tree_.plot(
            truncate_mode='lastp',
            p=max(50, min(cluster_results.cluster_count*10, 256)))
        fig = TPLT.get_single_linkage_tree_preview(
            item, axis.figure, self.cluster_distance,
            self.cls_type)
        return fig
