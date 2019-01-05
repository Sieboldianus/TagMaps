# -*- coding: utf-8 -*-

"""
Module for loading data and calculating basic statistics.
"""

import sys
import os
import ntpath
import csv
from pathlib import Path
from glob import glob
from _csv import QUOTE_MINIMAL
import collections
from collections import Counter
from collections import defaultdict
from collections import namedtuple
from tagmaps.classes.utils import Utils
from lbsntransform.classes.shared_structure_proto_lbsndb import PostAttrShared


class LoadData():
    """Main Class for ingesting data and building summary statistics.

    - will process CSV data into dict/set structures
    - will filter data, cleaned output can be stored
    - will generate statistics
    """

    def __init__(self, cfg):
        """Initializes Load Data structure"""
        self.filelist = self.read_local_files(cfg)
        self.guid_hash = set()  # global list of guids
        self.cleaned_photo_list = []
        self.append_to_already_exist = False  # unused?
        self.shape_exclude_locid_hash = set()
        self.shape_included_locid_hash = set()
        self.total_tag_counter_glob = collections.Counter()
        self.bounds = AnalysisBounds()
        self.stats = DataStats()
        # Hashsets:
        self.locations_per_userid_dict = defaultdict(set)
        self.userlocation_taglist_dict = defaultdict(set)
        if cfg.topic_modeling:
            self.user_topiclist_dict = defaultdict(set)
            self.user_post_ids_dict = defaultdict(set)
            self.userpost_first_thumb_dict = defaultdict(str)
        self.userlocation_wordlist_dict = defaultdict(set)
        self.userlocations_firstphoto_dict = defaultdict(set)
        if cfg.cluster_emoji:
            self.total_emoji_count_global = collections.Counter()
        # UserDict_TagCounters = defaultdict(set)
        self.userdict_tagcounters_global = defaultdict(set)
        # UserIDsPerLocation_dict = defaultdict(set)
        # PhotoLocDict = defaultdict(set)
        self.distinct_locations_set = set()
        self.distinct_userlocations_set = set()
        self.tmax = 1000  # default value

    def parse_input_records(self, cfg):
        """Loops input csv records and adds to records_dict

        Returns statistic-counts, modifies (adds results to) class structures
        """
        # get user input for max tags to process
        self.tmax = self.get_tmax(cfg)

    @staticmethod
    def get_tmax(cfg):
        """User Input to get number of tags to process"""
        if cfg.auto_mode:
            return 1000
        if cfg.cluster_tags or cfg.cluster_emoji:
            inputtext = input(f'Files to process: {len(filelist)}. \nOptional: '
                              f'Enter a Number for the variety of Tags to process '
                              f'(Default is 1000)\nPress Enter to proceed.. \n')
            if inputtext == "" or not inputtext.isdigit():
                return 1000
            else:
                return int(inputtext)

    @staticmethod
    def fetch_csv_data_from_file(source_config):
        """Read csv entries from file (either *.txt or *.csv).

        The actual CSV formatting is not setable in config yet. There are many specifics, e.g.
        #QUOTE_NONE is used here because media saved from Flickr does not contain any quotes ""
        """
        records = []
        loc_file = loc_filelist[start_file_id]
        HF.log_main_debug(f'\nCurrent file: {ntpath.basename(loc_file)}')
        with open(loc_file, 'r', encoding="utf-8", errors='replace') as file:
            reader = csv.reader(file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_NONE)
            next(reader, None)  # skip headerline
            records = list(reader)
        if not records:
            return None
        return records

    @staticmethod
    def read_local_files(config):
        """Read Local Files according to config parameters and returns list of file-paths"""
        input_path = config.input_folder
        filelist = list(input_path.glob(
            f'*.{config.source_map.file_extension}'))
        input_count = len(filelist)
        if input_count == 0:
            sys.exit(f"No input files *.{config.source_map.file_extension} "
                     "found.")
        else:
            return filelist

    @staticmethod
    def skip_empty_or_other(single_record):
        """Detect empty records"""
        if not single_record:
            return False
        return True


class AnalysisBounds():
    """Class stroing boundary (lim lat/lng)"""

    def __init__(self):
        """initialize global variables for analysis bounds

        (lat, lng coordinates)
        """
        self.lim_lat_min = None
        self.lim_lat_max = None
        self.lim_lng_min = None
        self.lim_lng_max = None

    def upd_latlng_bounds(self, lat, lng):
        """Update lat/lng bounds based on coordinate pair."""
        if self.lim_lat_min is None or \
                (lat < self.lim_lat_min and not lat == 0):
            self.lim_lat_min = lat
        if self.lim_lat_max is None or \
                (lat > self.lim_lat_max and not lat == 0):
            self.lim_lat_max = lat
        if self.lim_lng_min is None or \
                (lng < self.lim_lng_min and not lng == 0):
            self.lim_lng_min = lng
        if self.lim_lng_max is None or \
                (lng > self.lim_lng_max and not lng == 0):
            self.lim_lng_max = lng


class DataStats():
    """Class storing analysis stats"""

    def __init__(self):
        """Initialize stats."""
        self.count_non_geotagged = 0
        self.count_outside_shape = 0
        self.count_tags_global = 0
        self.count_emojis_global = 0
        self.count_tags_skipped = 0
        self.skipped_count = 0
        self.count_glob = 0
        self.partcount = 0
        self.count_loc = 0
