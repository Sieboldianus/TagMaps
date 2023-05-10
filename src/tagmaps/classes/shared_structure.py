# -*- coding: utf-8 -*-

"""
Module for shared structural elements
"""

from __future__ import absolute_import

import csv
from dataclasses import astuple, dataclass, fields
from decimal import Decimal
from typing import List, Optional, Set

LOCATIONS: str = 'Locations'
TAGS: str = 'Tags'
EMOJI: str = 'Emoji'
TOPICS: str = 'Topics'
ClusterTypes: List[str] = [TAGS, EMOJI, LOCATIONS, TOPICS]


@dataclass
class CleanedPost:
    """CleanedPost dataclass

    - provides access for fast handling
    of essential post attributes
    for use in tag maps clustering
    - dataclass instances are just as memory
    efficient as regular tuples because they
    do not have per-instance dictionaries
    """
    origin_id: int
    lat: float
    lng: float
    guid: str
    user_guid: str
    loc_id: str
    post_create_date: Optional[str] = None
    post_publish_date: Optional[str] = None
    post_body: Optional[Set[str]] = None
    hashtags: Optional[Set[str]] = None
    emoji: Optional[Set[str]] = None
    post_views_count: Optional[int] = None
    post_like_count: Optional[int] = None
    loc_name: Optional[str] = None

    def __iter__(self):
        return iter(astuple(self))


POST_FIELDS = [a.name for a in fields(CleanedPost)]


@dataclass
class PostStructure:
    """Shared structure for additional Post Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    - this could also be replaced by protobuf lbsnPost() from
    lbsnstructure package

    This list of arguments contains many  optional sets of information
    that can be adapted for specific cases / individual hooks
    """
    # origin of data (type int),
    # e.g. Flickr = 1, Twitter = 2
    origin_id: int
    # global unique id of post (type str),
    # can be hashed or encrypted
    guid: str
    # global unique id of user (type str),
    # can be hashed or encrypted
    user_guid: str
    # post latlng (type PostGis geometry.Point),
    # optional
    post_latlng: Optional[str] = None
    # global unique id (type str) for referenced place,
    # optional
    place_guid: Optional[str] = None
    # global unique id (type str) for referenced city,
    # optional
    city_guid: Optional[str] = None
    # global unique id (type str) for referenced country,
    # optional
    country_guid: Optional[str] = None
    # geoaccuracy of spatial information (type str),
    # either  'latlng', 'place', 'city' or 'country', optional
    post_geoaccuracy: Optional[str] = None
    # the time the post was created,
    # e.g. the timestamp of the photo on Flickr
    # (type str, e.g. 2017-10-29 15:58:25), optional
    post_create_date: Optional[str] = None
    # the time the post was uploaded,
    # e.g. the timestamp of the upload on Flickr (type str),
    # optional
    post_publish_date: Optional[str] = None
    # content of post body,
    # e.g. the description on Flickr or the Tweet text on Twitter,
    # optional
    post_body: Optional[str] = None
    # language id (type str), optional
    post_language: Optional[str] = None
    # mentioned user_guids in post_body, optional
    user_mentions: Optional[str] = None
    # list of (hash-) tags (type str),
    # separated by semicolon, e.g. "lov;loved;awesomeday;goldenhour;"),
    # required or auto-extracted from post_body based on hashing '#'
    hashtags: Optional[Set[str]] = None
    # list of emoji (type str, separatior semicolon),
    # optional - can be auto-extracted from post_body
    emoji: Optional[Set[str]] = None
    # number of times this post has beed liked or
    # starred (Flickr), type int, optional
    post_like_count: Optional[int] = None
    # number of times this Post has been commented by other users,
    # e.g. count of Reply-Tweets in Twitter,
    # count of comments in Flickr etc., type int, optional
    post_comment_count: Optional[int] = None
    # number of times this post has beed viewed by other users,
    # type int, optional
    post_views_count: Optional[int] = None
    # the title of the post, type str, optional
    post_title: Optional[str] = None
    # thumbnail url, optional
    post_thumbnail_url: Optional[str] = None
    # post url, optional
    post_url: Optional[str] = None
    # post type, either 'text', 'image' or 'video',
    # type str, optional
    post_type: Optional[str] = None
    # applied post filters, type str, optional
    post_filter: Optional[str] = None
    # Number of times this Post has been quoted by other users,
    # e.g. count of Quote-Tweets in Twitter, type int, optional
    post_quote_count: Optional[int] = None
    # Number of times this Post has been shared by other users,
    # e.g. count of Retweets in Twitter, type int, optional
    post_share_count: Optional[int] = None
    # Type of input device used by the user to post,
    # for a list see Twitter, e.g. "Web", "IPhone",
    # "Android" etc., type str, optional
    input_source: Optional[str] = None
    # An integer for specifying licenses attached to post
    # (e.g. All Rights Reserved = 0). Numbers shamelessly
    # ripped from Flickr:
    # https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
    # type int, optional
    post_content_license: Optional[str] = None
    # latitude of post in decimal degrees (WGS 1984),
    # type float, required
    latitude: Optional[Decimal] = None
    # longitude of post in decimal degrees  (WGS 1984),
    # type float, required
    longitude: Optional[Decimal] = None
    # location_id, automatically
    # constructed from lat:lng
    loc_id: Optional[str] = None
    # name of location, type str, optional
    loc_name: Optional[str] = None


