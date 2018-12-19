# -*- coding: utf-8 -*-

import argparse
import os
import sys

class BaseConfig():
    def __init__(self):
        ## Set Default Config options here
        ## or define options as input args
        self.d_source = "fromLBSN"
        self.cluster_tags = True
        self.cluster_photos = True
        self.epsg = True
        self.remove_long_tail = True
        self.cluster_emoji = True
        self.topic_modeling  = False
        self.write_cleaned_data = True
        self.local_saturation_check = True
        self.tokenize_japanese = False # currently not implemented
        self.shapefile_intersect = False
        self.shapefile_path = ""
        self.ignore_stoplists = False
        self.ignore_place_corrections = False
        self.statistics_only = False
        self.limit_bottom_user_count = 5
        self.write_gis_comp_line = True #

        # additional auto settings
        self.sort_out_always_set = set()
        self.sort_out_always_instr_set = set()
        self.override_crs = None
        self.crs_proj = ''
        self.epsg_code = ''

    def parse_args(self):
        """Parse init args and set default values

        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', "--source", default= "fromLBSN")
        parser.add_argument('-r', "--removeLongTail", action='store_true', default= True)
        parser.add_argument('-e', "--EPSG")
        parser.add_argument('-t', "--clusterTags", action='store_true', default= True)
        parser.add_argument('-p', "--clusterPhotos", action='store_true', default= True)
        parser.add_argument('-c', "--localSaturationCheck", action='store_true', default= False)
        parser.add_argument('-j', "--tokenizeJapanese", action='store_true', default= False)
        parser.add_argument('-o', "--clusterEmojis", action='store_true', default= True)
        parser.add_argument('-m', "--topicModeling", action='store_true', default= False)
        parser.add_argument('-w', "--writeCleanedData", action='store_true', default= True)
        parser.add_argument('-i', "--shapefileIntersect", action='store_true', default= False)
        parser.add_argument('-f', "--shapefilePath", default= "")
        parser.add_argument('-is',"--ignoreStoplists", action='store_true', default= False)
        parser.add_argument('-ip',"--ignorePlaceCorrections", action='store_true', default= False)
        parser.add_argument('-stat',"--statisticsOnly", action='store_true', default= False)
        parser.add_argument('-lmuc',"--limitBottomUserCount", type=int, default=5)
        parser.add_argument('-wG',"--writeGISCompLine", action='store_true', default= True,
                            help="writes placeholder entry after headerline for avoiding GIS import format issues")

        args = parser.parse_args()
        if args.source:
            self.d_source = args.source
        if args.clusterTags:
            self.cluster_tags = args.clusterTags
        if args.clusterPhotos:
            self.cluster_photos = args.clusterPhotos
        if args.EPSG is None:
            self.override_crs = None
        else:
            self.load_custom_crs(self.epsg)
        if args.removeLongTail:
            self.remove_long_tail = args.removeLongTail
        if args.clusterEmojis:
            self.cluster_emoji = args.clusterEmojis
        if args.topicModeling:
            self.topic_modeling  = args.topicModeling
        if args.writeCleanedData:
            self.write_cleaned_data = args.writeCleanedData
        if args.localSaturationCheck:
            self.local_saturation_check = args.localSaturationCheck
        if args.shapefileIntersect:
            self.shapefile_intersect = args.shapefileIntersect
        if args.shapefilePath:
            self.shapefile_path = args.shapefilePath
        if args.ignoreStoplists:
            self.ignore_stoplists = args.ignoreStoplists
        if args.ignorePlaceCorrections:
            self.ignore_place_corrections = args.ignorePlaceCorrections
        if args.statisticsOnly:
            self.statistics_only = args.statisticsOnly
        if args.limitBottomUserCount:
            self.limit_bottom_user_count = int(args.limitBottomUserCount)
        if args.writeGISCompLine:
            self.write_gis_comp_line = args.writeGISCompLine

    def load_filterlists(self):
        """Load filterlists for filtering terms (instring and full match)
        """
        sort_out_always_file = "00_Config/SortOutAlways.txt"
        sort_out_always_instr_file = "00_Config/SortOutAlways_inStr.txt"

        if not os.path.isfile(sort_out_always_file):
            print(f'{sort_out_always_file} not found.')
        #else read logfile
        else:
            if self.ignore_stoplists == False:
                with open(sort_out_always_file, newline='', encoding='utf8') as f: #read each unsorted file and sort lines based on datetime (as string)
                    self.sort_out_always_set = set([line.lower().rstrip('\r\n') for line in f])
                print(f'Loaded {len(self.sort_out_always_set)} stoplist items.')
        if not os.path.isfile(sort_out_always_instr_file):
            print(f'{sort_out_always_instr_file} not found.')
        #else read logfile
        else:
            if self.ignore_stoplists == False:
                with open(sort_out_always_instr_file, newline='', encoding='utf8') as f: #read each unsorted file and sort lines based on datetime (as string)
                    self.sort_out_always_instr_set = set([line.lower().rstrip('\r\n') for line in f])
                print(f'Loaded {len(self.sort_out_always_instr_set)} inStr stoplist items.')

    def load_custom_crs(self, override_crs):
        """Optionally, create custom crs for projecting data base don user input

        Note: not fully implemented
        """
        self.crs_proj = pyproj.Proj(init='epsg:{0}'.format(override_crs))
        print("Custom CRS set: " + str(self.crs_proj.srs))
        self.epsg_code = override_crs
