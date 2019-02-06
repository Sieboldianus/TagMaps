# -*- coding: utf-8 -*-

"""Module for preparing base data and calculating
overall statistics.

Returns:
    PreparedStats: Statistics prepared for Tag Maps clustering
    self.cleaned_post_dict: Cleaned list of posts
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
    EMOJI, LOCATIONS, TAGS, ClusterType)
from tagmaps.classes.shared_structure import (
    PostStructure, CleanedPost, AnalysisBounds, PreparedStats)


class PrepareData():
    """Main Class for building summary statistics.

    - will process individual cleaned post data into dict/set structures
    - will filter data, cleaned output can be stored
    - will generate statistics
    """

    def __init__(
            self, cluster_types, write_cleaned_data, max_items,
            output_folder, remove_long_tail, limit_bottom_user_count,
            topic_modeling):
        """Initializes Prepare Data structure"""
        # global settings
        self.cluster_types = cluster_types
        self.write_cleaned_data = write_cleaned_data
        self.max_items = max_items
        self.output_folder = output_folder
        self.remove_long_tail = remove_long_tail
        self.limit_bottom_user_count = limit_bottom_user_count
        self.topic_modeling = topic_modeling
        # global vars
        self.count_glob = 0
        self.bounds = AnalysisBounds()
        self.log = logging.getLogger("tagmaps")
        self.total_tag_counter = collections.Counter()
        self.total_emoji_counter = collections.Counter()
        self.total_location_counter = collections.Counter()
        self.cleaned_stats = PreparedStats()
        # Hashsets:
        self.locations_per_userid_dict = defaultdict(set)
        self.userlocation_taglist_dict = defaultdict(set)
        self.userlocation_emojilist_dict = defaultdict(set)
        self.locid_locname_dict: Dict[str, str] = dict()  # nopep8
        if self.topic_modeling:
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

    def add_record(self, lbsn_post: PostStructure):
        """Method will merge all tags/emoji/terms
        of a single user for each location (Metric 'UPL') to
        produce a cleaned version of input data


        - further information is derived from the first
        post for each user-location
        - the result is a cleaned output containing
        reduced information that is necessary for tag maps
        - get cleaned output with get_prepared_data()
        """
        self.count_glob += 1
        # create userid_loc_id, this is used as the base
        # for clustering data (metric UPL)
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
            # self.stats.count_loc += 1
            self.userlocations_firstpost_dict[
                post_locid_userid] = lbsn_post
        # union tags/emoji per userid/unique location
        if TAGS in self.cluster_types:
            self.userlocation_taglist_dict[
                post_locid_userid] |= lbsn_post.hashtags
        if EMOJI in self.cluster_types:
            self.userlocation_emojilist_dict[
                post_locid_userid] |= lbsn_post.emoji
        # get cleaned wordlist for topic modeling
        cleaned_wordlist = self._get_cleaned_wordlist(
            lbsn_post.post_body)
        # union words per userid/unique location
        self.userlocation_wordlist_dict[
            post_locid_userid] |= set(
            cleaned_wordlist)
        self._update_toplists(lbsn_post)

    def get_cleaned_post_dict(
            self) -> Dict[str, CleanedPost]:
        """Output wrapper

        - calls loop user locations method
        - optionally initializes output to file
        """
        if self.write_cleaned_data:
            with open(self.output_folder / 'Output_cleaned.csv', 'w',
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
        if self.topic_modeling:
            self._write_topic_models()
        return cleaned_post_dict

    def _get_item_stats(self) -> 'PreparedStats':
        """After data is loaded, this collects data and stats
        for distribution of tags, emoji and locations

        - prepare data for tag maps clustering
        - store to self.data_prepared
        """
        self._prepare_item_stats()
        return self.cleaned_stats

    def _prepare_item_stats(self):
        """Calculate overall tag and emoji statistics

        - write results (optionally) to file
        """
        # top lists and unique
        tag_stats = self._get_top_list(
            self.userdict_tagcounters_global, TAGS)
        top_tags_list = tag_stats[0]
        total_unique_tags = tag_stats[1]
        tagscount_without_longtail = tag_stats[2]

        emoji_stats = self._get_top_list(
            self.userdict_emojicounters_global, EMOJI)
        top_emoji_list = emoji_stats[0]
        total_unique_emoji = emoji_stats[1]
        emojicount_without_longtail = emoji_stats[2]

        location_stats = self._get_top_list(
            self.userdict_locationcounters_global, LOCATIONS)
        top_location_list = location_stats[0]
        total_unique_locations = location_stats[1]

        # update tmax and emax from optionally long tail removal
        if tagscount_without_longtail:
            self.cleaned_stats.tmax = tagscount_without_longtail
        else:
            self.cleaned_stats.tmax = self.max_items
        if emojicount_without_longtail:
            self.cleaned_stats.emax = emojicount_without_longtail
        else:
            self.cleaned_stats.emax = self.max_items

        # collect stats in prepared_data
        # if self.cfg.cluster_locations:
        total_location_count = PrepareData._get_total_count(
            top_location_list, self.total_location_counter)
        self.cleaned_stats.top_locations_list = top_location_list
        self.cleaned_stats.total_unique_locations = total_unique_locations
        self.cleaned_stats.total_location_count = total_location_count
        self.cleaned_stats.locid_locname_dict = self.locid_locname_dict

        if TAGS in self.cluster_types:
            # top counts
            total_tag_count = PrepareData._get_total_count(
                top_tags_list, self.total_tag_counter)
            self.cleaned_stats.top_tags_list = top_tags_list
            self.cleaned_stats.total_unique_tags = total_unique_tags
            self.cleaned_stats.total_tag_count = total_tag_count

        if EMOJI in self.cluster_types:
            total_emoji_count = PrepareData._get_total_count(
                top_emoji_list, self.total_emoji_counter)
            self.cleaned_stats.top_emoji_list = top_emoji_list
            self.cleaned_stats.total_unique_emoji = total_unique_emoji
            self.cleaned_stats.total_emoji_count = total_emoji_count

    def _update_toplists(self, lbsn_post):
        """Calculate toplists for emoji and tags

        - adds tag/emojicount of this media to overall
          tag/emojicount for this user,
        - initialize counter for user if not already done
        """
        if TAGS in self.cluster_types and lbsn_post.hashtags:
            self.userdict_tagcounters_global[
                lbsn_post.user_guid].update(
                lbsn_post.hashtags)
            self.total_tag_counter.update(lbsn_post.hashtags)
        if EMOJI in self.cluster_types and lbsn_post.emoji:
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
        with open(
                self.output_folder / f'Output_top{list_name}.txt',
                'w', encoding='utf8') as out_file:
            out_file.write(f'{list_name}, usercount\n')
            out_file.write(top_list_store)

    def _get_top_list(self, userdict_tagemoji_counters,
                      listtype: ClusterType = TAGS):
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
        if listtype in (TAGS, EMOJI):
            max_items = self.max_items
        else:
            max_items = None
        top_list = overall_usercount_perte.most_common(max_items)
        if self.remove_long_tail is True:
            total_without_longtail = self._remove_long_tail(top_list, listtype)
        # only ever write top 1000 to file
        max_to_write = min(1000, self.max_items)
        self._write_toplist(top_list[:max_to_write], listtype)
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
                          listtype: ClusterType
                          ) -> int:
        """Removes all items from list that are used by less

        than x number of users,
        where x is given as input arg limit_bottom_user_count
            Note: since list is a mutable object, method
            will modify top_tags_list
        """
        if listtype == LOCATIONS:
            # keep all locations
            return len(top_list)
        elif listtype == EMOJI:
            # emoji use a smaller area than tags on the map
            # therefore we can keep more emoji
            # (e.g..: use 2 instead of 5)
            bottomuser_count = math.trunc(
                self.limit_bottom_user_count/2)
        else:
            bottomuser_count = self.limit_bottom_user_count
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
            f'{listtype} that were used by less than '
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
                    PrepareData._write_location_tocsv(
                        datawriter, cleaned_post_location)
                if self.topic_modeling:
                    self._update_topic_models(
                        cleaned_post_location, user_key)
                cleaned_post_dict[cleaned_post_location.guid] = \
                    cleaned_post_location
                # update boundary
                self.bounds._upd_latlng_bounds(
                    cleaned_post_location.lat, cleaned_post_location.lng)
        return cleaned_post_dict

    def _write_topic_models(self):
        """Initialize two lists for topic modeling output

        - hashed (anonymized) output (*add salt)
        - original output
        """
        headerline = "topics,post_ids,user_ids\n"
        with open(
            self.output_folder / 'Output_usertopics_anonymized.csv',
                'w', encoding='utf8') as csvfile_anon, open(
                    self.output_folder / 'Output_usertopics.csv',
                    'w', encoding='utf8') as csvfile:
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

        merged_wordlist = PrepareData._get_merged(
            self.userlocation_wordlist_dict, locid_userid)
        merged_emojilist = PrepareData._get_merged(
            self.userlocation_emojilist_dict, locid_userid)
        merged_taglist = PrepareData._get_merged(
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
        ploc_list = PrepareData._cleaned_ploc_tolist(
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
        cleaned_wordlist = PrepareData._get_wordlist(cleaned_post_body)
        return cleaned_wordlist

    @staticmethod
    def _get_wordlist(cleaned_post_body):
        """split by space-characterm, filter by length"""
        wordlist = [word for word in cleaned_post_body.lower().split(
            ' ') if len(word) > 2]
        return wordlist
