# -*- coding: utf-8 -*-

"""Module with general utility methods used in tag maps package.
"""

from __future__ import absolute_import

import argparse
import hashlib
import io
import logging
import os
import platform
import re
import sys
import unicodedata
from datetime import timedelta
from importlib import reload
import math
from math import asin, cos, radians, sin, sqrt
from typing import Dict, Iterable, List, Set, Tuple
from collections import namedtuple
from pathlib import Path

import emoji
import numpy as np
import pyproj
import regex
import shapely.geometry as geometry

from tagmaps.classes.shared_structure import AnalysisBounds, CleanedPost


class Utils():
    """Collection of various tools and helper functions

    Primarily @classmethods and @staticmethods
    """
    def set_proj_dir():
        """Update PROJ_LIB location if not found."""
        if not os.environ.get('PROJ_LIB'):
            local_proj_path = Path.cwd() / "proj"
            if not local_proj_path.exists():
                raise ValueError("Pyproj 'proj' datadir not found. Either specify "
                                 "PROJ_LIB environmental variable or copy 'proj' "
                                 "folder to local path of executable")
            os.environ['PROJ_LIB'] = str(local_proj_path)
            pyproj.datadir.set_data_dir(str(local_proj_path))

    @staticmethod
    def get_shapely_bounds(
            bounds: AnalysisBounds) -> geometry.MultiPoint:
        """Returns boundary shape from 4 coordinates"""
        bound_points_shapely = geometry.MultiPoint([
            (bounds.lim_lng_min, bounds.lim_lat_min),
            (bounds.lim_lng_max, bounds.lim_lat_max)
        ])
        return bound_points_shapely

    @staticmethod
    def get_best_utmzone(
            bound_points_shapely: geometry.MultiPoint):
        """Calculate best UTM Zone SRID/EPSG Code
        Args:
        True centroid (coords may be multipoint)"""
        input_lon_center = bound_points_shapely.centroid.coords[0][0]
        input_lat_center = bound_points_shapely.centroid.coords[0][1]
        epsg_code = Utils._convert_wgs_to_utm(
            input_lon_center, input_lat_center)
        crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}', preserve_units=False)
        return crs_proj, epsg_code

    @staticmethod
    def _convert_wgs_to_utm(lon: float, lat: float):
        """"Return best epsg code for pair
        of WGS coordinates (lat/lng)

        Args:
            lon: latitude
            lat: longitude

        Returns:
            [type]: [description]

        See:
        https://gis.stackexchange.com/questions/269518/auto-select-suitable-utm-zone-based-on-grid-intersection/
        https://stackoverflow.com/questions/40132542/get-a-cartesian-projection-accurate-around-a-lat-lng-pair
        https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects
        """

        utm_band = str((math.floor((lon + 180) / 6) % 60) + 1)
        if len(utm_band) == 1:
            utm_band = '0'+utm_band
        if lat >= 0:
            epsg_code = '326' + utm_band
        else:
            epsg_code = '327' + utm_band
        return epsg_code

    @staticmethod
    def default_empty_cstructure():
        """Generates a tuple of parametric length with
        empty strings:
        (" "," "," "," "," "," "," "," "," "," "," "," ")
        """
        empty_string_list = list()
        for _ in range(len(CleanedPost._fields)):
            empty_string_list.append(" ")
        empty_string_tuple = tuple(empty_string_list)
        return empty_string_tuple

    @staticmethod
    def encode_string(text_s):
        """Encode string in Sha256,
        produce hex

        - returns a string of double length,
        containing only hexadecimal digits"""
        encoded_string = hashlib.sha3_256(
            text_s.encode("utf8")).hexdigest()
        return encoded_string

    @staticmethod
    def remove_special_chars(text_s):
        """Removes a list of special chars from string"""
        special_chars = "?.!/;:,[]()'-&#"
        s_cleaned = text_s.translate(
            {ord(c): " " for c in special_chars})
        return s_cleaned

    @staticmethod
    def _is_number(number_s):
        """Check if variable is number (float)"""
        try:
            float(number_s)
            return True
        except ValueError:
            return False

    @staticmethod
    def init_main():
        """Initializing main procedure
        if package is executed directly

        TODO:
        - disables fiona logging, as it (somehow)
          interferes with tag maps logging
          (find better solution)
        """
        # set console view parameters
        # stretch console
        if platform.system() == 'Windows':
            os.system('mode con: cols=197 lines=40')
        logging.getLogger("fiona.collection").disabled = True

    @staticmethod
    def set_logger(output_folder, logging_level=None):
        """ Set logging handler manually,
        so we can also print to console while logging to file
        """
        # reset logging in case Jupyter Notebook has
        # captured stdout
        reload(logging)
        # Create or get logger with specific name
        log = logging.getLogger("tagmaps")
        if log.handlers:
            # only add log handlers once
            return log
        if logging_level is None:
            logging_level = logging.INFO
        if output_folder is not None:
            if not output_folder.exists():
                Utils.init_output_dir(output_folder)
            # input(f'{type(output_folder)}')
            __log_file = output_folder / 'log.txt'
        log.format = '%(message)s'
        log.datefmt = ''
        log.setLevel(logging_level)
        # Set Output to Replace in case of
        # encoding issues (console/windows)
        if isinstance(sys.stdout, io.TextIOWrapper):
            # only for console output (not Juypter Notebook stream)
            sys.stdout = io.TextIOWrapper(
                sys.stdout.detach(), sys.stdout.encoding, 'replace')
            log.addHandler(logging.StreamHandler())
            if output_folder is not None:
                # only log to file in console mode
                log.addHandler(
                    logging.FileHandler(__log_file, 'w', 'utf-8'))
        else:
            # log to stdout, not stderr in Jupyter Mode to prevent
            # log.Info messages appear as red boxes
            logging.basicConfig(
                stream=sys.stdout, format=log.format,
                level=logging_level, datefmt=None)
            # log.stream = sys.stdout
        # flush once to clear console
        sys.stdout.flush()
        return log

    @staticmethod
    def init_output_dir(output_folder):
        """Creates local output dir if not exists"""
        if output_folder is not None and not output_folder.exists():
            output_folder.mkdir()
            print(f'Folder {output_folder.name}/ was created')

    @staticmethod
    def query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    @staticmethod
    def daterange(start_date, end_date):
        """Return time difference between two dates"""
        for n_val in range(
                int((end_date - start_date).days)):
            yield start_date + timedelta(n_val)

    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(
            radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a_value = (sin(dlat/2)**2 + cos(lat1) *
                   cos(lat2) * sin(dlon/2)**2)
        c_value = 2 * asin(sqrt(a_value))
        # Radius of earth in kilometers is 6371
        km_dist = 6371 * c_value
        m_dist = km_dist*1000
        return m_dist

    @staticmethod
    def get_radians_from_meters(dist):
        """Get approx. distance in radians from meters

        Args:
            dist (float): Distance in meters

        Returns:
            float: Distance in radians

        https://www.mathsisfun.com/geometry/radians.html
        - 1 Radian is about 57.2958 degrees.
        - then see:
        https://sciencing.com/convert-distances-degrees-meters-7858322.html
        - Multiply the number of degrees by 111.325
        - To convert this to meters, multiply by 1,000.
          So, 2 degrees is about 222,65 meters.
        """
        dist = dist/1000
        degrees_dist = dist/111.325
        radians_dist = degrees_dist/57.2958
        return radians_dist

    @staticmethod
    def get_meters_from_radians(dist):
        """Get approx. distance in meters from radians
        distance

        Args:
            dist (float): Distance in radians

        Returns:
            float: Distance in meters

        - 1 Radian is about 57.2958 degrees.
        - then see
        https://sciencing.com/convert-distances-degrees-meters-7858322.html
        - Multiply the number of degrees by 111.325
        - To convert this to meters, multiply by 1,000.
        So, 2 degrees is about 222,65 meters.
        """
        dist = dist * 57.2958
        dist = dist * 111.325
        meters_dist = round(dist * 1000, 1)
        return meters_dist

    @staticmethod
    def get_emojiname(emoji_string):
        """"Tries to get a name representation for
        emoji. Emoji can either be a single character,
        or a number of characters that construct a grapheme cluster.
        Therefore, unicodedata.name cannot directly be applied.
        For some grapheme clusters, there exists no unicodedata.name
        """
        emoji_name = None
        # first try to get name for whole str
        if len(emoji_string) == 1:
            # if single character
            emoji_name = Utils._get_unicode_name(emoji_string)
        if not emoji_name:
            for char_s in emoji_string:
                emoji_name = Utils._get_unicode_name(
                    char_s)
                if emoji_name:
                    break
        if not emoji_name:
            emoji_name = emoji.demojize(emoji_string)
        if not emoji_name:
            raise ValueError(f'No name found for {emoji_string}')
        return emoji_name

    @staticmethod
    def _get_unicode_name(emoji_string_or_char):
        try:
            emojiname = unicodedata.name(
                emoji_string_or_char)
            return emojiname
        except ValueError:
            return False

    @staticmethod
    def _check_emoji_type(char_unicode):
        """Checks if emoji code point is of specific type,

        e.g.:
        EMOJI MODIFIER, VARIATION SELECTOR
        or ZERO WIDTH modifier

        To check: Is this method really needed?
        """
        # name = name(str_emoji)
        try:
            if unicodedata.name(
                    char_unicode
            ).startswith(
                ("EMOJI MODIFIER",
                 "VARIATION SELECTOR",
                 "ZERO WIDTH")
            ):
                return False
            else:
                return True
        except ValueError:
            print(char_unicode)
            return True

    @staticmethod
    def split_emoji_count(text_with_emoji):
        """Split emoji from string and count"""
        emoji_list = []
        # use \X (eXtended grapheme cluster) regular expression:
        data = regex.findall(r'\X', text_with_emoji)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI for char in word):
                emoji_list.append(word)
        return emoji_list

    @staticmethod
    def extract_flags(text_with_flags):
        """Extract emoji flags from string"""
        flags = regex.findall(u'[\U0001F1E6-\U0001F1FF]', text_with_flags)
        return flags

    @staticmethod
    def extract_emoji(string_with_emoji: str) -> Set[str]:
        """Extract emoji and flags using regex package

        This is a new version to extract emoji (see old method:
        _extract_emoji_old). Code source:
        https://stackoverflow.com/a/49242754/4556479
        This method supports extracting grapheme clusters,
        emoji constructed of multiple emoji (the "perceived
        pictograms") e.g.: 👨‍👩‍👦‍👦

        Compare:
        A: _extract_emoji_old:
        Total emoji count for the 100 most
        used emoji in selected area: 27722.
        Total distinct emoji (DEC): 918
        B: _extract_emoji:
        Total emoji count for the 100 most
        used emoji in selected area: 25793.
        Total distinct emoji (DEC): 1349
        """

        emoji_split = Utils.split_emoji_count(string_with_emoji)
        emoji_list = [emoji for emoji in emoji_split]
        flags_list = Utils.extract_flags(string_with_emoji)
        emoji_list.extend(flags_list)
        return set(emoji_list)

    @staticmethod
    def _extract_emoji_old(string_with_emoji):
        """Extracts (one or more) emoji from string

        - uses emoji package
        str = str.decode('utf-32').encode('utf-32', 'surrogatepass')
        return list(c for c in str if c in emoji.UNICODE_EMOJI)

        c = a single character
        This code cannot cannot detect flags in the text, e.g.:
        _extract_emoji("🇵🇰 👧 🏿")
        i.e. that is because it iterates over every character.
        Unicode flags are a combination of two "regional indicator"
        characters which are not, individually, emoji.
        If you want to detect Unicode flags you'll need
        to check pairs of characters.

        there's also a bug in _check_emoji_type if emoji
        package is upgraded from 0.4.5 to 0.5.1
        see:
        https://stackoverflow.com/questions/49276977/how-to-extract-emojis-and-flags-from-strings-in-python?noredirect=1&lq=1
        """
        emoji_list = list(c for c in string_with_emoji if c in
                          emoji.UNICODE_EMOJI and
                          Utils._check_emoji_type(c) is True)
        return emoji_list

    @staticmethod
    def _surrogatepair(match):
        char = match.group()
        assert ord(char) > 0xffff
        encoded = char.encode('utf-16-le')
        return (
            chr(int.from_bytes(encoded[:2], 'little')) +
            chr(int.from_bytes(encoded[2:], 'little')))

    @staticmethod
    def _with_surrogates(text):
        """Process emoji with surrogates text

        test: text = '❤️👨‍⚕️'
        """
        _nonbmp = re.compile(r'[\U00010000-\U0010FFFF]')
        return _nonbmp.sub(Utils._surrogatepair, text)

    @staticmethod
    def _convert_encode_emoji(emoji_text):
        """Fix weird emoji encoding issue with surrogates

        see:
        https://stackoverflow.com/questions/52179465/best-and-clean-way-to-encode-emojis-python-from-text-file

        test: emoji_text = '❤️👨‍⚕️'
        """
        emoji_encoded = (emoji_text
                         .encode('utf-16', 'surrogatepass')
                         .decode('utf-16')
                         )
        return emoji_encoded

    @staticmethod
    def str2bool(str_text):
        """Convert any type of yes no string to
        bool representation"""
        if str_text.lower() in (
                'yes', 'true', 't', 'y', '1'):
            return True
        elif str_text.lower() in (
                'no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError(
                'Boolean value expected.')

    @staticmethod
    def get_rectangle_bounds(points):
        """Get rectangle bounds for numpy.ndarray of point coordinates"""
        RectangleBounds = namedtuple(
            'RectangleBounds',
            'lim_lat_min lim_lat_max lim_lng_min lim_lng_max')
        lim_y_min = np.min(points.T[1])
        lim_y_max = np.max(points.T[1])
        lim_x_min = np.min(points.T[0])
        lim_x_max = np.max(points.T[0])
        return RectangleBounds(lim_y_min, lim_y_max, lim_x_min, lim_x_max)

    @staticmethod
    def filter_tags(taglist: Iterable[str],
                    sort_out_always_set: Set[str],
                    sort_out_always_instr_set: Set[str]
                    ) -> Tuple[Set[str], int, int]:
        """Filter list of tags based on two stoplists

        Also removes numeric items and duplicates

        Args:
            taglist (Iterable[str]): List/Set of input tags to filter
            sort_out_always_set (Set[str]): Filter complete match
            sort_out_always_instr_set (Set[str]): Filter partial match

        Returns:
            Tuple[Set[str], int, int]: Filtered list,
                                       length of list and
                                       skipped number of items
        """

        count_tags = 0
        count_skipped = 0

        photo_tags_filtered = set()
        for tag in taglist:
            count_tags += 1
            # exclude numbers and those tags that are in sort_out_always_set
            # or sort_out_always_instr_set
            if (len(tag) == 1 or tag == '""'
                    or tag.isdigit()
                    or tag in sort_out_always_set):
                count_skipped += 1
                continue
            for in_str_partial in sort_out_always_instr_set:
                if in_str_partial in tag:
                    count_skipped += 1
                    break
            else:
                photo_tags_filtered.add(tag)
        return (photo_tags_filtered,
                count_tags, count_skipped)

    @staticmethod
    def get_index_of_tup(
            l_tuple_str: List[Tuple[str, int]], index: int, value: str) -> int:
        """Get index pos from list of tuples.

        Stops iterating through the list as
        soon as it finds the value
        """
        for pos, tuple_str in enumerate(l_tuple_str):
            if tuple_str[index] == value:
                return pos
        # Matches behavior of list.index
        raise ValueError("list.index(x): x not in list")

    @staticmethod
    def get_locname(item: str, loc_name_dict: Dict[str, str]):
        """Gets location name from ID, if available"""
        if loc_name_dict:
            item_name = loc_name_dict.get(item, item)
        else:
            # default to item if dict key not found
            item_name = item
        return item_name
