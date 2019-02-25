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
    """
    origin_id = attr.ib(init=False)
    guid = attr.ib(init=False)
    post_latlng = attr.ib(init=False)
    place_guid = attr.ib(init=False)
    city_guid = attr.ib(init=False)
    country_guid = attr.ib(init=False)
    post_geoaccuracy = attr.ib(init=False)
    user_guid = attr.ib(init=False)
    post_create_date = attr.ib(init=False)
    post_publish_date = attr.ib(init=False)
    post_body = attr.ib(init=False)
    post_language = attr.ib(init=False)
    user_mentions = attr.ib(init=False)
    hashtags = attr.ib(init=False)
    emoji = attr.ib(init=False)
    post_like_count = attr.ib(init=False)
    post_comment_count = attr.ib(init=False)
    post_views_count = attr.ib(init=False)
    post_title = attr.ib(init=False)
    post_thumbnail_url = attr.ib(init=False)
    post_url = attr.ib(init=False)
    post_type = attr.ib(init=False)
    post_filter = attr.ib(init=False)
    post_quote_count = attr.ib(init=False)
    post_share_count = attr.ib(init=False)
    input_source = attr.ib(init=False)
    post_content_license = attr.ib(init=False)
    latitude = attr.ib(init=False)
    longitude = attr.ib(init=False)
    loc_id = attr.ib(init=False)
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
