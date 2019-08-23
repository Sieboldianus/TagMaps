import argparse
import argdown
"""Parse init args and set default values

"""
parser = argparse.ArgumentParser(prog="tagmaps")
parser.add_argument('--version',
                    action='version',
                    version=f'tagmaps 0.19.1')
parser.add_argument("-s",
                    "--source",
                    default="lbsn",
                    help="Specify type of source of data. "
                    "This is needed to read data. "
                    "Defaults to 'lbsn'.")
parser.add_argument("-r",
                    "--disable_remove_longtail",
                    action="store_true",
                    help="This will disable exclusion"
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
                    "[Not implemented]")
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
                    action="store_true",
                    help="If set, clip "
                    "data to shapefile (specify path "
                    "with --shapefilePath)"
                    )
parser.add_argument("-f",
                    "--shapefile_path",
                    help="Provide a (full) path to a shapefile "
                    "to clip data prior to clustering.")
parser.add_argument("-n",
                    "--ignore_stoplists",
                    action="store_true",
                    help="If stoplist is available "
                    "ignore it."
                    )
parser.add_argument("-b",
                    "--ignore_place_corrections",
                    action="store_true",
                    help="If place corrections are available, "
                    "ignore them."
                    )
parser.add_argument("-d",
                    "--statistics_only",
                    action="store_true",
                    help="Do not cluster, only read input data"
                    " and calculate statistics."
                    )
parser.add_argument("-l",
                    "--limit_bottom_usercount",
                    type=int,
                    default=5,
                    help="Remove all tags that are used by "
                    "less than x photographers. Defaults to 5.")
parser.add_argument("-g",
                    "--disable_write_gis_comp_line",
                    action="store_true",
                    default=True,
                    help="Disables writing placeholder "
                    "entry after headerline "
                    "for avoiding GIS import format issues",
                    )
parser.add_argument("-a",
                    "--auto_mode",
                    action="store_true",
                    help="If set, no user input will "
                    "be requested during processing.",
                    )
parser.add_argument("-fO",
                    "--filter_origin",
                    type=str,
                    help="If provided, will filter input data "
                    "based on origin_id column.",
                    )
parser.add_argument("-v", "--verbose",
                    help="Increase output verbosity",
                    action="store_true")
parser.add_argument("-x", "--max_items",
                    help="Number of distinct items to process",
                    default=1000,
                    type=int)
parser.add_argument("-q", "--output_folder",
                    help="Path to output folder",
                    default="02_Output",
                    type=str)
parser.add_argument("-j", "--input_folder",
                    help="Path to input folder",
                    default="01_Input",
                    type=str)
parser.add_argument("-k", "--config_folder",
                    help="Path to config folder",
                    default="00_Config",
                    type=str)
parser.add_argument("-u", "--load_intermediate",
                    help="Load from intermediate (cleaned) data "
                    "from path",
                    type=str)

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
    self.shapefile_intersect = True
if args.shapefile_path:
    self.shapefile_path = args.shapefile_path
if args.ignore_stoplists:
    self.ignore_stoplists = True
if args.ignore_place_corrections:
    self.ignore_place_corrections = True
if args.statistics_only:
    self.statistics_only = True
if args.limit_bottom_usercount:
    self.limit_bottom_user_count = int(args.limit_bottom_usercount)
if args.disable_write_gis_comp_line:
    self.write_gis_comp_line = False
if args.auto_mode:
    self.auto_mode = args.auto_mode
if args.filter_origin:
    self.filter_origin = args.filter_origin
if args.max_items:
    self.max_items = args.max_items
if args.output_folder:
    self.output_folder = args.output_folder
if args.input_folder:
    self.input_folder = args.input_folder
if args.config_folder:
    self.config_folder = args.config_folder
if args.load_intermediate:
    self.load_from_intermediate = args.load_intermediate
