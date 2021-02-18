# -*- coding: utf-8 -*-

"""
Config processing for tag maps package.
"""

from __future__ import absolute_import

import argparse
import configparser
import logging
import os
import warnings
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional

import fiona
from shapely.geometry import shape

from tagmaps import __version__
from tagmaps.classes.utils import Utils
from tagmaps.classes.shared_structure import ConfigMap


class BaseConfig:
    """Optional class for handling of typical config parameters"""

    def __init__(self):
        # Set Default Config options here
        # or define options as input args
        self.data_source = "lbsn"
        self.cluster_tags = True
        self.cluster_locations = True
        self.epsg = True
        self.remove_long_tail = True
        self.cluster_emoji = True
        self.topic_modeling = False
        self.write_cleaned_data = True
        self.local_saturation_check = False
        self.tokenize_japanese = False  # currently not implemented
        self.shapefile_intersect = None
        self.shapefile_exclude = None
        self.ignore_stoplists = False
        self.selectionlist_emoji = None
        self.selectionlist_tags = None
        self.stoplist_emoji = None
        self.stoplist_tags = None
        self.stoplist_user = None
        self.stoplist_places = None
        self.ignore_place_corrections = False
        self.statistics_only = False
        self.limit_bottom_user_count = 5
        self.write_gis_comp_line = True
        self.auto_mode = False
        self.max_items = 1000
        self.filter_origin = None
        self.logging_level = logging.INFO
        self.input_folder = None
        self.output_folder = None
        self.config_folder = None
        self.cluster_cut_distance = None

        # additional auto settings
        self.sort_out_always_set = set()
        self.sort_out_always_instr_set = set()
        self.override_crs = None
        self.crs_proj = None
        self.epsg_code = ""
        self.sort_out_places_set = set()
        self.sort_out_user_set = None
        self.sort_out_places = False
        self.sort_out_emoji_set = None
        self.select_emoji_set = None
        self.select_tags_set = None
        self.correct_places = False
        self.correct_place_latlng_dict = dict()

        # initialization
        resource_path = os.environ.get("TAGMAPS_RESOURCES")

        self.pathname = Path.cwd()
        if resource_path:
            self.resource_path = Path(resource_path)
        else:
            self.resource_path = self.pathname
        self.load_from_intermediate = None
        self.parse_args()

        # set logger
        self.log = Utils.set_logger(
            self.output_folder, self.logging_level)

        self.load_filterlists()

        self.source_map = self.load_sourcemapping()
        self.set_glob_options()

    def parse_args(self):
        """Parse init args and set default values

        Note: All paths are relative. If you wish to use another path entirely,
        set TAGMAPS_RESOURCES environment variable to the absolute path to use
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--version',
                            action='version',
                            version=f'tagmaps {__version__}')
        parser.add_argument("-s",
                            "--source",
                            default="lbsn",
                            help="Specify type of source of data. "
                            "This is needed to read data. "
                            "Defaults to 'lbsn'.")
        parser.add_argument("-r",
                            "--disable_remove_longtail",
                            action="store_true",
                            help="This will disable exclusion "
                            "of tags that are used by only a "
                            "small number of users")
        parser.add_argument("-e",
                            "--epsg",
                            help="If provided, will overwrite "
                            "auto EPSG code")
        parser.add_argument("-t", "--disable_cluster_tags",
                            action="store_true",
                            help="Disable cluster tag locations"
                            "No clusters will be generated per "
                            "distinct tag.")
        parser.add_argument("-p",
                            "--disable_cluster_locations",
                            action="store_true",
                            help="Disable cluster of post locations "
                            )
        parser.add_argument("-c",
                            "--local_saturation_check",
                            action="store_true",
                            help="Will attempt to exclude any tags that "
                            "are (over)used at above a certain percentage "
                            "of locations in processing extent. This "
                            "may improve legibility of tag maps at "
                            "larger scales"
                            )
        parser.add_argument("-o",
                            "--disable_cluster_emoji",
                            action="store_true",
                            help="Disable cluster of "
                            "emoji in addition to tags.")
        parser.add_argument("-m",
                            "--topic_modeling",
                            action="store_true",
                            help="This will used topic modeling "
                            "to detect groups of tags (based on "
                            "Latent Dirichlet Allocation). "
                            "[Not fully implemented: currently, if this flag "
                            "is set, tagmaps will output a list of merged "
                            "terms per user which can be used in topic "
                            "modeling, e.g. Latent Dirichlet Allocation "
                            "algorithms]")
        parser.add_argument("-w",
                            "--disable_write_cleaneddata",
                            action="store_true",
                            help="This will disable "
                            "write out of a file limited to the data "
                            "that will be used for tag clustering "
                            "(filtered based on stoplists, clipped boundary, "
                            "minimum user threshold etc.)"
                            )
        parser.add_argument("-i",
                            "--shapefile_intersect",
                            type=Path,
                            help="Provide a relative path to a shapefile "
                            "to clip data prior to clustering. The shapefile "
                            "must be projected to WGS1984 (4326) Projection. "
                            "Multipart shapefiles are supported, but be "
                            "careful with polygon holes: it is recommended to "
                            "exclude polygon holes with a separate shapefile "
                            "using the --shapefile_exclude flag.")
        parser.add_argument("--shapefile_exclude",
                            type=Path,
                            help="Provide a relative path to a shapefile "
                            "to exclude data prior to clustering. In case "
                            "--shapefile_intersect is also used, the exclusion "
                            "here applies after inclusion.")
        parser.add_argument("-n",
                            "--ignore_stoplists",
                            action="store_true",
                            help="Set this flag to ignore any stoplists, "
                            "even if available/supplied. This is useful "
                            "if files that are places in 00_Config folder "
                            "must be temporarily ignored."
                            )
        parser.add_argument("--stoplist_emoji",
                            type=Path,
                            help="Supply a relative path to a text file "
                            "containing emoji to ignore "
                            "during emoji clustering. "
                            "Format: one entry per line."
                            )
        parser.add_argument("--stoplist_tags",
                            type=Path,
                            help="Supply a relative path to a text file "
                            "containing terms to ignore during tag clustering. "
                            "This list is supplemental to "
                            "00_Config/SortOutAlways.txt, if such file exists. "
                            "Format: one entry per line."
                            )
        parser.add_argument("--stoplist_user",
                            type=Path,
                            help="Supply a relative path to a text file "
                            "containing user (guids) to ignore during "
                            "tag clustering. Format: one entry per line."
                            )
        parser.add_argument("--stoplist_places",
                            type=Path,
                            help="Supply a relative path to a text file "
                            "containing places (guids) to ignore during tag clustering. "
                            "This list is supplemental to "
                            "00_Config/SortOutPlaces.txt, if such file exists. "
                            "Format: one entry per line."
                            )
        parser.add_argument("--selectionlist_emoji",
                            type=Path,
                            help="Supply a relative path to a text file "
                            "containing emoji, as a positive filter list "
                            "for selecting a subset of emoji to focus on. "
                            "Format: one entry per line."
                            )
        parser.add_argument("--selectionlist_tags",
                            type=Path,
                            help="Supply a relative path to a text file "
                            "containing tags, as a positive filter list "
                            "for selecting a subset of tags to focus on. "
                            "Format: one entry per line."
                            )
        parser.add_argument("-b",
                            "--ignore_place_corrections",
                            action="store_true",
                            help="Set this flag to ignore place corrections, "
                            "even if available, supplied."
                            )
        parser.add_argument("--statistics_only",
                            action="store_true",
                            help="Do not cluster, only read input data"
                            " and output statistics. Suitable to get an "
                            "overview of input data."
                            )
        parser.add_argument("-d", "--cluster_cut_distance",
                            help="Provide a cluster cut distance (in meters) "
                            "where the clustering will be stopped. This "
                            "will override the auto detection "
                            "of cluster distance.",
                            type=float)
        parser.add_argument("-l",
                            "--limit_bottom_usercount",
                            type=int,
                            default=5,
                            help="Remove all tags that are used by "
                            "less than x photographers.")
        parser.add_argument("-g",
                            "--disable_write_gis_comp_line",
                            action="store_true",
                            default=True,
                            help="Disables writing placeholder "
                            "entry after headerline "
                            "for avoiding GIS import format issues. "
                            "Some GIS programs will decide format of "
                            "columns based on the first data line in a CSV. "
                            "This setting makes sure there're no empty fields "
                            "in the first line.",
                            )
        parser.add_argument("-a",
                            "--auto_mode",
                            action="store_true",
                            help="If set, no user input will "
                            "be requested during processing. "
                            "This flag is suitable if you're running in a "
                            "command line only environment (WSL) that "
                            "cannot use the tKinter GUI.",
                            )
        parser.add_argument("-f",
                            "--filter_origin",
                            type=str,
                            help="If provided, will filter input data "
                            "based on origin_id column and the value "
                            "provided.",
                            )
        parser.add_argument("-v", "--verbose",
                            help="Increase output verbosity",
                            action="store_true")
        parser.add_argument("-x", "--max_items",
                            help="Number of distinct items to process",
                            default=1000,
                            type=int)
        parser.add_argument("-q", "--output_folder",
                            help="Relative path to output folder",
                            default="02_Output",
                            type=Path)
        parser.add_argument("-j", "--input_folder",
                            help="Relative path to input folder",
                            default="01_Input",
                            type=Path)
        parser.add_argument("-k", "--config_folder",
                            help="Relative path to config folder",
                            default="00_Config",
                            type=Path)
        parser.add_argument("-u", "--load_intermediate",
                            help="A (relative) path to load from "
                            "intermediate (cleaned) data",
                            type=Path)

        args = parser.parse_args()
        if args.verbose:
            self.logging_level = logging.DEBUG
        if args.source:
            self.data_source = args.source
        if args.disable_cluster_tags:
            self.cluster_tags = False
        if args.disable_cluster_locations:
            self.cluster_locations = False
        if args.epsg is None:
            self.override_crs = None
        else:
            self.load_custom_crs(self.epsg)
        if args.disable_remove_longtail:
            self.remove_long_tail = False
        if args.disable_cluster_emoji:
            self.cluster_emoji = False
        if args.topic_modeling:
            self.topic_modeling = True
        if args.disable_write_cleaneddata:
            self.write_cleaned_data = False
        if args.local_saturation_check:
            self.local_saturation_check = True
        if args.shapefile_intersect:
            shp_path = Utils.check_folder_file(
                self.resource_path / args.shapefile_intersect)
            self.shapefile_intersect = self.load_shapefile(shp_path)
        if args.shapefile_exclude:
            shp_path = Utils.check_folder_file(
                self.resource_path / args.shapefile_exclude)
            self.shapefile_exclude = self.load_shapefile(shp_path)
        if args.ignore_stoplists:
            self.ignore_stoplists = True
        if args.selectionlist_emoji:
            self.selectionlist_emoji = Utils.check_folder_file(
                self.resource_path / args.selectionlist_emoji)
        if args.selectionlist_tags:
            self.selectionlist_tags = \
                self.resource_path / args.selectionlist_tags
        if args.stoplist_emoji:
            self.stoplist_emoji = Utils.check_folder_file(
                self.resource_path / args.stoplist_emoji)
        if args.stoplist_tags:
            self.stoplist_tags = Utils.check_folder_file(
                self.resource_path / args.stoplist_tags)
        if args.stoplist_user:
            self.stoplist_user = Utils.check_folder_file(
                self.resource_path / args.stoplist_user)
        if args.stoplist_places:
            self.stoplist_places = Utils.check_folder_file(
                self.resource_path / args.stoplist_places)
        if args.ignore_place_corrections:
            self.ignore_place_corrections = True
        if args.statistics_only:
            self.statistics_only = True
        if args.limit_bottom_usercount:
            self.limit_bottom_user_count = args.limit_bottom_usercount
        if args.disable_write_gis_comp_line:
            self.write_gis_comp_line = False
        if args.auto_mode:
            self.auto_mode = args.auto_mode
        if args.filter_origin:
            self.filter_origin = args.filter_origin
        if args.max_items:
            self.max_items = args.max_items
        if args.output_folder:
            # default: 02_Output
            self.output_folder = Utils.check_folder_file(
                self.resource_path / args.output_folder, create_folder=True)
        if args.input_folder:
            self.input_folder = Utils.check_folder_file(
                self.resource_path / args.input_folder)
        if args.config_folder:
            self.config_folder = Utils.check_folder_file(
                self.resource_path / args.config_folder)
        if args.load_intermediate:
            self.load_from_intermediate = Utils.check_folder_file(
                self.resource_path / args.load_intermediate)
        if args.cluster_cut_distance:
            self.cluster_cut_distance = args.cluster_cut_distance

    def load_filterlists(self):
        """Load filterlists for filtering terms (in-string and full match)
        and places, including place lat/lng corrections.
        """
        # locations for files
        sort_out_always_file = Path(
            self.config_folder / "SortOutAlways.txt")
        sort_out_always_instr_file = Path(
            self.config_folder / "SortOutAlways_inStr.txt")
        sort_out_places_file = Path(
            self.config_folder / "SortOutPlaces.txt")
        correct_place_latlng_file = Path(
            self.config_folder / "CorrectPlaceLatLng.txt")
        # load lists
        self.sort_out_always_set = self.load_filterlist(sort_out_always_file)
        if self.stoplist_tags:
            stoplist_tags_set = self.load_filterlist(self.stoplist_tags)
            if stoplist_tags_set:
                self.sort_out_always_set.update(stoplist_tags_set)
        self.sort_out_always_instr_set = self.load_filterlist(
            sort_out_always_instr_file)
        self.sort_out_places_set = self.load_place_stoplist(
            sort_out_places_file)
        if self.stoplist_places:
            stoplist_places_set = self.load_filterlist(self.stoplist_places)
            if stoplist_places_set:
                self.sort_out_places_set.update(stoplist_places_set)
        if self.stoplist_user:
            self.sort_out_user_set = self.load_filterlist(
                self.stoplist_user)
        if self.stoplist_emoji:
            self.sort_out_emoji_set = self.load_filterlist(
                self.stoplist_emoji)
        if self.selectionlist_emoji:
            self.select_emoji_set = self.load_filterlist(
                self.selectionlist_emoji)
        if self.selectionlist_tags:
            self.select_tags_set = self.load_filterlist(
                self.selectionlist_tags)
        if not self.ignore_place_corrections:
            self.correct_place_latlng_dict = self.load_place_corrections(
                correct_place_latlng_file)
            if self.correct_place_latlng_dict:
                self.correct_places = True
        # log results
        self._report_loaded_lists()

    def _report_loaded_lists(self):
        """Report stats of loaded stop & selection lists"""
        Utils.report_listload(
            self.sort_out_always_set, "stoplist items")
        Utils.report_listload(
            self.sort_out_always_instr_set, "inStr stoplist items")
        Utils.report_listload(
            self.sort_out_places_set, "stoplist places")
        Utils.report_listload(
            self.correct_place_latlng_dict, "place lat/lng corrections")
        Utils.report_listload(
            self.sort_out_user_set, "user stoplist items")
        Utils.report_listload(
            self.select_emoji_set, "emoji selection items")
        Utils.report_listload(
            self.select_tags_set, "tags selection items")

    def load_filterlist(self, file: Path) -> Optional[Set[str]]:
        """Loads filterlist of terms from file returns set"""
        if self.ignore_stoplists is True:
            return
        if not file.is_file():
            self.log.warning(f"{file} not found.")
            return
        store_set = set()
        with open(file, newline="", encoding="utf8") as f_handle:
            store_set = {line.lower().rstrip("\r\n") for line in f_handle}
        return store_set

    def load_place_stoplist(self, file):
        """Loads stoplist places from file and stores in set"""
        if not os.path.isfile(file) or self.ignore_stoplists is True:
            return
        store_set = set()
        with open(file, newline="", encoding="utf8") as f_handle:
            f_handle.readline()
            # Get placeid
            store_set = {
                line.rstrip("\r\n").split(",")[0]
                for line in f_handle if len(line) > 0}
        self.sort_out_places = True
        return store_set

    @classmethod
    def load_place_corrections(
            cls, file: Path) -> Optional[Dict[str, Tuple[float, float]]]:
        """Fills dictionary with list of corrected lat/lng entries
        e.g.: Dictionary: placeid = lat, lng

        - sets self.correct_places to True
        """
        store_dict = dict()
        if not file.is_file():
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
        return store_dict

    def load_shapefile(self, shapefile_path: Path) -> List[shape]:
        """Imports single or multi polygon shapefile for intersecting points"""
        poly_shape = fiona.open(shapefile_path)
        vertices_count = 0
        shp_geom = []
        if len(poly_shape) == 1:
            # simple polygon
            geom = next(iter(poly_shape))
            vertices_count = len(geom["geometry"]["coordinates"][0])
            shp_geom.append(shape(geom["geometry"]))
        else:
            # multipolygon
            for pol in poly_shape:
                for part in pol["geometry"]["coordinates"]:
                    vertices_count += len(part)
                shp_geom.append(shape(pol['geometry']))
        poly_count = len(shp_geom)
        poly_s = ""
        if poly_count > 1:
            poly_s = "s"
        print(
            f'Loaded shapefile with '
            f'{poly_count} polygon{poly_s} '
            f'and '
            f'{vertices_count} vertices.'
        )
        return shp_geom

    def load_custom_crs(self, override_crs):
        """Optionally, create custom crs for projecting
        data base don user input

        Note: not fully implemented
        """
        self.crs_proj = f"epsg:{override_crs}"
        print(f"Custom CRS set: {self.crs_proj}")
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
            orig_path = (
                self.config_folder /
                f'sourcemapping_fromlbsn.cfg'
            )
            if os.path.exists(orig_path):
                warnings.warn(
                    "Please rename resources/sourcemapping_fromlbsn.cfg "
                    "to sourcemapping_lbsn.cfg. The former name will be "
                    "deprecated in the future.", DeprecationWarning)
                mapping_config_path = orig_path
            else:
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
