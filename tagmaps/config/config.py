# -*- coding: utf-8 -*-

"""
Config processing for tag maps package.
"""

from __future__ import absolute_import

import argparse
import configparser
import csv
import logging
import os
import sys
from pathlib import Path

import fiona
import pyproj
from shapely.geometry import shape


class BaseConfig:
    """Optional class for handling of typical config parameters"""

    def __init__(self):
        # Set Default Config options here
        # or define options as input args
        self.data_source = "fromLBSN"
        self.cluster_tags = True
        self.cluster_locations = True
        self.epsg = True
        self.remove_long_tail = True
        self.cluster_emoji = True
        self.topic_modeling = False
        self.write_cleaned_data = True
        self.local_saturation_check = False
        self.tokenize_japanese = False  # currently not implemented
        self.shapefile_intersect = False
        self.shapefile_path = ""
        self.ignore_stoplists = False
        self.ignore_place_corrections = False
        self.statistics_only = False
        self.limit_bottom_user_count = 5
        self.write_gis_comp_line = True
        self.auto_mode = False
        self.max_items = 1000
        self.filter_origin = None
        self.logging_level = logging.INFO

        # additional auto settings
        self.sort_out_always_set = set()
        self.sort_out_always_instr_set = set()
        self.override_crs = None
        self.crs_proj = None
        self.epsg_code = ""
        self.sort_out_places_set = set()
        self.sort_out_places = False
        self.correct_places = False
        self.correct_place_latlng_dict = dict()
        self.shp_geom = None

        # initialization
        resource_path = os.environ.get("TAGMAPS_RESOURCES")

        self.pathname = Path.cwd()
        if resource_path:
            self.resource_path = Path(resource_path)
        else:
            self.resource_path = self.pathname
        self.config_folder = self.resource_path / "00_Config"
        self.input_folder = self.resource_path / "01_Input"
        self.output_folder = Path.cwd() / "02_Output"
        self.load_from_intermediate = None
        self.parse_args()

        if not self.load_from_intermediate and not self.input_folder.exists():
            raise ValueError(f"Folder {self.input_folder} not found.")
        if not self.config_folder.exists():
            raise ValueError(f"Folder {self.config_folder} not found.")

        self.load_filterlists()
        if self.shapefile_intersect:
            self.load_shapefile()
        self.source_map = self.load_sourcemapping()
        self.set_glob_options()

    def parse_args(self):
        """Parse init args and set default values

        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-s",
                            "--source",
                            default="fromLBSN",
                            help="Specify type of source of data. "
                            "This is needed to read data. "
                            "Defaults to 'fromLBSN'.")
        parser.add_argument("-r",
                            "--disableRemoveLongTail",
                            action="store_true",
                            help="This will disable exclusion"
                            "of tags that are used by only a "
                            "small number of users")
        parser.add_argument("-e",
                            "--EPSG",
                            help="If provided, will overwrite "
                            "auto EPSG code")
        parser.add_argument("-t", "--disableClusterTags",
                            action="store_true",
                            help="Disable cluster tag locations"
                            "No clusters will be generated per "
                            "distinct tag.")
        parser.add_argument("-p",
                            "--disableClusterLocations",
                            action="store_true",
                            help="Disable cluster of post locations "
                            )
        parser.add_argument("-c",
                            "--localSaturationCheck",
                            action="store_true",
                            help="Will attempt to exclude any tags that "
                            "are (over)used at above a certain percentage "
                            "of locations in processing extent. This "
                            "may improve legibility of tag maps at "
                            "larger scales"
                            )
        # parser.add_argument("-j",
        #                     "--tokenizeJapanese",
        #                     action="store_true",
        #                     help="Japanese language requires "
        #                     "tokenization prior to clustering. "
        #                     "Disabled by default. Note:"
        #                     "Not fully implemented"
        #                     )
        parser.add_argument("-o",
                            "--disableClusterEmoji",
                            action="store_true",
                            help="Disable cluster of "
                            "emoji in addition to tags.")
        parser.add_argument("-m",
                            "--topicModeling",
                            action="store_true",
                            help="This will used topic modeling "
                            "to detect groups of tags (based on "
                            "Latent Dirichlet Allocation). "
                            "[Not implemented]")
        parser.add_argument("-w",
                            "--disableWriteCleanedData",
                            action="store_true",
                            help="This will disable "
                            "write out of a file limited to the data "
                            "that will be used for tag clustering "
                            "(filtered based on stoplists, clipped boundary, "
                            "minimum user threshold etc.)"
                            )
        parser.add_argument("-i",
                            "--shapefileIntersect",
                            action="store_true",
                            help="If set, clip "
                            "data to shapefile (specify path "
                            "with --shapefilePath)"
                            )
        parser.add_argument("-f",
                            "--shapefilePath",
                            default="",
                            help="Provide a (full) path to a shapefile "
                            "to clip data prior to clustering.")
        parser.add_argument("-is",
                            "--ignoreStoplists",
                            action="store_true",
                            help="If stoplist is available "
                            "ignore it."
                            )
        parser.add_argument("-ip",
                            "--ignorePlaceCorrections",
                            action="store_true",
                            help="If place corrections are available, "
                            "ignore them."
                            )
        parser.add_argument("-stat",
                            "--statisticsOnly",
                            action="store_true",
                            help="Do not cluster, only read input data"
                            " and calculate statistics."
                            )
        parser.add_argument("-lmuc",
                            "--limitBottomUserCount",
                            type=int,
                            default=5,
                            help="Remove all tags that are used by "
                            "less than x photographers. Defaults to 5.")
        parser.add_argument("-wG",
                            "--disableWriteGISCompLine",
                            action="store_true",
                            default=True,
                            help="Writes placeholder entry after headerline "
                            "for avoiding GIS import format issues",
                            )
        parser.add_argument("-aM",
                            "--autoMode",
                            action="store_true",
                            help="If set, no user input will "
                            "be requested during processing.",
                            )
        parser.add_argument("-fO",
                            "--filterOrigin",
                            type=str,
                            default=None,
                            help="If provided, will filter input data "
                            "based on origin_id column.",
                            )
        parser.add_argument("-v", "--verbose",
                            help="Increase output verbosity",
                            action="store_true")
        parser.add_argument("-mI", "--maxItems",
                            help="Number of distinct items to process",
                            default=1000,
                            type=int)
        parser.add_argument("-oF", "--outputFolder",
                            help="Complete path for output folder",
                            default="",
                            type=str)
        parser.add_argument("-iF", "--inputFolder",
                            help="Complete path for input folder",
                            default="",
                            type=str)
        parser.add_argument("-cF", "--configFolder",
                            help="Complete path for config folder",
                            default="",
                            type=str)
        parser.add_argument("-lI", "--loadIntermediate",
                            help="Load from intermediate (cleaned) data "
                            "from path",
                            default="",
                            type=str)

        args = parser.parse_args()
        if args.verbose:
            self.logging_level = logging.DEBUG
        if args.source:
            self.data_source = args.source
        if args.disableClusterTags:
            self.cluster_tags = False
        if args.disableClusterLocations:
            self.cluster_locations = False
        if args.EPSG is None:
            self.override_crs = None
        else:
            self.load_custom_crs(self.epsg)
        if args.disableRemoveLongTail:
            self.remove_long_tail = False
        if args.disableClusterEmoji:
            self.cluster_emoji = False
        if args.topicModeling:
            self.topic_modeling = True
        if args.disableWriteCleanedData:
            self.write_cleaned_data = False
        if args.localSaturationCheck:
            self.local_saturation_check = True
        if args.shapefileIntersect:
            self.shapefile_intersect = True
        if args.shapefilePath:
            self.shapefile_path = args.shapefilePath
        if args.ignoreStoplists:
            self.ignore_stoplists = True
        if args.ignorePlaceCorrections:
            self.ignore_place_corrections = True
        if args.statisticsOnly:
            self.statistics_only = True
        if args.limitBottomUserCount:
            self.limit_bottom_user_count = int(args.limitBottomUserCount)
        if args.disableWriteGISCompLine:
            self.write_gis_comp_line = False
        if args.autoMode:
            self.auto_mode = args.autoMode
        if args.filterOrigin:
            self.filter_origin = args.filterOrigin
        if args.maxItems:
            self.max_items = args.maxItems
        if args.outputFolder:
            self.output_folder = args.outputFolder
        if args.inputFolder:
            self.input_folder = args.inputFolder
        if args.configFolder:
            self.config_folder = args.configFolder
        if args.loadIntermediate:
            self.load_from_intermediate = args.loadIntermediate

    def load_filterlists(self):
        """Load filterlists for filtering terms (instring and full match)
        and places, including place lat/lng corrections.
        """
        # locations for files
        sort_out_always_file = (
            self.config_folder / "SortOutAlways.txt")
        sort_out_always_instr_file = (
            self.config_folder / "SortOutAlways_inStr.txt")
        sort_out_places_file = (
            self.config_folder / "SortOutPlaces.txt")
        correct_place_latlng_file = (
            self.config_folder / "CorrectPlaceLatLng.txt")
        # load lists
        self.sort_out_always_set = self.load_stoplists(sort_out_always_file)
        self.sort_out_always_instr_set = self.load_stoplists(
            sort_out_always_instr_file)
        self.sort_out_places_set = self.load_place_stoplist(
            sort_out_places_file)
        self.correct_place_latlng_dict = self.load_place_corrections(
            correct_place_latlng_file
        )
        # print results, ignore empty
        try:
            print(f"Loaded {len(self.sort_out_always_set)} "
                  f"stoplist items.")
            print(f"Loaded {len(self.sort_out_always_instr_set)} "
                  f"inStr stoplist items.")
            print(f"Loaded {len(self.sort_out_places_set)} stoplist places.")
            print(f"Loaded {len(self.correct_place_latlng_dict)} "
                  f"place lat/lng corrections."
                  )
        except TypeError:
            pass

    def load_stoplists(self, file):
        """Loads stoplist terms from file and stores in set"""
        if self.ignore_stoplists is True:
            return
        if not os.path.isfile(file):
            print(f"{file} not found.")
            return
        store_set = set()
        with open(file, newline="", encoding="utf8") as f_handle:
            store_set = set(
                [line.lower().rstrip("\r\n") for line in f_handle])
        return store_set

    def load_place_stoplist(self, file):
        """Loads stoplist places from file and stores in set"""
        if not os.path.isfile(file) or self.ignore_stoplists is True:
            return
        store_set = set()
        with open(file, newline="", encoding="utf8") as f_handle:
            f_handle.readline()
            # Get placeid
            store_set = set(
                [line.rstrip("\r\n").split(",")[0]
                 for line in f_handle if len(line) > 0]
            )
        self.sort_out_places = True
        return store_set

    def load_place_corrections(self, file):
        """Fills dictionary with list of corrected lat/lng entries
        e.g.: Dictionary: placeid = lat, lng

        - sets self.correct_places to True
        """
        store_dict = dict()
        if os.path.isfile(file) or self.ignore_place_corrections is True:
            return
        with open(file, newline="", encoding="utf8") as f_handle:
            f_handle.readline()
            for line in f_handle:
                if not line:
                    continue
                linesplit = line.rstrip("\r\n").split(",")
                if len(linesplit) == 1:
                    continue
                store_dict[linesplit[0]] = (linesplit[1], linesplit[2])
        self.correct_places = True
        return store_dict

    def load_shapefile(self):
        """Imports single polygon shapefile for intersecting points"""
        if self.shapefile_intersect is False:
            return
        if self.shapefile_path == "":
            sys.exit(f"No Shapefile-Path specified. Exiting..")
            return
        poly_shape = fiona.open(self.shapefile_path)
        first = poly_shape.next()
        print(
            f'Loaded Shapefile with '
            f'{str(len(first["geometry"]["coordinates"][0]))}'
            f' Vertices.'
        )
        self.shp_geom = shape(first["geometry"])
        # For Multi-Polygon:
        # - not yet implemented
        ###
        # vcount = PShape.next()['geometry']['coordinates']
        # #needed for count of vertices
        # geom = MultiPolygon([shape(pol['geometry']) for pol
        # in PShape])
        # shp_geom = geom
        # print("Loaded Shapefile with Vertices ",
        # sum([len(poly[0]) for poly in vcount])) # (GeoJSON format)

    def load_custom_crs(self, override_crs):
        """Optionally, create custom crs for projecting
        data base don user input

        Note: not fully implemented
        """
        self.crs_proj = pyproj.Proj(init="epsg:{0}".format(override_crs))
        print("Custom CRS set: " + str(self.crs_proj.srs))
        self.epsg_code = override_crs

    def load_sourcemapping(self):
        """Loads source mapping, if available.

        Otherwise, try to read structure from first line of CSV.
        """
        mapping_config_path = (
            self.config_folder /
            f"sourcemapping_{self.data_source.lower()}.cfg"
        )
        if not os.path.exists(mapping_config_path):
            exit("Source mapping does not exist: "
                 f"sourcemapping_{self.data_source.lower()}.cfg")
        source_config = configparser.ConfigParser()
        source_config.read(mapping_config_path)
        source_config_py = ConfigMap(source_config)
        return source_config_py

    @staticmethod
    def set_glob_options():
        """Includes global options in other packages to be set
        prior execution"""
        # unused


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
