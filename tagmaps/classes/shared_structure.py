# -*- coding: utf-8 -*-

"""
Module for shared structural elements
"""


class PostStructure():
    """Shared structure for Post Attributes

    Contains attributes shared among PG DB and LBSN ProtoBuf spec.
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
