# -*- coding: utf-8 -*-


"""
Tag Maps Clustering Package

Package to cluster data (locations, tags or emoji)
and output shapefile containing Alpha Shapes
and statistics.

Package can be executed directly (__main__) or
imported using from tagmaps import tagmaps.TagMaps as TM
"""

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"

import sys
import time
import logging
from pathlib import Path

from tagmaps.classes.cluster import ClusterGen
from tagmaps.classes.compile_output import Compile
from tagmaps.classes.interface import UserInterface
from tagmaps.classes.load_data import LoadData
from tagmaps.classes.prepare_data import PrepareData
from tagmaps.classes.shared_structure import (
    EMOJI, LOCATIONS, TAGS, PostStructure, ClusterType, PreparedStats)
from tagmaps.classes.utils import Utils


def main():
    """Main tag maps method for direct execution of package

    - will read from 01_Input/ folder
    - will output clustered data to 02_Output/
    """

    # initialize config from args
    cfg = Utils.init_main()

    print('\n')
    log = Utils._set_logger(cfg.output_folder)
    log.info(
        "########## "
        "STEP 1 of 6: Data Cleanup "
        "##########")
    input_data = LoadData(cfg)
    # initialize tag maps
    tagmaps = TagMaps(
        cfg.cluster_tags, cfg.cluster_emoji,
        cfg.cluster_locations, cfg.write_cleaned_data,
        cfg.output_folder, cfg.remove_long_tail,
        cfg.limit_bottom_user_count,
        cfg.topic_modeling, cfg.local_saturation_check,
        cfg.max_items)
    # read input records from csv
    with input_data as records:
        for record in records:
            tagmaps.add_record(record)
    # get statistics for input data
    # and indested data
    input_data.input_stats_report()
    tagmaps.global_stats_report()
    # get current time for monitoring
    now = time.time()

    if (cfg.cluster_tags or cfg.cluster_emoji):
        log.info(
            "\n########## "
            "STEP 2 of 6: Tag Ranking "
            "##########")
    # calculate and report item stats
    tagmaps.item_stats_report()

    if cfg.statistics_only is False:
        # restart time monitoring for
        # actual cluster step
        now = time.time()
        log.info(
            "\n########## "
            "STEP 3 of 6: Tag & Emoji "
            "Location Clustering "
            "##########")
        # get user input for cluster distances
        if not cfg.auto_mode:
            # open user interface for optional user input
            continue_proc = tagmaps.user_interface()

        if cfg.auto_mode or continue_proc is True:
            tagmaps.cluster_tags()
            tagmaps.cluster_emoji()
            log.info(
                "########## "
                "STEP 4 of 6: Generating Alpha Shapes "
                "##########")
            tagmaps.gen_tagcluster_shapes()
            tagmaps.gen_emojicluster_shapes()
            log.info(
                "########## "
                "STEP 5 of 6: Writing Results to Shapefile "
                "##########")
            tagmaps.write_tagemoji_shapes()
        else:
            print(f'\nUser abort.')
    if cfg.cluster_locations and continue_proc is True:
        log.info(
            "\n########## "
            "STEP 6 of 6: Calculating Overall Location Clusters "
            "##########")
        tagmaps.cluster_locations()
        tagmaps.gen_location_centroids()
        tagmaps.write_location_shapes()

    # time reporting
    later = time.time()
    hours, rem = divmod(later-now, 3600)
    minutes, seconds = divmod(rem, 60)
    # difference = int(later - now)
    log.info(f'\nDone.\n{int(hours):0>2} Hours '
             f'{int(minutes):0>2} Minutes and '
             f'{seconds:05.2f} Seconds passed.')
    input("Press any key to exit...")
    sys.exit()


