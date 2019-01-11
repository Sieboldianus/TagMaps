# -*- coding: utf-8 -*-

"""
Module for shared structural elements
"""

from collections import namedtuple


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


"""This auto-class generated from named structure

provides access for fast handling
of essential post attributes
for use in tag maps clustering

- namedtuple instances are just as memory
efficient as regular tuples because they
do not have per-instance dictionaries.
"""
CleanedPost = namedtuple(
    'CleanedPost',
    'origin_id lat lng guid user_guid '
    'post_create_date post_publish_date '
    'post_body hashtags emoji '
    'post_views_count loc_id')


class CleanedPost_():
    """Shared structure for Post Attributes

    Contains only the attributes needed for tag maps.
    - in correct order for CSV read/write (PostStructure.__dict__)
    """

    def __init__(self):
        self.origin_id = None
        self.latitude = None
        self.longitude = None
        self.guid = None
        self.place_guid = None
        self.user_guid = None
        self.post_create_date = None
        self.post_publish_date = None
        self.post_body = None
        self.hashtags = None
        self.emoji = None
        self.post_views_count = None
        self.loc_id = None

    def __iter__(self):
        return iter([self.origin_id,
                     self.latitude,
                     self.longitude,
                     self.guid,
                     self.place_guid,
                     self.user_guid,
                     self.post_create_date,
                     self.post_publish_date,
                     self.post_body,
                     self.hashtags,
                     self.emoji,
                     self.post_views_count,
                     self.loc_id])
