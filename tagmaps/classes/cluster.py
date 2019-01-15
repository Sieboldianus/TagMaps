# -*- coding: utf-8 -*-

"""
Module for tag maps clustering functions
"""

import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import hdbscan
from typing import List, Set, Dict, Tuple, Optional, TextIO
import shapely.geometry as geometry
from multiprocessing.pool import ThreadPool
from tagmaps.classes.utils import Utils, AnalysisBounds
from tagmaps.classes.shared_structure import CleanedPost

pool = ThreadPool(processes=1)


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

    def _getselect_postguids(self, tag: str, silent: bool = True):
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

    def _getselect_posts(self, selected_postguids_list):
        selected_posts_list = [self.cleaned_post_dict[x]
                               for x in selected_postguids_list]
        return selected_posts_list

    def _get_np_points(self, tag: str = None, silent: bool = None):
        """Gets numpy array of selected points from tags with latlng

            toptag ([type], optional): Defaults to None. [description]
            silent ([type], optional): Defaults to None. [description]

        Returns:
            [type]: [description]
        """
        # no log reporting for selected points
        if silent is None:
            silent = True

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
        return points, selected_postguids_list

    def cluster_points(self, points, cluster_distance,
                       selected_postguids_list,
                       min_span_tree, silent):
        # cluster data
        # conversion to radians for HDBSCAN
        # (does not support decimal degrees)
        tag_radians_data = np.radians(points)
        # for each tag in overallNumOfUsersPerTag_global.most_common(1000)
        # (descending), calculate HDBSCAN Clusters
        # min_cluster_size default - 5% optimum:
        min_cluster_size = max(
            2, int(((len(selected_postguids_list))/100)*5))
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
        # if silent:
        #    #on silent command line operation,
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
            sel_labels = self.clusterer.labels_  # auto selected clusters
        else:
            # min_cluster_size:
            # 0.000035 without haversine: 223 m (or 95 m for 0.000015)
            sel_labels = self.clusterer.single_linkage_tree_.get_clusters(
                Utils.get_radians_from_meters(
                    cluster_distance), min_cluster_size=2)
        # exit function in case final processing loop (no figure generating)
        if silent:
            return sel_labels, None

        mask_noisy = (sel_labels == -1)
        # len(sel_labels)
        number_of_clusters = len(
            np.unique(sel_labels[~mask_noisy]))
        # palette = sns.color_palette("hls", )
        # palette = sns.color_palette(None, len(sel_labels))
        # #sns.color_palette("hls", ) #sns.color_palette(None, 100)
        palette = sns.color_palette("husl", number_of_clusters+1)
        # clusterer.labels_ (best selection) or sel_labels (cut distance)
        sel_colors = [palette[x] if x >= 0
                      else (0.5, 0.5, 0.5)
                      # for x in clusterer.labels_ ]
                      for x in sel_labels]
        return sel_labels, (mask_noisy, sel_colors, number_of_clusters)
