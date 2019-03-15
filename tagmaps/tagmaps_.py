"""
TagMaps: Tag, Emoji and Location clustering
         from spatially referenced and tagged records
"""

from __future__ import absolute_import

import logging
from typing import Dict

from .classes.cluster import ClusterGen
from .classes.compile_output import Compile
from .classes.interface import UserInterface
from .classes.prepare_data import PrepareData
from .classes.shared_structure import (EMOJI, LOCATIONS, TAGS, TOPICS,
                                       ClusterType, PostStructure)
from .classes.utils import Utils

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"


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

    output_folder : Path, optional (default=None)
        optionally provide a path (Pathlib Path object) for storing
        output files, e.g. Path.cwd() / "02_Output"/.

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

    class TMDec():
        """Decorators for checking states in TagMaps class"""
        @staticmethod
        def init_data_check(func):
            """Check if lbsn_data has been initialized"""

            def _wrapper(self, *args, **kwargs):
                # init lbsn data
                if self.lbsn_data is None:
                    self.init_lbsn_data()
                return func(self, *args, **kwargs)
            return _wrapper

        @staticmethod
        def prepare_clustering_check(func):
            """Check if clusters have been initialized"""

            def _wrapper(self, *args, **kwargs):
                # add clusterer
                if not self.clusterer:
                    self.init_cluster()
                return func(self, *args, **kwargs)
            return _wrapper

        @staticmethod
        def data_added_check(func):
            """Check if (any) data has been added"""

            def _wrapper(self, *args, **kwargs):
                if kwargs and "input_path" in kwargs:
                    input_path = kwargs['input_path']
                    # first check if input_path present in args
                    # return function
                    # if input_path present
                    # (load intermediate data mode)
                    if input_path:
                        return func(self, *args, **kwargs)
                # check if data has been added
                if not self.lbsn_data or self.lbsn_data.count_glob == 0:
                    raise ValueError(
                        "No data records available. "
                        "Add records with tagmaps.add_record() first.")
                return func(self, *args, **kwargs)
            return _wrapper

        @staticmethod
        def prepare_data_check(func):
            """Check if data has been prepared"""

            def _wrapper(self):
                # prepare stats
                if self.cleaned_stats is None:
                    self.prepare_data()
                func(self)
            return _wrapper

    def __init__(
            self, tag_cluster=True, emoji_cluster=True,
            location_cluster=True,
            output_folder=None, remove_long_tail=True,
            limit_bottom_user_count=5, topic_modeling=False,
            local_saturation_check=False, max_items=None,
            logging_level=None, topic_cluster=None):
        """Init settings for Tag Maps Clustering"""
        self.output_folder = output_folder
        self.remove_long_tail = remove_long_tail
        self.limit_bottom_user_count = limit_bottom_user_count
        self.topic_modeling = topic_modeling
        if max_items is None:
            max_items = 1000
        if topic_cluster is None:
            topic_cluster = False
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
        if topic_cluster:
            self.cluster_types.append(TOPICS)
        # create output dir if not exists
        Utils.init_output_dir(self.output_folder)
        # init logger (logging to console and file log.txt)
        if logging_level is None:
            logging_level = logging.INFO
        self.log = Utils.set_logger(self.output_folder, logging_level)
        # data structures for clustering
        self.lbsn_data: PrepareData = None
        self.cleaned_post_dict = None
        self.cleaned_post_list = None
        self.cleaned_stats = None
        self.clusterer: Dict[ClusterType, ClusterGen] = dict()
        self.itemized_cluster_shapes = list()
        self.global_cluster_centroids = list()

    @TMDec.init_data_check
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
        self.lbsn_data.add_record(record)

    def init_lbsn_data(self):
        """init PrepareData structure"""
        self.lbsn_data = PrepareData(
            cluster_types=self.cluster_types,
            max_items=self.max_items,
            output_folder=self.output_folder,
            remove_long_tail=self.remove_long_tail,
            limit_bottom_user_count=self.limit_bottom_user_count,
            topic_modeling=self.topic_modeling)

    @TMDec.data_added_check
    def global_stats_report(self, cleaned=None):
        """Report global stats after data has been read"""
        if cleaned is None:
            cleaned = False
        self.lbsn_data.global_stats_report(cleaned=cleaned)

    @TMDec.data_added_check
    @TMDec.init_data_check
    def prepare_data(self, input_path=None):
        """Prepare data and metrics for use in clustering.
        Optional: provide input_path to cleaned data will load
        preprocessed data
        """
        # get cleaned data for use in clustering
        if not self.cleaned_post_dict:
            self.cleaned_post_dict = self.lbsn_data.get_cleaned_post_dict(
                input_path)
        # a list is faster for looping through,
        # a dict is faster for key lookup,
        # get both here
        self.cleaned_post_list = list(self.cleaned_post_dict.values())
        # get prepared data for statistics and clustering
        self.cleaned_stats = self.lbsn_data.get_item_stats()

    @TMDec.init_data_check
    def load_intermediate(self, input_path):
        """Load data from intermediate (already filtered) data"""
        self.cleaned_post_dict = self.lbsn_data.get_cleaned_post_dict(
            input_path)

    @TMDec.prepare_data_check
    @TMDec.data_added_check
    def item_stats_report(self):
        """Stats reporting for tags, emoji (and locations)"""
        location_name_count = len(
            self.lbsn_data.locid_locname_dict)
        if location_name_count:
            self.log.info(
                f"Number of locations with names: "
                f"{location_name_count}")
        self.log.info(
            f'Total distinct tags (DTC): '
            f'{self.cleaned_stats[TAGS].total_unique_items}')
        self.log.info(
            f'Total distinct emoji (DEC): '
            f'{self.cleaned_stats[EMOJI].total_unique_items}')
        self.log.info(
            f'Total distinct locations (DLC): '
            f'{self.cleaned_stats[LOCATIONS].total_unique_items}')
        self.log.info(
            f'Total tag count for the '
            f'{self.cleaned_stats[TAGS].max_items} '
            f'most used tags in selected area: '
            f'{self.cleaned_stats[TAGS].total_item_count}.')
        self.log.info(
            f'Total emoji count for the '
            f'{self.cleaned_stats[EMOJI].max_items} '
            f'most used emoji in selected area: '
            f'{self.cleaned_stats[EMOJI].total_item_count}.')
        self.log.info(
            self.lbsn_data.bounds.get_bound_report())

    @TMDec.prepare_data_check
    @TMDec.data_added_check
    def init_cluster(self):
        """Initialize clusterers after base data
        has been loaded"""
        for cls_type in self.cluster_types:
            clusterer = ClusterGen.new_clusterer(
                cls_type=cls_type,
                bounds=self.lbsn_data.bounds,
                cleaned_post_dict=self.cleaned_post_dict,
                cleaned_post_list=self.cleaned_post_list,
                cleaned_stats=self.cleaned_stats,
                local_saturation_check=self.local_saturation_check
            )
            self.clusterer[cls_type] = clusterer

    @TMDec.prepare_clustering_check
    def user_interface(self):
        """Opens interface for optional user input to:
        - remove tags, emoji or locations from processing list
        - adjust cluster distances

        Returns False or True, depending on optional user Quit()
        """
        # init user interface
        user_intf = UserInterface(
            self.clusterer.values(),
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

    @TMDec.prepare_clustering_check
    def _cluster(self, cluster_type: ClusterType,
                 itemized=True):
        """Run clusterer based on type and output

        Itemized:  Gets clusters for each item
        otherwise: Gets global clusters for all
                   locations.
        """
        clusterer = self.clusterer.get(cluster_type)
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
        clusterer = self.clusterer.get(cluster_type)
        cluster_shapes = clusterer.get_cluster_shapes()
        # store results for tags and emoji in one list
        self.itemized_cluster_shapes.append(cluster_shapes)

    def _cluster_centroids(self, cluster_type):
        """Calculates cluster centroids"""
        clusterer = self.clusterer.get(cluster_type)
        cluster_results = clusterer.get_all_cluster_centroids()
        self.global_cluster_centroids.append(cluster_results)

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
        if self.output_folder is None:
            raise ValueError(
                "Please provide output folder "
                "(tagmaps.output_folder is none).")
        Compile.write_shapes(
            bounds=self.lbsn_data.bounds,
            shapes_and_meta_list=shapelist,
            output_folder=self.output_folder
        )

    @TMDec.prepare_clustering_check
    def get_selection_map(self, cls_type: ClusterType, item):
        """Return plt.figure for item selection."""
        fig = self.clusterer[cls_type].get_sel_preview(item)
        return fig

    @TMDec.prepare_clustering_check
    def get_cluster_map(self, cls_type: ClusterType, item):
        """Return plt.figure for item clusters."""
        fig = self.clusterer[cls_type].get_cluster_preview(item)
        return fig

    @TMDec.prepare_clustering_check
    def get_cluster_shapes_map(self, cls_type: ClusterType, item):
        """Return plt.figure for item cluster shapes."""
        fig = self.clusterer[cls_type].get_clustershapes_preview(item)
        return fig

    @TMDec.prepare_clustering_check
    def get_singlelinkagetree_preview(self, cls_type: ClusterType, item):
        """Return plt.figure for item cluster shapes."""
        fig = self.clusterer[cls_type].get_singlelinkagetree_preview(item)
        return fig

    @TMDec.init_data_check
    def write_toplists(self):
        """Write toplists for items to output"""
        self.lbsn_data.write_toplists()

    def write_cleaned_data(self):
        """Write cleaned data to file for intermediate results store"""
        self.lbsn_data.write_cleaned_data(self.cleaned_post_dict)

    @TMDec.prepare_data_check
    def write_topics(self):
        """Write topics to file (e.g. for advanced topic modeling)"""
        self.lbsn_data.write_topic_models()

    @TMDec.init_data_check
    def get_pseudo_anonymized_data(self):
        """Returns dict of cleaned posts with removed
        personal information.


        E.g. without terms and tags that are not collectively
        relevant to users. This is the
        reduced data that is finally used to generate tagmaps.
        """
        panon_cleaned_post_dict = self.lbsn_data.get_panonymized_posts(
            self.cleaned_post_dict)
        return panon_cleaned_post_dict
