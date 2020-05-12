# -*- coding: utf-8 -*-
"""TagMaps package import specifications"""

from __future__ import absolute_import

from .version import __version__
from .tagmaps_ import TagMaps
from .config.config import BaseConfig
from .classes.load_data import LoadData
from .classes.prepare_data import PrepareData
from .classes.interface import UserInterface
from .classes.shared_structure import (
    EMOJI, LOCATIONS, TAGS, TOPICS, PostStructure, ClusterTypes)

# pdoc documentation include/exclude
__pdoc__ = {}

# pdoc documentation include format
__pdoc__["tagmaps.__main__"] = True
