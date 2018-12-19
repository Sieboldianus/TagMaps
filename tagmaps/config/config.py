# -*- coding: utf-8 -*-

import argparse
import os
import sys

from shapely.geometry import Polygon
from shapely.geometry import shape
from shapely.geometry import Point

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
        self.write_gis_comp_line = True

        # additional auto settings
        self.sort_out_always_set = set()
        self.sort_out_always_instr_set = set()
        self.override_crs = None
        self.crs_proj = ''
        self.epsg_code = ''
        self.sort_out_places_set = set()
        self.sort_out_places = False
        self.correct_places = False
        self.correct_place_latlng_dict = dict()
        self.shp_geom = None

        # initialization
        self.parse_args()
        self.load_filterlists()
        if self.shapefile_intersect:
            self.load_shapefile()

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
        and places, including place lat/lng corrections.
        """
        # locations for files
        sort_out_always_file = "00_Config/SortOutAlways.txt"
        sort_out_always_instr_file = "00_Config/SortOutAlways_inStr.txt"
        sort_out_places_file = "00_Config/SortOutPlaces.txt"
        correct_place_latlng_file = "00_Config/CorrectPlaceLatLng.txt"
        # load lists
        self.sort_out_always_set = self.load_stoplists(sort_out_always_file)
        self.sort_out_always_instr_set = self.load_stoplists(sort_out_always_instr_file)
        self.sort_out_places_set = self.load_place_stoplist(sort_out_places_file)
        self.correct_place_latlng_dict = self.load_place_corrections(correct_place_latlng_file)
        # print results, ignore empty
        try:
            print(f'Loaded {len(self.sort_out_always_set)} stoplist items.')
            print(f'Loaded {len(self.sort_out_always_instr_set)} inStr stoplist items.')
            print(f'Loaded {len(self.sort_out_places_set)} stoplist places.')
            print(f'Loaded {len(self.correct_place_latlng_dict)} place lat/lng corrections.')
        except TypeError:
            pass
                
    def load_stoplists(self, file):
        """Loads stoplist terms from file and stores in set"""
        if self.ignore_stoplists is True:
            return
        if not os.path.isfile(file):
            print(f'{file} not found.')
            return
        store_set = set()
        with open(file, newline='', encoding='utf8') as f:
            store_set = set([line.lower().rstrip('\r\n') for line in f])
        return store_set

    def load_place_stoplist(self, file):
        """Loads stoplist places from file and stores in set"""
        if not os.path.isfile(file) or self.ignore_stoplists is True:
            return
        store_set = set()
        with open(file, newline='', encoding='utf8') as f:
            f.readline()
            # Get placeid
            store_set = set([line.rstrip('\r\n').split(",")[0] for line in f if len(line) > 0])
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
        with open(file, newline='', encoding='utf8') as f:
            f.readline()
            for line in f:
                if len(line) == 0:
                    continue
                linesplit = line.rstrip('\r\n').split(",")
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
            sys.exit(f'No Shapefile-Path specified. Exiting..')
            return
        poly_shape = fiona.open(cfg.shapefile_path)
        first = poly_shape.next()
        print("Loaded Shapefile with " + str(len(first['geometry']['coordinates'][0])) + " Vertices.")
        self.shp_geom = shape(first['geometry'])
        ###For Multi-Polygon:
        ###- not yet implemented
        ###
        #vcount = PShape.next()['geometry']['coordinates'] #needed for count of vertices
        #geom = MultiPolygon([shape(pol['geometry']) for pol in PShape])
        #shp_geom = geom
        #print("Loaded Shapefile with Vertices ", sum([len(poly[0]) for poly in vcount])) # (GeoJSON format)

    def load_custom_crs(self, override_crs):
        """Optionally, create custom crs for projecting data base don user input

        Note: not fully implemented
        """
        self.crs_proj = pyproj.Proj(init='epsg:{0}'.format(override_crs))
        print("Custom CRS set: " + str(self.crs_proj.srs))
        self.epsg_code = override_crs
