# -*- coding: utf-8 -*-

"""
Module for shared structural elements
"""

from collections import namedtuple


CleanedPost_ = namedtuple(
    'CleanedPost',
    'origin_id lat lng guid user_guid '
    'post_create_date post_publish_date '
    'post_body hashtags emoji '
    'post_views_count post_like_count loc_id')


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
    pass


class PostStructure():
    """Shared structure for Post Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
    - this could also be replaces by protobuf lbsnPost() from
    lbsnstructure package
    """

    def __init__(self):
        self.origin_id = None
        self.guid = None
        self.post_latlng = None
        self.place_guid = None
        self.city_guid = None
        self.country_guid = None
        self.post_geoaccuracy = None
        self.user_guid = None
        self.post_create_date = None
        self.post_publish_date = None
        self.post_body = None
        self.post_language = None
        self.user_mentions = None
        self.hashtags = None
        self.emoji = None
        self.post_like_count = None
        self.post_comment_count = None
        self.post_views_count = None
        self.post_title = None
        self.post_thumbnail_url = None
        self.post_url = None
        self.post_type = None
        self.post_filter = None
        self.post_quote_count = None
        self.post_share_count = None
        self.input_source = None
        self.post_content_license = None
        # optional:
        self.latitude = None
        self.longitude = None
        self.loc_id = None
        self.loc_name = None


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

    def _upd_latlng_bounds(self, lat, lng):
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
        bound_report = f'Bounds are: ' \
            f'Min {float(self.lim_lng_min)} {float(self.lim_lat_min)} ' \
            f'Max {float(self.lim_lng_max)} {float(self.lim_lat_max)}'
        return bound_report


class PreparedData():
    """Class storing what is needed for tag cluster"""

    def __init__(self):
        """Initialize structure."""
        self.top_tags_list = None
        self.top_emoji_list = None
        self.top_locations_list = None
        self.total_unique_tags = 0
        self.total_unique_emoji = 0
        self.total_unique_locations = 0
        self.total_tag_count = 0
        self.total_emoji_count = 0
        self.total_location_count = 0
        self.single_mostused_tag = None
        self.single_mostused_emoji = None
        self.single_mostused_location = None
        self.tmax = 0
        self.emax = 0
        self.locid_locname_dict = None