class TagMaps():
    """Perform tag clustering from spatially referenced and tagged records.

    TagMaps - Spatial clustering of tagged and spatially referenced records.
    Performs itemized or global clustering based on a list of records with
    multiple tags (or emoji) attached. Utilizes HDBSCAN for determining cluster
    results at specific (optional user defined) distance. Tags, Locations and
    Emoji are processed in descending order of global occurence, alpha
    shapes are generated for cluster point clouds. Produces two output
    shapefiles with cluster shapes that can be visualized, e.g. in ESRI ArcGIS.

    Parameters
    ----------
    tag_cluster : bool, optional (default=True)
        If true, perform tag clustering (based on lists of terms attached to
        records, either identified from #hashtags in
        post_body or from separate .tags column in PostStructure)

    emoji_cluster : bool, optional (default=True)
        If true, perform emoji clustering (based on lists of emoji attached to
        records, either identified from emoji used in
        post_body or from separate .emoji column in PostStructure)

    location_cluster : bool, optional (default=True)
        If true, perform overall location clustering. This will cluster
        all locations in provided records, regardless of tags attached.
        Usefull for visualizing overall frequentation patterns.

    write_cleaned_data : bool, optional (default=False)
        If true, write out a file limited to the cleaned data
        that is finally used for tag clustering
        (filtered records based on stoplists, clipped boundary,
        minimum user threshold etc.)

    output_folder : Path, optional (default=./02_Output/)
        optionally provide a path (Pathlib Path object) for storing
        output files.

    remove_long_tail : bool, optional (default=True)
        Social Media data often shows data that follows the pareto principle,
        also sometimes called Zipf-Curve, or the long tail principle.
        The long tail can be removed to increase speed of clustering,
        since usually clusters will only be found in the top used 20%
        of items used by the majority of users (tags, emoji, location).

    limit_bottom_user_count : int (default=5)
        Any items that are globally used by less than x users will be removed,
        since it is unlikely that there will be any clusters found for those
        items. remove_long_tail must be True for this parameter to take effect.

    topic_modeling : bool (default=False)
        This will used topic modeling to detect groups of tags
        (based on Latent Dirichlet Allocation) Not fully implemented:
        Currently, this will simply output a list of topics; this is not used
        for clustering.

    local_saturation_check : bool (default=False)
        Some tags are used equally often over the whole area of analysis. The
        cluster results for such homogenuous distributed items will usually
        be poor. Such tags often stem from aspects that have their center of
        cluster gravity above the current scale of analysis. If this parameter
        is True, the algorithm will try to identify those tags
        and remove them from clustering.

    max_items : int (default=1000)
        Top x items to cluster. Remove_long_tail must be True for this
        parameter to take effect.
    """

    def __init__(
            self, tag_cluster=True, emoji_cluster=True,
            location_cluster=True, write_cleaned_data=False,
            output_folder=Path.cwd() / "02_Output", remove_long_tail=True,
            limit_bottom_user_count=5, topic_modeling=False,
            local_saturation_check=False, max_items=None):
        """Init settings for Tag Maps Clustering"""
        self.write_cleaned_data = write_cleaned_data
        self.output_folder = output_folder
        self.remove_long_tail = remove_long_tail
        self.limit_bottom_user_count = limit_bottom_user_count
        self.topic_modeling = topic_modeling
        if max_items is None:
            max_items = 1000
        self.max_items = max_items
        self.local_saturation_check = local_saturation_check
        # initialize list of types to cluster
        self.cluster_types = list()
        if tag_cluster:
            self.cluster_types.append(TAGS)
        if emoji_cluster:
            self.cluster_types.append(EMOJI)
        if location_cluster:
            self.cluster_types.append(LOCATIONS)
        # create output dir if not exists
        Utils._init_output_dir(self.output_folder)
        # init logger (logging to console and file log.txt)
        tagmaps_logger = logging.getLogger("tagmaps")
        if tagmaps_logger:
            self.log = tagmaps_logger
        else:
            self.log = Utils._set_logger(self.output_folder)
        # data structures for clustering
        self.lbsn_data: PrepareData = None
        self.cleaned_post_dict = None
        self.cleaned_post_list = None
        self.cleaned_stats: PreparedStats = None
        self.clusterer_list = list()
        self.itemized_cluster_shapes = list()
        self.global_cluster_centroids = list()

    def add_record(self, record: PostStructure):
        """Adds record to input data

        Args:
            record (PostStructure):
            A record with latitude/ longitude
            coordinates and tags/ terms attached.
            This structure provides a wide array of
            input attributes that will be filtered/
            reduced to CleanedPost structure for
            TagMaps clustering
        """
        if self.lbsn_data is None:
            self._init_lbsn_data()
        self.lbsn_data.add_record(record)

    def _init_lbsn_data(self):
        """init PrepareData structure"""
        self.lbsn_data = PrepareData(
            self.cluster_types, self.write_cleaned_data,
            self.max_items, self.output_folder, self.remove_long_tail,
            self.limit_bottom_user_count, self.topic_modeling)

    def global_stats_report(self):
        """Report global stats after data has been read"""
        if not self.lbsn_data:
            raise ValueError(
                "Add data some data first.")
        self.log.info(
            f'Total user count (UC): '
            f'{len(self.lbsn_data.locations_per_userid_dict)}')
        self.log.info(
            f'Total user post locations (UPL): '
            f'{len(self.lbsn_data.distinct_userlocations_set)}')

    def prepare_stats(self):
        """Prepare data and metrics for use in clustering
        """
        if not self.lbsn_data or self.lbsn_data.count_glob == 0:
            raise ValueError(
                "No data records available."
                "Add records with tagmaps.add_record() first.")
        # get cleaned data for use in clustering
        self.cleaned_post_dict = self.lbsn_data.get_cleaned_post_dict()
        # a list is faster for looping through,
        # a dict is faster for key lookup,
        # get both here
        self.cleaned_post_list = list(self.cleaned_post_dict.values())
        # get prepared data for statistics and clustering
        self.cleaned_stats = self.lbsn_data._get_item_stats()

    def item_stats_report(self):
        """Stats reporting for tags, emoji (and locations)"""
        if not self.lbsn_data:
            raise ValueError(
                'No data has been added (use .add_record(record))')
        if self.cleaned_stats is None:
            self.prepare_stats()
        location_name_count = len(
            self.lbsn_data.locid_locname_dict)
        if location_name_count > 0:
            self.log.info(
                f"Number of locations with names: "
                f"{location_name_count}")
        self.log.info(
            f'Total distinct tags (DTC): '
            f'{self.cleaned_stats.total_unique_tags}')
        self.log.info(
            f'Total distinct emoji (DEC): '
            f'{self.cleaned_stats.total_unique_emoji}')
        self.log.info(
            f'Total distinct locations (DLC): '
            f'{self.cleaned_stats.total_unique_locations}')
        self.log.info(
            f'Total tags count for the '
            f'{self.cleaned_stats.tmax} '
            f'most used tags in selected area: '
            f'{self.cleaned_stats.total_tag_count}.')
        self.log.info(
            f'Total emoji count for the '
            f'{self.cleaned_stats.emax} '
            f'most used emoji in selected area: '
            f'{self.cleaned_stats.total_emoji_count}.')
        self.log.info(
            self.lbsn_data.bounds.get_bound_report())

    def _init_cluster(self):
        """Initialize clusterers after base data
        has been loaded"""
        if not self.lbsn_data:
            raise ValueError(
                "No data has been added (use .add_record(record))")
        if self.cleaned_stats is None:
            self.prepare_stats()
        for cls_type in self.cluster_types:
            clusterer = ClusterGen.new_clusterer(
                clusterer_type=cls_type,
                bounds=self.lbsn_data.bounds,
                cleaned_post_dict=self.cleaned_post_dict,
                cleaned_post_list=self.cleaned_post_list,
                cleaned_stats=self.cleaned_stats,
                local_saturation_check=self.local_saturation_check
            )
            self.clusterer_list.append(clusterer)

    def user_interface(self):
        """Opens interface for optional user input to:
        - remove tags, emoji or locations prom processing list
        - adjust cluster distances

        Returns False or True, depending on optional user Quit()
        """
        # init list of clusterers
        if not self.clusterer_list:
            self._init_cluster()
        # init user interface
        user_intf = UserInterface(
            self.clusterer_list,
            self.lbsn_data.locid_locname_dict)
        # start user interface
        user_intf.start()
        # return continue = False or True
        # depending on how user exited interface
        if user_intf.abort is True:
            return False
        return True

    def cluster_tags(self):
        """Calculate all tag clusters"""
        self._cluster(TAGS)

    def cluster_emoji(self):
        """Calculate all emoji clusters"""
        self._cluster(EMOJI)

    def cluster_locations(self):
        """Calculate overall location clusters"""
        self._cluster(LOCATIONS, itemized=False)

    def _cluster(self, cluster_type: ClusterType,
                 itemized=True):
        """Run all clusterer (itermize dor global) based on type"""
        # prepare stats
        if self.cleaned_stats is None:
            self.prepare_stats()
        # add clusterer
        if not self.clusterer_list:
            self._init_cluster()
        for clusterer in self.clusterer_list:
            if clusterer.cls_type == cluster_type:
                self.log.info(f'{cluster_type.rstrip("s")} clustering: ')
                if itemized:
                    clusterer.get_itemized_clusters()
                else:
                    clusterer.get_overall_clusters()

    def gen_location_centroids(self):
        """Generate centroids for location clusters
        """
        self._cluster_centroids(LOCATIONS)

    def gen_tagcluster_shapes(self):
        """Calculate all tag clusters"""
        self._alpha_shapes(TAGS)

    def gen_emojicluster_shapes(self):
        """Calculate all emoji clusters"""
        self._alpha_shapes(EMOJI)

    def _alpha_shapes(self, cluster_type):
        """Calculates alpha shapes for clustered data"""
        for clusterer in self.clusterer_list:
            if clusterer.cls_type == cluster_type:
                cluster_shapes = clusterer.get_cluster_shapes()
                # store results for tags and emoji in one list
                self.itemized_cluster_shapes.append(cluster_shapes)

    def _cluster_centroids(self, cluster_type):
        """Calculates cluster centroids"""
        for clusterer in self.clusterer_list:
            if clusterer.cls_type == cluster_type:
                cluster_shapes = clusterer.get_cluster_centroids()
                self.global_cluster_centroids.append(cluster_shapes)

    def write_tagemoji_shapes(self):
        """Write tag and emoji cluster shapes to shapefile"""
        self._write_shapes(itemized=True)

    def write_location_shapes(self):
        """Write location cluster centroids to shapefile"""
        self._write_shapes(itemized=False)

    def _write_shapes(self, itemized=True):
        """Compile output, normalize and write itemized cluster shapes
        (e.g. Tags/ Emoji) to file"""
        if itemized:
            shapelist = self.itemized_cluster_shapes
        else:
            shapelist = self.global_cluster_centroids
        Compile.write_shapes(
            bounds=self.lbsn_data.bounds,
            shapes_and_meta_list=shapelist
        )


if __name__ == "__main__":
    main()