@dataclass
class ItemCounter:
    name: str
    ucount: int

    def __iter__(self):
        return iter(astuple(self))


class AnalysisBounds():
    """Structure for storing boundary (lim lat/lng)"""

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

    def get_bound_report(self):
        """Report on spatial bounds"""
        if (self.lim_lat_min is None
                or self.lim_lat_max is None
                or self.lim_lng_min is None
                or self.lim_lng_max is None):
            return f'Bounds have not been initlialized'
        bound_report = f'Bounds are: ' \
            f'Min {float(self.lim_lng_min)} {float(self.lim_lat_min)} ' \
            f'Max {float(self.lim_lng_max)} {float(self.lim_lat_max)}'
        return bound_report


class ConfigMap:
    """Retrieves python object from config.cfg"""

    def __init__(self, source_config):
        # [Main]
        self.name = source_config["Main"]["name"]
        self.file_extension = source_config["Main"]["file_extension"].lower()
        self.delimiter = source_config["Main"]["delimiter"]
        self.array_separator = source_config["Main"]["array_separator"]
        self.quoting = self._quote_selector(
            source_config["Main"]["quoting"])
        self.quote_char = source_config["Main"]["quote_char"].strip('\'')
        self.date_time_format = source_config["Main"]["file_extension"]
        # [Columns]
        self.originid_col = source_config["Columns"]["originid_col"]
        self.post_guid_col = source_config["Columns"]["post_guid_col"]
        self.latitude_col = source_config["Columns"]["latitude_col"]
        self.longitude_col = source_config["Columns"]["longitude_col"]
        self.user_guid_col = source_config["Columns"]["user_guid_col"]
        self.post_create_date_col = \
            source_config["Columns"]["post_create_date_col"]
        self.post_publish_date_col = \
            source_config["Columns"]["post_publish_date_col"]
        self.post_views_count_col = \
            source_config["Columns"]["post_views_count_col"]
        self.post_like_count_col = \
            source_config["Columns"]["post_like_count_col"]
        self.post_url_col = source_config["Columns"]["post_url_col"]
        self.tags_col = source_config["Columns"]["tags_col"]
        self.emoji_col = source_config["Columns"]["emoji_col"]
        self.post_title_col = source_config["Columns"]["post_title_col"]
        self.post_body_col = source_config["Columns"]["post_body_col"]
        self.post_geoaccuracy_col = \
            source_config["Columns"]["post_geoaccuracy_col"]
        self.place_guid_col = source_config["Columns"]["place_guid_col"]
        self.place_name_col = source_config["Columns"]["place_name_col"]

    @staticmethod
    def _quote_selector(quote_string):
        quote_switch = {
            "QUOTE_MINIMAL": csv.QUOTE_MINIMAL,
            "QUOTE_ALL": csv.QUOTE_ALL,
            "QUOTE_NONNUMERIC": csv.QUOTE_NONNUMERIC,
            "QUOTE_NONE": csv.QUOTE_NONE,
        }
        quoting = quote_switch.get(quote_string)
        return quoting
