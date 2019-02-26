# -*- coding: utf-8 -*-

"""
Module for shared structural elements
"""

from __future__ import absolute_import

from collections import namedtuple
from typing import List, Tuple

import attr

LOCATIONS: str = 'Locations'
TAGS: str = 'Tags'
EMOJI: str = 'Emoji'
TOPICS: List[str] = 'Topics'
ClusterType: Tuple[Tuple[str, int]] = (
    (LOCATIONS, 1),
    (TAGS, 2),
    (EMOJI, 3),
    (TOPICS, 4),
)

CleanedPost_ = namedtuple(  # pylint: disable=C0103
    'CleanedPost',
    'origin_id lat lng guid user_guid '
    'post_create_date post_publish_date '
    'post_body hashtags emoji '
    'post_views_count post_like_count loc_id '
    'loc_name')


class CleanedPost(CleanedPost_):
    """This a wrapper class for namedtuple

    CleanedPost namedtuple provides access
    for fast handling
    of essential post attributes
    for use in tag maps clustering

    - namedtuple instances are just as memory
    efficient as regular tuples because they
    do not have per-instance dictionaries.
    """


@attr.s
class PostStructure(object):
    """Shared structure for Post Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    - this could also be replaces by protobuf lbsnPost() from
    lbsnstructure package

    This list of arguments contains many  optional sets of information
    that can be adapted for specific cases / individual hooks
    """
    # origin of data (type int),
    # e.g. Flickr = 1, Twitter = 2
    origin_id = attr.ib(init=False)
    # global unique id of post (type str),
    # can be hashed or encrypted
    guid = attr.ib(init=False)
    # post latlng (type PostGis geometry.Point),
    # optional
    post_latlng = attr.ib(init=False)
    # global unique id (type str) for referenced place,
    # optional
    place_guid = attr.ib(init=False)
    # global unique id (type str) for referenced city,
    # optional
    city_guid = attr.ib(init=False)
    # global unique id (type str) for referenced country,
    # optional
    country_guid = attr.ib(init=False)
    # geoaccuracy of spatial information (type str),
    # either  'latlng', 'place', 'city' or 'country', optional
    post_geoaccuracy = attr.ib(init=False)
    # global unique id of user (type str),
    # can be hashed or encrypted
    user_guid = attr.ib(init=False)
    # the time the post was created,
    # e.g. the timestamp of the photo on Flickr
    # (type str, e.g. 2017-10-29 15:58:25), optional
    post_create_date = attr.ib(init=False)
    # the time the post was uploaded,
    # e.g. the timestamp of the upload on Flickr (type str),
    # optional
    post_publish_date = attr.ib(init=False)
    # content of post body,
    # e.g. the description on Flickr or the Tweet text on Twitter,
    # optional
    post_body = attr.ib(init=False)
    # language id (type str), optional
    post_language = attr.ib(init=False)
    # mentioned user_guids in post_body, optional
    user_mentions = attr.ib(init=False)
    # list of (hash-) tags (type str),
    # separated by semicolon, e.g. "lov;loved;awesomeday;goldenhour;"),
    # required or auto-extracted from post_body based on hashing '#'
    hashtags = attr.ib(init=False)
    # list of emoji (type str, separatior semicolon),
    # optional - can be auto-extracted from post_body
    emoji = attr.ib(init=False)
    # number of times this post has beed liked or
    # starred (Flickr), type int, optional
    post_like_count = attr.ib(init=False)
    # number of times this Post has been commented by other users,
    # e.g. count of Reply-Tweets in Twitter,
    # count of comments in Flickr etc., type int, optional
    post_comment_count = attr.ib(init=False)
    # number of times this post has beed viewed by other users,
    # type int, optional
    post_views_count = attr.ib(init=False)
    # the title of the post, type str, optional
    post_title = attr.ib(init=False)
    # thumbnail url, optional
    post_thumbnail_url = attr.ib(init=False)
    # post url, optional
    post_url = attr.ib(init=False)
    # post type, either 'text', 'image' or 'video',
    # type str, optional
    post_type = attr.ib(init=False)
    # applied post filters, type str, optional
    post_filter = attr.ib(init=False)
    # Number of times this Post has been quoted by other users,
    # e.g. count of Quote-Tweets in Twitter, type int, optional
    post_quote_count = attr.ib(init=False)
    # Number of times this Post has been shared by other users,
    # e.g. count of Retweets in Twitter, type int, optional
    post_share_count = attr.ib(init=False)
    # Type of input device used by the user to post,
    # for a list see Twitter, e.g. "Web", "IPhone",
    # "Android" etc., type str, optional
    input_source = attr.ib(init=False)
    # An integer for specifying licenses attached to post
    # (e.g. All Rights Reserved = 0). Numbers shamelessly
    # ripped from Flickr:
    # https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
    # type int, optional
    post_content_license = attr.ib(init=False)
    # latitude of post in decimal degrees (WGS 1984),
    # type float, required
    latitude = attr.ib(init=False)
    # longitude of post in decimal degrees  (WGS 1984),
    # type float, required
    longitude = attr.ib(init=False)
    # location_id, automatically
    # constructed from lat:lng
    loc_id = attr.ib(init=False)
    # name of location, type str, optional
    loc_name = attr.ib(init=False)


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
