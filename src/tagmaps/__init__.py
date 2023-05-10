# -*- coding: utf-8 -*-
"""TagMaps package import specifications"""

from __future__ import absolute_import

from tagmaps.version import __version__
from tagmaps.tagmaps_ import TagMaps
from tagmaps.config.config import BaseConfig
from tagmaps.classes.load_data import LoadData
from tagmaps.classes.prepare_data import PrepareData
from tagmaps.classes.interface import UserInterface
from tagmaps.classes.shared_structure import (
    EMOJI, LOCATIONS, TAGS, TOPICS, PostStructure, ClusterTypes)

# pdoc documentation include/exclude
__pdoc__ = {}

# pdoc documentation include format
__pdoc__["tagmaps.__main__"] = True
