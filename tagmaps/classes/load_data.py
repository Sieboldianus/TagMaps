# -*- coding: utf-8 -*-

"""Module for loading data and calculating basic statistics.

Returns:
    PreparedData: Data cleaned for Tag Maps clustering

Todo:
    * separate module into a) load data and b) prepare data
"""


import sys
import os
import ntpath
import csv
import logging
from pathlib import Path
from glob import glob
from _csv import QUOTE_MINIMAL
from decimal import Decimal
import json
import math
import collections
from typing import List, Set, Dict, Tuple, Optional, TextIO
from collections import Counter
from collections import defaultdict
from collections import namedtuple

from shapely.geometry import Polygon
from shapely.geometry import shape
from shapely.geometry import Point
from tagmaps.classes.utils import Utils
from tagmaps.classes.shared_structure import (
    PostStructure, CleanedPost, AnalysisBounds, PreparedData)


class LoadData():
    """Main Class for ingesting data and building summary statistics.

    - will process CSV data into dict/set structures
    - will filter data, cleaned output can be stored
    - will generate statistics
    """

    def __init__(self, cfg):
        """Initializes Load Data structure"""
        self.filelist = self._read_local_files(cfg)
        self.guid_hash = set()  # global list of guids
        self.cleaned_photo_list = []
        self.append_to_already_exist = False  # unused?
        self.shape_exclude_locid_hash = set()
        self.shape_included_locid_hash = set()
        self.total_tag_counter = collections.Counter()
        self.total_emoji_counter = collections.Counter()
        self.total_location_counter = collections.Counter()
        self.bounds = AnalysisBounds()
        self.stats = DataStats()
        self.prepared_data = PreparedData()
        self.cfg = cfg
        self.log = logging.getLogger("tagmaps")
        # Hashsets:
        self.locations_per_userid_dict = defaultdict(set)
        self.userlocation_taglist_dict = defaultdict(set)
        self.userlocation_emojilist_dict = defaultdict(set)
        self.locid_locname_dict: Dict[str, str] = dict()  # nopep8
        if cfg.topic_modeling:
            self.user_topiclist_dict = defaultdict(set)
            self.user_post_ids_dict = defaultdict(set)
            self.userpost_first_thumb_dict = defaultdict(str)
        self.userlocation_wordlist_dict = defaultdict(set)
        self.userlocations_firstpost_dict = defaultdict(set)
        # UserDict_TagCounters = defaultdict(set)
        self.userdict_tagcounters_global = defaultdict(set)
        self.userdict_emojicounters_global = defaultdict(set)
        self.userdict_locationcounters_global = defaultdict(set)
        # UserIDsPerLocation_dict = defaultdict(set)
        # PhotoLocDict = defaultdict(set)
        self.distinct_locations_set = set()
        self.distinct_userlocations_set = set()

    def parse_input_records(self):
        """Loops input csv records and adds to records_dict

        Returns statistic-counts, modifies (adds results to) class structures
        """
        # get user input for max tags to process
        self._get_tmax()
        for file_name in self.filelist:
            with open(file_name, 'r', newline='', encoding='utf8') as f:
                self.stats.partcount += 1
                self._process_inputfile(f)

    def _process_inputfile(self, file_handle):
        """File parse for CSV or JSON

        Output: produces a list of post that can be parsed
        """
        if self.cfg.source_map.file_extension == "csv":
            post_reader = csv.DictReader(
                file_handle,
                delimiter=self.cfg.source_map.delimiter,
                quotechar=self.cfg.source_map.quote_char,
                quoting=self.cfg.source_map.quoting)
            # next(post_list, None)  # skip headerline
        elif self.cfg.source_map.file_extension == "json":
            post_reader = post_reader + json.loads(file_handle.read())
        self._parse_postlist(post_reader)

    def _parse_postlist(self, post_reader: TextIO):
        """Process posts according to specifications"""
        # row_num = 0
        for post in post_reader:
            # row_num += 1
            lbsn_post = self._parse_post(post)
            if lbsn_post is None:
                continue
            self._merge_posts(lbsn_post)
            # status report
            msg = (
                f'Cleaned output to {len(self.distinct_locations_set):02d} '
                f'distinct locations from '
                f'{self.stats.count_glob:02d} posts '
                f'(File {self.stats.partcount} of {len(self.filelist)}) - '
                f'Skipped posts: {self.stats.skipped_count} - skipped tags: '
                f'{self.stats.count_tags_skipped} of '
                f'{self.stats.count_tags_global}')
            # if (row_num % 10 == 0):
            # modulo: print only once every 10 iterations
            print(msg, end='\r')
        # log last message to file, clean stdout
        print(" " * len(msg), end='\r')
        sys.stdout.flush()
        self.log.info(msg)

    def _merge_posts(self, lbsn_post: PostStructure):
        """Method will union all tags of a single user for each location

        - further information is derived from the first
        post for each user-location
        - the result is a cleaned output containing
        reduced information that is necessary for tag maps
        """
        # create userid_loc_id
        post_locid_userid = f'{lbsn_post.loc_id}::{lbsn_post.user_guid}'
        self.distinct_locations_set.add(lbsn_post.loc_id)
        # print(f'Added: {photo_locID} to distinct_locations_set '
        #       f'(len: {len(self.distinct_locations_set)})')
        self.distinct_userlocations_set.add(post_locid_userid)
        # print(f'Added: {post_locid_userid} to distinct_userlocations_set '
        #       f'(len: {len(distinct_userlocations_set)})')
        if (lbsn_post.loc_name and
                lbsn_post.loc_id not in self.locid_locname_dict):
            # add locname to dict
            self.locid_locname_dict[
                lbsn_post.loc_id] = lbsn_post.loc_name
        if lbsn_post.user_guid not in \
                self.locations_per_userid_dict or \
                lbsn_post.loc_id not in \
                self.locations_per_userid_dict[
                    lbsn_post.user_guid]:
            # Bit wise or and assignment in one step.
            # -> assign locID to UserDict list
            # if not already contained
            self.locations_per_userid_dict[
                lbsn_post.user_guid] |= {
                lbsn_post.loc_id}
            self.stats.count_loc += 1
            self.userlocations_firstpost_dict[
                post_locid_userid] = lbsn_post
        # union tags/emoji per userid/unique location
        if self.cfg.cluster_tags:
            self.userlocation_taglist_dict[
                post_locid_userid] |= lbsn_post.hashtags
        if self.cfg.cluster_emoji:
            self.userlocation_emojilist_dict[
                post_locid_userid] |= lbsn_post.emoji
        # get cleaned wordlist for topic modeling
        cleaned_wordlist = self._get_cleaned_wordlist(
            lbsn_post.post_body)
        # union words per userid/unique location
        self.userlocation_wordlist_dict[
            post_locid_userid] |= set(
            cleaned_wordlist)
        self.stats.count_glob += 1
        self._update_toplists(lbsn_post)

    def _update_toplists(self, lbsn_post):
        """Calculate toplists for emoji and tags

        - adds tag/emojicount of this media to overall
          tag/emojicount for this user,
        - initialize counter for user if not already done
        """
        if self.cfg.cluster_tags and lbsn_post.hashtags:
            self.userdict_tagcounters_global[
                lbsn_post.user_guid].update(
                lbsn_post.hashtags)
            self.total_tag_counter.update(lbsn_post.hashtags)
        if self.cfg.cluster_emoji and lbsn_post.emoji:
            self.userdict_emojicounters_global[
                lbsn_post.user_guid].update(
                lbsn_post.emoji)
            self.total_emoji_counter.update(
                lbsn_post.emoji)
        if lbsn_post.loc_id:
            # update single item hack
            # there're more elegant ways to do this
            self.userdict_locationcounters_global[
                lbsn_post.user_guid].update(
                (lbsn_post.loc_id,))
            self.total_location_counter.update(
                (lbsn_post.loc_id,))

    def get_cleaned_post_dict(
            self) -> Dict[str, CleanedPost]:
        """Output wrapper

        - calls loop user locations method
        - optionally initializes output to file
        """
        if self.cfg.write_cleaned_data:
            with open(f'{self.cfg.output_folder}/Output_cleaned.csv', 'w',
                      encoding='utf8') as csvfile:
                # get headerline from class structure
                headerline = ','.join(CleanedPost._fields)
                csvfile.write(f'{headerline}\n')
                # values will be written with CSV writer module
                datawriter = csv.writer(
                    csvfile, delimiter=',', lineterminator='\n',
                    quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                cleaned_post_dict = self._loop_loc_per_userid(datawriter)
        else:
            cleaned_post_dict = self._loop_loc_per_userid(None)
        if self.cfg.topic_modeling:
            self._write_topic_models()
        return cleaned_post_dict

    def get_prepared_data(self) -> 'PreparedData':
        """After data is loaded, this collects data and stats

        - prepare data for tag maps clustering
        - store to self.data_prepared
        """
        self._prepare_main_stats()
        return self.prepared_data

    def _prepare_main_stats(self):
        """Calculate overall tag and emoji statistics

        - write results (optionally) to file
        """
        # top lists and unique
        tag_stats = self._get_top_list(
            self.userdict_tagcounters_global, "tags")
        top_tags_list = tag_stats[0]
        total_unique_tags = tag_stats[1]
        tagscount_without_longtail = tag_stats[2]

        emoji_stats = self._get_top_list(
            self.userdict_emojicounters_global, "emoji")
        top_emoji_list = emoji_stats[0]
        total_unique_emoji = emoji_stats[1]
        emojicount_without_longtail = emoji_stats[2]

        location_stats = self._get_top_list(
            self.userdict_locationcounters_global, "locations")
        top_location_list = location_stats[0]
        total_unique_locations = location_stats[1]

        # update tmax and emax from optionally long tail removal
        if tagscount_without_longtail:
            self.prepared_data.tmax = tagscount_without_longtail
        else:
            self.prepared_data.tmax = self.cfg.tmax
        if emojicount_without_longtail:
            self.prepared_data.emax = emojicount_without_longtail
        else:
            self.prepared_data.emax = self.cfg.tmax

        # collect stats in prepared_data

        # if self.cfg.cluster_locations:
        total_location_count = LoadData._get_total_count(
            top_location_list, self.total_location_counter)
        self.prepared_data.top_locations_list = top_location_list
        self.prepared_data.total_unique_locations = total_unique_locations
        self.prepared_data.total_location_count = total_location_count
        self.prepared_data.locid_locname_dict = self.locid_locname_dict

        if self.cfg.cluster_tags:
            # top counts
            total_tag_count = LoadData._get_total_count(
                top_tags_list, self.total_tag_counter)
            self.prepared_data.top_tags_list = top_tags_list
            self.prepared_data.total_unique_tags = total_unique_tags
            self.prepared_data.total_tag_count = total_tag_count

        if self.cfg.cluster_emoji:
            total_emoji_count = LoadData._get_total_count(
                top_emoji_list, self.total_emoji_counter)
            self.prepared_data.top_emoji_list = top_emoji_list
            self.prepared_data.total_unique_emoji = total_unique_emoji
            self.prepared_data.total_emoji_count = total_emoji_count

    def _write_toplist(self, top_list, list_name):
        """Write toplists to file

        e.g.:
            tag, usercount
            toptag1, 1231
            toptag2, 560
            ...
        """
        if len(top_list) == 0:
            return
        top_list_store = ''.join(
            "%s,%i" % v + '\n' for v in top_list)
        # overwrite, if exists:
        with open(f'{self.cfg.output_folder}/'
                  f'Output_top{list_name}.txt', 'w',
                  encoding='utf8') as out_file:
            out_file.write(f'{list_name}, usercount\n')
            out_file.write(top_list_store)

    def _get_top_list(self, userdict_tagemoji_counters,
                      listname: str = "tags"):
        """Get Top Tags on a per user basis, i.e.

        - the global number of distinct users who used each distinct tag
        - this ignores duplicate use of
        - calculation is based on dict userdict_tagcounters_global,
            with counters of tags for each user
        Returns:
            - list of top tags up to tmax [1000]
            - count of total unique tags
        """
        overall_usercount_perte = collections.Counter()
        for tagemoji_hash in userdict_tagemoji_counters.values():
            # taghash contains unique values (= strings) for each user,
            # thus summing up these taghashes counts each user
            # only once per tag (or emoji)
            overall_usercount_perte.update(tagemoji_hash)
        total_unique = len(overall_usercount_perte)
        # get all items for "locations"
        # but clip list for tags and emoji
        if listname in ("tags", "emoji"):
            max_items = self.cfg.tmax
        else:
            max_items = None
        top_list = overall_usercount_perte.most_common(max_items)
        if self.cfg.remove_long_tail is True:
            total_without_longtail = self._remove_long_tail(top_list, listname)
        max_to_write = min(1000, self.cfg.tmax)
        self._write_toplist(top_list[:max_to_write], listname)
        return top_list, total_unique, total_without_longtail

    @staticmethod
    def _get_total_count(top_list, top_counter):
        """Calculate Total Tags for selected

        Arguments:
        top_list (Long Tail Stat)
        top_counter (Reference to counter object)
        """
        total_count = 0
        for tagemoji in top_list:
            count = top_counter.get(tagemoji[0])
            if count:
                total_count += count
        return total_count

    def _remove_long_tail(self,
                          top_list: List[Tuple[str, int]],
                          listname: str
                          ) -> int:
        """Removes all items from list that are used by less

        than x number of users,
        where x is given as input arg limit_bottom_user_count
            Note: since list is a mutable object, method
            will modify top_tags_list
        """
        if listname == 'locations':
            # keep all locations
            return len(top_list)
        elif listname == 'emoji':
            # emoji use a smaller area than tags on the map
            # therefore we can keep more emoji
            # (e.g..: use 2 instead of 5)
            bottomuser_count = math.trunc(
                self.cfg.limit_bottom_user_count/2)
        else:
            bottomuser_count = self.cfg.limit_bottom_user_count
        indexMin = next((i for i, (t1, t2) in enumerate(
            top_list) if t2 < bottomuser_count
        ), None)
        if not indexMin:
            return
        len_before = len(top_list)
        # delete based on slicing
        del top_list[indexMin:]
        len_after = len(top_list)
        if len_before == len_after:
            # if no change, return
            return len_after
        self.log.info(
            f'Long tail removal: Filtered {len_before - len_after} '
            f'{listname} that were used by less than '
            f'{bottomuser_count} users.')
        return len_after

    def _loop_loc_per_userid(self, datawriter=None):
        """Will produce final cleaned list
        of items to be processed by clustering.

        - optionally writes entries to file, if handler exists
        """
        cleaned_post_dict = defaultdict(CleanedPost)
        for user_key, locationhash in \
                self.locations_per_userid_dict.items():
            for location in locationhash:
                locid_userid = f'{location}::{user_key}'
                post_latlng = location.split(':')

                first_post = self.userlocations_firstpost_dict.get(
                    locid_userid, None)
                if first_post is None:
                    return
                # create tuple with cleaned photo data
                cleaned_post_location = self._get_cleaned_location(
                    first_post, locid_userid, post_latlng, user_key)

                if datawriter is not None:
                    LoadData._write_location_tocsv(
                        datawriter, cleaned_post_location)
                if self.cfg.topic_modeling:
                    self._update_topic_models(
                        cleaned_post_location, user_key)
                cleaned_post_dict[cleaned_post_location.guid] = \
                    cleaned_post_location
        return cleaned_post_dict

    def _write_topic_models(self):
        """Initialize two lists for topic modeling output

        - hashed (anonymized) output (*add salt)
        - original output
        """
        headerline = "topics,post_ids,user_ids\n"
        with open(f'{self.cfg.output_folder}/'
                  f'"Output_usertopics_anonymized.csv', 'w',
                  encoding='utf8') as csvfile_anon, \
            open(f'{self.cfg.output_folder}/'
                 f'"Output_usertopics.csv', 'w',
                 encoding='utf8') as csvfile:
            dw_list = list()
            for cfile in (csvfile, csvfile_anon):
                cfile.write(headerline)
                dw = csv.writer(cfile, delimiter=',',
                                lineterminator='\n', quotechar='"',
                                quoting=csv.QUOTE_NONNUMERIC)
                dw_list.append(dw)
            self._write_topic_rows(dw_list)

    def _write_topic_rows(self, dw_list):
        """Write Topic models to file"""
        dw = dw_list[0]
        dw_anon = dw_list[1]

        def _join_encode(keys):
            joined_keys = ",".join(keys)
            joined_encoded_keys = ",".join(
                [Utils.encode_string(post_id) for post_id in keys])
            return joined_keys, joined_encoded_keys
        for user_key, topics in self.user_topiclist_dict.items():
            joined_topics = " ".join(topics)
            post_keys = self.user_post_ids_dict.get(user_key, None)
            joined_keys, joined_encoded_keys = _join_encode(post_keys)
            dw_anon.writerow([joined_topics,
                              "{" + joined_encoded_keys + "}",
                              Utils.encode_string(user_key)])
            dw.writerow([joined_topics,
                         "{" + joined_keys + "}",
                         str(user_key)])

    def _update_topic_models(self,
                             cleaned_post_location,
                             user_key):
        """If Topic Modeling enabled, update
        required dictionaries with merged words from
        title, tags and post_body
        """
        if not len(
                cleaned_post_location.hashtags) == 0:
            self.user_topiclist_dict[user_key] |= \
                cleaned_post_location.hashtags
            # also use descriptions for Topic Modeling
            self. user_topiclist_dict[user_key] |= \
                cleaned_post_location.post_body
            # Bit wise or and assignment in one step.
            # -> assign PhotoGuid to UserDict list
            # if not already contained
            self.user_post_ids_dict[user_key] |= {
                cleaned_post_location.guid}
            # UserPhotoFirstThumb_dict[user_key] = photo[5]

    def _get_cleaned_location(self, first_post, locid_userid,
                              post_latlng, user_key):
        """Merge cleaned post from all posts of a certain user
        at a specific location

        - some information is not needed, those post attributes
        are simply skipped (e.g. location name)
        - some information must not be merged, this can be directly copied
        from the first post at a location/user (e.g. origin_id - will always be
        the same for a particular user, post_create_date, post_publish_date)
        - some information (e.g. hashtags) need merge with removing dupliates:
        use prepared dictionaries
        - some important information is type-checked (longitude, latitude)

        Keyword arguments:
        first_post      -- first post of a user_guid at a location
        locid_userid    -- user_guid and loc_id in merged format
                           (f'{location}::{user_key}')
        post_latlng     -- tuple with lat/lng coordinates
        user_key        -- user_guid

        Note:
            ("",) means: substitute empty tuple as default
        """

        merged_wordlist = LoadData._get_merged(
            self.userlocation_wordlist_dict, locid_userid)
        merged_emojilist = LoadData._get_merged(
            self.userlocation_emojilist_dict, locid_userid)
        merged_taglist = LoadData._get_merged(
            self.userlocation_taglist_dict, locid_userid)
        cleaned_post = CleanedPost(
            origin_id=first_post.origin_id,
            lat=float(post_latlng[0]),
            lng=float(post_latlng[1]),
            guid=first_post.guid,
            user_guid=user_key,
            post_body=merged_wordlist,
            post_create_date=first_post.post_create_date,
            post_publish_date=first_post.post_publish_date,
            post_views_count=first_post.post_views_count,
            post_like_count=first_post.post_like_count,
            emoji=merged_emojilist,
            hashtags=merged_taglist,
            loc_id=first_post.loc_id
        )
        return cleaned_post

    @staticmethod
    def _get_merged(ref_dict: Dict, locid_userid: str) -> Set[str]:
        """Gets set of words for userlocid from ref dictionary

        Note: since using defaultdict,
        keys not found will return empty set()
        """
        value = ref_dict[locid_userid]
        return value

    @staticmethod
    def _write_location_tocsv(datawriter: TextIO,
                              cleaned_post_location: CleanedPost) -> None:
        """Writes a single record of cleaned posts to CSV list

        - write intermediate cleaned post data to file for later use
        Arguments
        datawriter              -      open file file_handle to
                                       output file
        cleaned_post_location   -      cleaned post of type CleanedPost
                                       (namedtuple)
        """
        ploc_list = LoadData._cleaned_ploc_tolist(
            cleaned_post_location)
        datawriter.writerow(ploc_list)

    @staticmethod
    def _cleaned_ploc_tolist(cleaned_post_location: CleanedPost
                             ) -> List[str]:
        """Converts a cleaned post structure to list for CSV write"""
        attr_list = list()
        for attr in cleaned_post_location:
            if isinstance(attr, set):
                attr_list.append(";".join(attr))
            else:
                attr_list.append(attr)
        return attr_list

    def _get_cleaned_wordlist(self, post_body_string):
        cleaned_post_body = Utils._remove_special_chars(post_body_string)
        cleaned_wordlist = LoadData._get_wordlist(cleaned_post_body)
        return cleaned_wordlist

    @staticmethod
    def _get_wordlist(cleaned_post_body):
        """split by space-characterm, filter by length"""
        wordlist = [word for word in cleaned_post_body.lower().split(
            ' ') if len(word) > 2]
        return wordlist

    def _parse_post(self, post: Dict[str, str]) -> PostStructure:
        """Process single post and attach to common structure"""
        # skip duplicates and erroneous entries
        post_guid = post.get(self.cfg.source_map.post_guid_col)
        if post_guid in self.guid_hash or len(post) < 15:
            self.stats.skipped_count += 1
            return None
        else:
            self.guid_hash.add(post_guid)
        # Continue Parse Post
        lbsn_post = PostStructure()
        lbsn_post.guid = post_guid  # guid
        lbsn_post.origin_id = post.get(self.cfg.source_map.originid_col)
        lbsn_post.user_guid = post.get(self.cfg.source_map.user_guid_col)
        lbsn_post.post_url = post.get(self.cfg.source_map.post_url_col)
        lbsn_post.post_publish_date = \
            post.get(self.cfg.source_map.post_publish_date_col)
        # Process Spatial Query first (if skipping necessary)
        if self.cfg.sort_out_places and \
                self._is_sortout_place(post):
            return None
        if self._is_empty_latlng(post):
            return None
        else:
            # assign lat/lng coordinates from dict
            lat, lng = self._correct_placelatlng(
                post.get(self.cfg.source_map.place_guid_col),
                post.get(self.cfg.source_map.latitude_col),
                post.get(self.cfg.source_map.longitude_col)
            )
            # update boundary
            self.bounds._upd_latlng_bounds(lat, lng)
        lbsn_post.latitude = lat
        lbsn_post.longitude = lng
        lbsn_post.loc_id = str(lat) + ':' + \
            str(lng)  # create loc_id from lat/lng
        lbsn_post.loc_name = post.get(self.cfg.source_map.place_name_col)
        # exclude posts outside boundary
        if self.cfg.shapefile_intersect and \
                self._is_outside_shapebounds(post):
            return None
        if self.cfg.cluster_tags or \
                self.cfg.cluster_emoji or \
                self.cfg.topic_modeling:
            lbsn_post.post_body = post.get(self.cfg.source_map.post_body_col)
        else:
            lbsn_post.post_body = ""
        lbsn_post.post_like_count = self._get_count_frompost(
            post.get(self.cfg.source_map.post_like_count_col))
        lbsn_post.hashtags = set()
        if self.cfg.cluster_tags or self.cfg.topic_modeling:
            lbsn_post.hashtags = self._get_tags(
                post.get(self.cfg.source_map.tags_col))
        if self.cfg.cluster_emoji:
            lbsn_post.emoji = self._get_emoji(lbsn_post.post_body)
            # no merge anymore:
            # lbsn_post.hashtags = set.union(post_emoji)
        lbsn_post.post_create_date = \
            post.get(self.cfg.source_map.post_create_date_col)
        lbsn_post.post_views_count = self._get_count_frompost(
            post.get(self.cfg.source_map.post_views_count_col))
        # return parsed post object
        return lbsn_post

    def _get_emoji(self, post_body):
        emoji_filtered = set(Utils._extract_emoji(post_body))
        if not len(emoji_filtered) == 0:
            self.stats.count_emojis_global += len(emoji_filtered)
            # self.total_emoji_counter.update(emoji_filtered)
        return emoji_filtered

    def _get_tags(self, tags_string: str) -> Set[str]:
        # [1:-1] removes curly brackets, second [1:-1] removes quotes
        tags = set(filter(None, tags_string.lower().split(";")))
        # Filter tags based on two stoplists
        if self.cfg.ignore_stoplists:
            count_tags = len(tags)
            count_skipped = 0
        else:
            tags, count_tags, count_skipped = \
                Utils.filter_tags(
                    tags,
                    self.cfg.sort_out_always_set,
                    self.cfg.sort_out_always_instr_set
                )
        self.stats.count_tags_global += count_tags
        self.stats.count_tags_skipped += count_skipped
        return tags

    @staticmethod
    def _get_count_frompost(count_string: str) -> int:
        if count_string and not count_string == "":
            try:
                photo_likes_int = int(count_string)
                return photo_likes_int
            except TypeError:
                pass
        return 0

    def _correct_placelatlng(self, place_guid_string, lat, lng):
        """If place corrections available, update lat/lng coordinates
        Needs test: not place_guid_string
        """
        if (self.cfg.correct_places and not place_guid_string and
                place_guid_string in self.cfg.correct_place_latlng_dict):
            lat = Decimal(
                # correct lat
                self.cfg.correct_place_latlng_dict[place_guid_string][0])
            lng = Decimal(
                # correct lng
                self.cfg.correct_place_latlng_dict[place_guid_string][1])
        else:
            # return original lat/lng
            lat = Decimal(lat)  # original lat
            lng = Decimal(lng)  # original lng
        return lat, lng

    def _is_outside_shapebounds(self, post):
        """Skip all posts outside shapefile """
        # do not expensive spatial check twice:
        if post.loc_id in self.shape_exclude_locid_hash:
            self.stats.skipped_count += 1
            return True
        if post.loc_id not in self.cfg.shape_included_locid_hash:
            LngLatPoint = Point(post.longitude, post.latitude)
            if not LngLatPoint.within(self.cfg.shp_geom):
                self.stats.skipped_count += 1
                self.shape_exclude_locid_hash.add(post.loc_id)
                return True
            else:
                self.shape_included_locid_hash.add(post.loc_id)
        return False

    def _is_empty_latlng(self, post):
        """ skip non-geotagged medias"""
        latitude = post.get(self.cfg.source_map.latitude_col)
        longitude = post.get(self.cfg.source_map.longitude_col)
        if not latitude or not longitude:
            self.stats.count_non_geotagged += 1
            return True
        return False

    def _is_sortout_place(self, post):
        place_guid = post.get(self.cfg.source_map.place_guid_col)
        if place_guid:
            if place_guid in self.cfg.sort_out_places_set:
                self.stats.skipped_count += 1
                return True
        return False

    def _get_tmax(self):
        """User Input to get number of tags to process"""
        if self.cfg.auto_mode:
            return
        if self.cfg.cluster_tags or self.cfg.cluster_emoji:
            inputtext = \
                input(f'Files to process: {len(self.filelist)}. \nOptional: '
                      f'Enter a Number for the variety of tags to process '
                      f'(default is 1000)\nPress Enter to proceed.. \n')
            if inputtext is None \
                    or inputtext == "" \
                    or not inputtext.isdigit():
                return
            else:
                self.cfg.tmax = int(inputtext)

    @staticmethod
    def _read_local_files(config):
        """Read Local Files according to config parameters

        - returns list of file-paths
        """
        input_path = config.input_folder
        filelist = list(input_path.glob(
            f'*.{config.source_map.file_extension}'))
        input_count = len(filelist)
        if input_count == 0:
            raise ValueError(
                f'No input files *.'
                f'{config.source_map.file_extension} '
                f'found.')
        else:
            return filelist


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
