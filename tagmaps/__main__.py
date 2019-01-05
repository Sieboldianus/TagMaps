#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tag Maps Clustering

- will read in geotagged (lat/lng) decimal degree point data
- will generate HDBSCAN Cluster Hierarchy
- will output Alpha Shapes/Delauney for cluster cut at specific distance
"""

__author__  = "Alexander Dunkel"
__license__ = "GNU GPLv3"


import csv
import os
import sys
import re
from glob import glob
from _csv import QUOTE_MINIMAL
from collections import defaultdict
from collections import Counter
from collections import namedtuple
import collections
import tkinter as tk
from tkinter.messagebox import showerror
import tkinter.messagebox


#from .utils import *
import datetime
import warnings
from unicodedata import name as unicode_name

#Cluster stuff
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
plt.ion() #enable interactive mode for pyplot (not necessary?!)
import seaborn as sns
import sklearn.datasets as data
import pandas as pd
import hdbscan

from multiprocessing.pool import ThreadPool
pool = ThreadPool(processes=1)
import time
from time import sleep
import copy

#needed for anonymization (Topic Clustering)
import hashlib

#enable for map display
#from mpl_toolkits.basemap import Basemap
#from PIL import Image

import fiona #Fiona needed for reading Shapefile
from fiona.crs import from_epsg
import shapely.geometry as geometry
import pyproj #import Proj, transform
#https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects

from shapely.ops import transform
from decimal import Decimal

#alternative Shapefile module pure Python
#https://github.com/GeospatialPython/pyshp#writing-shapefiles
#import shapefile


##Emojitest
#n = '❤️👨‍⚕️'
#n = '😍,146'
##print(n.encode("utf-8"))
###n = '👨‍⚕️' #medical emoji with zero-width joiner (http://www.unicode.org/emoji/charts/emoji-zwj-sequences.html)
#nlist = Utils.extract_emojis(n)
#with open("emojifile.txt", "w", encoding='utf-8') as emojifile:
#    emojifile.write("Original: " + n + '\n')
#    for xstr in nlist:
#        emojifile.write('Emoji Extract: U+%04x' % ord(xstr) + '\n')
#        emojifile.write(xstr + '\n')
#    for _c in n:
#        emojifile.write(str(unicode_name(_c)) + '\n')
#        emojifile.write('Each Codepoint: U+%04x' % ord(_c) +  '\n')

#initialize global variables for analysis bounds (lat, lng coordinates)
limLatMin = None
limLatMax = None
limLngMin = None
limLngMax = None
abort = False
#definition of global figure for reusing windows
fig1 = None
fig2 = None
fig3 = None
fig4 = None
proceedClusting = False
currentDisplayTag = None
imgRatio = 0
floaterX = 0
floaterY = 0
clusterTreeCuttingDist = 0
topTagsList = []
lastselectionList = []
tnum = 0
tkScalebar = None
cleanedPhotoList = []

from tagmaps.classes.utils import Utils
from tagmaps.classes.load_data import LoadData

def main():
    """Main tag maps function for direct execution of package
    
    - will read from 01_Input/ folder
    - will output clustered data to 02_Output/
    """
    
    # initialize logger and config
    cfg, log = Utils.init_main()
    filelist = LoadData.read_local_files(cfg)

    # READ All JSON in Current Folder and join to list
    #partnum = 0
    guid_list = set() #global list of guids
    count_glob = 0
    partcount = 0
    #filenameprev = ""
    #if (cfg.data_source == "fromFlickr_CSV"):
    #    filelist = glob('01_Input/*.txt')
    #    GMTTimetransform = 0
    #    guid_columnNameID = 5 #guid
    #    Sourcecode = 2
    #    quoting_opt = csv.QUOTE_NONE
    #elif (cfg.data_source == "fromInstagram_PGlbsnEmoji") or (cfg.data_source == "fromLBSN") or (cfg.data_source == "fromLBSN_old"):
    #    filelist = glob('01_Input/*.csv')
    #    guid_columnNameID = 1 #guid
    #    quoting_opt = csv.QUOTE_MINIMAL
    #elif (cfg.data_source == "fromSensorData_InfWuerz"):
    #    filelist = glob('01_Input/*.csv')
    #    GMTTimetransform = 0
    #    guid_columnNameID = 1 #guid
    #    Sourcecode = 11
    #    quoting_opt = csv.QUOTE_NONE
    #else:
    #    sys.exit("Source not supported yet.")

    print('\n')
    log.info("########## STEP 1 of 6: Data Cleanup ##########")
    if (len(filelist) == 0):
        sys.exit(f'No *.json/csv/txt files found.')
    else:
        if cfg.cluster_tags or cfg.cluster_emoji:
            inputtext = input(f'Files to process: {len(filelist)}. \nOptional: Enter a Number for the variety of Tags to process (Default is 1000)\nPress Enter to proceed.. \n')
            if inputtext == "" or not inputtext.isdigit():
                tmax = 1000
            else:
                tmax = int(inputtext)

    skippedCount = 0
    appendToAlreadyExist = False
    count_non_geotagged = 0
    count_outside_shape = 0
    count_tags_global = 0
    count_emojis_global = 0
    count_tags_skipped = 0
    shapeFileExcludelocIDhash = set()
    shapeFileIncludedlocIDhash  = set()
    TotalTagCount_Counter_global = collections.Counter()

    def setLatLngBounds(Lat,Lng):
        global limLatMin, limLatMax, limLngMin, limLngMax
        if limLatMin is None or (Lat < limLatMin and not Lat == 0):
            limLatMin = Lat
        if limLatMax is None or (Lat > limLatMax and not Lat == 0):
            limLatMax = Lat
        if limLngMin is None or (Lng < limLngMin and not Lng == 0):
            limLngMin = Lng
        if limLngMax is None or (Lng > limLngMax and not Lng == 0):
            limLngMax = Lng
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    photoIDHash = set()
    LocationsPerUserID_dict = defaultdict(set)
    UserLocationTagList_dict = defaultdict(set)
    if cfg.topic_modeling:
        UserTopicList_dict  = defaultdict(set)
        UserPhotoIDS_dict  = defaultdict(set)
        UserPhotoFirstThumb_dict = defaultdict(str)
    UserLocationWordList_dict = defaultdict(set)
    UserLocationsFirstPhoto_dict = defaultdict(set)
    if cfg.cluster_emoji:
        overallNumOfEmojis_global = collections.Counter()

    #UserDict_TagCounters = defaultdict(set)
    UserDict_TagCounters_global = defaultdict(set)
    #UserIDsPerLocation_dict = defaultdict(set)
    #PhotoLocDict = defaultdict(set)
    distinctLocations_set = set()
    distinctUserLocations_set = set()
    count_loc = 0
    now = time.time()
    for file_name in filelist:
        #filename = "02_Output/" + os.path.basename(file_name)
        #with open(filename, 'a', encoding='utf8') as file:
        #    file.write("ID_Date,SOURCE,Latitude,Longitude,PhotoID,Owner,UserID,Name,URL,DateTaken,UploadDate,Views,Tags,MTags,Likes,Comments,Shortcode,Type,LocName,LocID" + '\n')
        #    file.write('"2000-01-01 00:00:00","TESTLINE","43.2544706","28.023467","24PHOTOID3534","testowner","812643S9812644","testcaption","https://scontent.cdninstagram.com/t/s640x640/22344798_1757535311005731_6649353052090269696_n.jpg","2000-01-01 00:00:00","2000-01-01 00:00:00","22",";blacksea;romania;ig;seaside;mareaneagra;travel;getfit;trip;travelog;sun;beachy;avenit;mytinyatlas;islandhopping;flashesofdelight;beachvibes;beautiful;waves;barbershop;sea;love;photooftheday;picoftheday;vsco;vscocam;snapshot;instatravel;instamood;ich;io;summer;photography;europa;happy;end;je;lacrusesc;contrejour;chiaroscuro;morninsunshine;treadmill;gainz;workout;sunshine;getstrong;eu;rumunsko;calatoriecupasiune;superduper;selfie;lazyday;","TESTMTAG","50","25","BaE5OZpgfRu","Image","Sunshine Boulevard Sunshine Boulevard Sunshine Bou","821648SS21642"' +'\n')

        photolist = [] # clear photolist for every file
        ##f_count += 1
        ##if f_count > 25:
        ##    break
        #    guid_list.clear() #duplicate detection only for last 500k items
        with open(file_name, newline='', encoding='utf8') as f: # On input, if newline is None, universal newlines mode is enabled. Lines in the input can end in '\n', '\r', or '\r\n', and these are translated into '\n' before being returned to the caller.
            partcount += 1
            if (cfg.data_source == "fromInstagram_LocMedia_CSV" or
            cfg.data_source == "fromLBSN" or cfg.data_source == "fromLBSN_old" or
            cfg.data_source == "fromInstagram_UserMedia_CSV" or
            cfg.data_source == "fromFlickr_CSV" or
            cfg.data_source == "fromInstagram_PGlbsnEmoji" or
            cfg.data_source == "fromSensorData_InfWuerz"):
                photolist = csv.reader(f,
                                       delimiter=cfg.source_map.delimiter,
                                       quotechar=cfg.source_map.quote_char,
                                       quoting=cfg.source_map.quoting)
                                       #QUOTE_NONE is important because media saved from
                                       # php/Flickr does not contain any " check; only ',' are replaced
                next(photolist, None)  # skip headerline
            elif (cfg.data_source == "fromInstagram_HashMedia_JSON"):
                photolist = photolist + json.loads(f.read())
            #PhotosPerDayLists = defaultdict(list)
            #keyCreatedHash = set()
            for item in photolist:
                #duplicate check based on GUID
                if item[cfg.source_map.post_guid_col] in photoIDHash:
                    skippedCount += 1
                    continue
                else:
                    photoIDHash.add(item[cfg.source_map.post_guid_col])
                if (cfg.data_source == "fromInstagram_LocMedia_CSV"):
                    if len(item) < 15:
                        #skip
                        skippedCount += 1
                        continue
                    else:
                        photo_source = Sourcecode #LocamediaCode
                        photo_guid = item[0] #guid
                        photo_userid = item[2]
                        #photo_owner = item[7] ##!!!
                        photo_shortcode = item[5]
                        photo_uploadDate = item[3] # format datetime as string
                        photo_idDate = photo_uploadDate #use upload date as sorting ID
                        photo_caption = item[7]
                        photo_likes = item[12]
                        photo_tags = ";" + item[8] + ";"
                        photo_thumbnail = item[6]
                        photo_comments = item[13]
                        photo_mediatype = item[4]
                        photo_locID = item[14]
                        photo_locName = item[1]
                        #assign lat/lng coordinates from dict
                        if (photo_locID in loc_dict):
                            photo_latitude = loc_dict[photo_locID][0]
                            photo_longitude = loc_dict[photo_locID][1]
                            #setLatLngBounds(photo_latitude,photo_longitude)
                            if cfg.shapefile_intersect:
                                #skip all outside shapefile
                                if photo_locID in shapeFileExcludelocIDhash:
                                    count_outside_shape += 1
                                    continue
                                if not photo_locID in shapeFileIncludedlocIDhash:
                                    LngLatPoint = Point(photo_longitude, photo_latitude)
                                    if not LngLatPoint.within(shp_geom):
                                        count_outside_shape += 1
                                        shapeFileExcludelocIDhash.add(photo_locID)
                                        continue
                                    else:
                                        shapeFileIncludedlocIDhash.add(photo_locID)
                        else:
                            if excludeWhereMissingGeocode:
                                skippedCount += 1
                                continue #skip non-geotagged medias
                            else:
                                photo_latitude = ""
                                photo_longitude = ""
                        #assign usernames from dict
                        if photo_userid in user_dict:
                            photo_owner = user_dict[photo_userid]
                        elif photo_userid in netlytics_usernameid_dict:
                            photo_owner = netlytics_usernameid_dict[photo_userid]
                        else:
                            photo_owner = ""
                        #empty for instagram:
                        photo_mTags = ""
                        photo_dateTaken = ""
                        photo_views = ""
                elif cfg.data_source == "fromInstagram_UserMedia_CSV":
                    if len(item) < 15:
                        #skip
                        skippedCount += 1
                        continue
                    else:
                        photo_source = Sourcecode #LocMediaCode
                        photo_guid = item[0].split("_")[0] #guid
                        photo_userid = item[0].split("_")[1] #userid
                        photo_owner = item[1] ##!!!
                        photo_shortcode = item[6]
                        photo_uploadDate = item[4] # format datetime as string
                        photo_idDate = photo_uploadDate #use upload date as sorting ID
                        photo_caption = item[8]
                        photo_likes = item[13]
                        photo_tags = ";" + item[9] + ";"
                        photo_thumbnail = item[7]
                        photo_comments = item[14]
                        photo_mediatype = item[5]
                        photo_locID = item[2]
                        if photo_locID == "":
                            count_non_geotagged += 1
                            continue #skip non-geotagged medias
                        photo_locName = item[3]
                        #assign lat/lng coordinates from dict
                        if (photo_locID in loc_dict):
                            photo_latitude = loc_dict[photo_locID][0]
                            photo_longitude = loc_dict[photo_locID][1]
                            if cfg.shapefile_intersect:
                                #skip all outside shapefile
                                if photo_locID in shapeFileExcludelocIDhash:
                                    count_outside_shape += 1
                                    continue
                                if not photo_locID in shapeFileIncludedlocIDhash:
                                    LngLatPoint = Point(photo_longitude, photo_latitude)
                                    if not LngLatPoint.within(shp_geom):
                                        count_outside_shape += 1
                                        shapeFileExcludelocIDhash.add(photo_locID)
                                        continue
                                    else:
                                        shapeFileIncludedlocIDhash.add(photo_locID)
                        else:
                            if excludeWhereMissingGeocode:
                                skippedCount += 1
                                continue #skip non-geotagged medias
                            else:
                                photo_latitude = ""
                                photo_longitude = ""
                        #empty for Instagram:
                        photo_mTags = ""
                        photo_dateTaken = ""
                        photo_views = ""
                elif cfg.data_source == "fromFlickr_CSV":
                    if len(item) < 12:
                        #skip
                        skippedCount += 1
                        continue
                    else:
                        photo_source = Sourcecode #LocMediaCode
                        photo_guid = item[5] #photoID
                        photo_userid = item[7] #userid
                        photo_owner = item[6] ##!!!
                        photo_shortcode = ""
                        photo_uploadDate = datetime.datetime.strptime(item[9],'%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')  # format datetime as string
                        photo_dateTaken = datetime.datetime.strptime(item[8]  ,'%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        photo_idDate = photo_dateTaken #use date taken date as sorting ID
                        photo_caption = item[3]
                        photo_likes = ""
                        #Filter tags based on two stoplists
                        if cfg.cluster_tags or cfg.topic_modeling:
                            photo_tags = set(filter(None, item[11].lower().split(";"))) #filter empty strings from photo_tags list and convert to set (hash) with unique values
                            #Filter tags based on two stoplists
                            photo_tags, count_tags, count_skipped = Utils.filterTags(photo_tags,cfg.sort_out_always_set,cfg.sort_out_always_instr_set)
                            count_tags_global += count_tags
                            count_tags_skipped += count_skipped
                        else:
                            photo_tags = set()
                        #if not "water" in photo_tags:
                        #    continue
                        photo_thumbnail = item[4]
                        photo_comments = ""
                        photo_mediatype = ""
                        photo_locName = ""
                        if is_number(item[1]):
                            photo_latitude = Decimal(item[1])
                        else:
                            skippedCount += 1
                            continue
                        if is_number(item[2]):
                            photo_longitude = Decimal(item[2])
                        else:
                            skippedCount += 1
                            continue
                        setLatLngBounds(photo_latitude,photo_longitude)
                        photo_locID = str(photo_latitude) + ':' + str(photo_longitude) #create loc_id from lat/lng
                        photo_mTags = "" #not used currently but available
                        photo_views = item[10]
                elif (cfg.data_source == "fromInstagram_HashMedia_JSON"):
                    photo_source = Sourcecode #HashMediaCode
                    if item.get('owner'):
                        photo_userid = item["owner"]["id"]
                    else:
                        # skip problematic entries
                        skippedCount += 1
                        continue
                    if item.get('edge_liked_by'):
                        photo_likes = item["edge_liked_by"]["count"]
                    else:
                        photo_likes = ""
                    if item.get('edge_media_to_caption') and not len(item.get("edge_media_to_caption", {}).get("edges")) == 0:
                        photo_caption = item["edge_media_to_caption"]["edges"][0]["node"]["text"].replace('\n', ' ').replace('\r', '')
                    else:
                        photo_caption = ""
                    if item.get('edge_media_to_comment'):
                        photo_comments = item["edge_media_to_comment"]["count"]
                    else:
                        photo_comments = ""
                    if item.get('id'):
                        photo_guid = item["id"]
                    else:
                        # skip problematic entries
                        skippedCount += 1
                        continue
                    if item.get('is_video'):
                        photo_mediatype = "video"
                    else:
                        photo_mediatype = "image"
                    if item.get('location'):
                        photo_locID = item["location"]["id"]
                        photo_locName = item["location"]["name"]
                    else:
                        # skip non geotagged
                        count_non_geotagged += 1
                        continue
                    if item.get('shortcode'):
                        photo_shortcode = item["shortcode"]
                    else:
                        photo_shortcode = ""
                    if item.get('tags'):
                        photo_tags =';'.join(item["tags"]).replace('\n', ' ').replace('\r', '')
                        photo_tags = ";%s;" % (photo_tags.replace(",", ";"))
                    else:
                        photo_tags = ""
                    if item.get('taken_at_timestamp'):
                        pdate = datetime.datetime.fromtimestamp(int(item["taken_at_timestamp"])) + timedelta(hours = GMTTimetransform) #GMT conversion
                        photo_uploadDate = pdate.strftime('%Y-%m-%d %H:%M:%S') # format datetime as string
                        photo_idDate = photo_uploadDate
                    else:
                        # skip problematic entries
                        skippedCount += 1
                        continue
                    if item.get('thumbnail_src'):
                        photo_thumbnail = item["thumbnail_src"]
                    else:
                        photo_thumbnail = ""

                    #assign lat/lng coordinates from dict
                    if (photo_locID in loc_dict):
                        photo_latitude = loc_dict[photo_locID][0]
                        photo_longitude = loc_dict[photo_locID][1]
                        if cfg.shapefile_intersect:
                            #skip all outside shapefile
                            if photo_locID in shapeFileExcludelocIDhash:
                                count_outside_shape += 1
                                continue
                            if not photo_locID in shapeFileIncludedlocIDhash:
                                LngLatPoint = Point(photo_longitude, photo_latitude)
                                if not LngLatPoint.within(shp_geom):
                                    count_outside_shape += 1
                                    shapeFileExcludelocIDhash.add(photo_locID)
                                    continue
                                else:
                                    shapeFileIncludedlocIDhash.add(photo_locID)
                    else:
                        if excludeWhereMissingGeocode:
                            #count_non_geotagged += 1
                            skippedCount += 1
                            continue #skip non-geotagged medias
                        else:
                            photo_latitude = ""
                            photo_longitude = ""

                    #assign usernames from dict
                    if photo_userid in user_dict:
                        photo_owner = user_dict[photo_userid]
                    elif photo_userid in netlytics_usernameid_dict:
                        photo_owner = netlytics_usernameid_dict[photo_userid]
                    else:
                        photo_owner = ""
                    #empty for instagram:
                    photo_mTags = ""
                    photo_dateTaken = ""
                    photo_views = ""
                elif cfg.data_source == "fromInstagram_PGlbsnEmoji":
                    if len(item) < 15:
                        #skip
                        skippedCount += 1
                        continue
                    else:
                        photo_source = item[0]
                        photo_guid = item[1] #guid
                        photo_userid = item[7] #guid
                        photo_owner = ""#item[1] ##!!!
                        photo_shortcode = item[18]
                        photo_uploadDate = item[8] #guid
                        photo_idDate = photo_uploadDate #use upload date as sorting ID
                        photo_caption = item[9]
                        photo_likes = item[13]
                        #photo_tags = ";" + item[11] + ";"
                        tags_filtered = Utils.extract_emojis(photo_caption)
                        if not len(tags_filtered) == 0:
                            count_tags_global += len(tags_filtered)
                            photo_tags = set(tags_filtered)
                        else:
                            photo_tags = set()
                        #photo_emojis = extract_emojis(photo_caption)
                        photo_thumbnail = item[17]
                        photo_comments = item[14]
                        photo_mediatype = item[19]

                        photo_locName = item[4] #guid
                        if item[2] == "" or item[3] == "":
                            count_non_geotagged += 1
                            continue #skip non-geotagged medias
                        else:
                            photo_latitude = Decimal(item[2]) #guid
                            photo_longitude = Decimal(item[3]) #guid
                            setLatLngBounds(photo_latitude,photo_longitude)
                        photo_locID = str(photo_latitude) + ':' + str(photo_longitude) #create loc_id from lat/lng
                        #empty for Instagram:
                        photo_mTags = ""
                        photo_dateTaken = ""
                        photo_views = 0
                elif cfg.data_source == "fromLBSN":
                    if len(item) < 15:
                        #skip
                        skippedCount += 1
                        continue
                    else:
                        photo_source = item[0] #LocMediaCode
                        photo_guid = item[1] #guid
                        photo_userid = item[4] #guid
                        photo_owner = ""#item[1] ##!!!
                        photo_shortcode = None#item[18]
                        photo_uploadDate = item[6] #guid
                        photo_idDate = None#photo_uploadDate #use upload date as sorting ID
                        #Process Spatial Query first (if skipping necessary)
                        if cfg.sort_out_places:
                            if not item[19] == "":
                                if item[19] in cfg.sort_out_places_set:
                                    skippedCount += 1
                                    continue
                        if item[2] == "" or item[3] == "":
                            count_non_geotagged += 1
                            continue #skip non-geotagged medias
                        else:
                            if cfg.correct_places and not item[19] and item[19] in cfg.correct_place_latlng_dict:
                                photo_latitude = Decimal(cfg.correct_place_latlng_dict[item[19]][0]) #correct lat/lng
                                photo_longitude = Decimal(cfg.correct_place_latlng_dict[item[19]][1]) #correct lat/lng
                            else:
                                photo_latitude = Decimal(item[2]) #guid
                                photo_longitude = Decimal(item[3]) #guid
                            setLatLngBounds(photo_latitude,photo_longitude)
                        photo_locID = str(photo_latitude) + ':' + str(photo_longitude) #create loc_id from lat/lng
                        #assign lat/lng coordinates from dict
                        if cfg.shapefile_intersect:
                            #skip all outside shapefile
                            if photo_locID in shapeFileExcludelocIDhash:
                                skippedCount += 1
                                continue
                            if not photo_locID in shapeFileIncludedlocIDhash:
                                LngLatPoint = Point(photo_longitude, photo_latitude)
                                if not LngLatPoint.within(shp_geom):
                                    skippedCount += 1
                                    shapeFileExcludelocIDhash.add(photo_locID)
                                    continue
                                else:
                                    shapeFileIncludedlocIDhash.add(photo_locID)
                        if cfg.cluster_tags or cfg.cluster_emoji or cfg.topic_modeling:
                            photo_caption = item[14]
                        else:
                            photo_caption = ""
                        photo_likes = 0
                        if not item[9] == "":
                            try:
                                photo_likes = int(item[9])
                            except TypeError:
                                pass
                        photo_tags = set()
                        if cfg.cluster_tags or cfg.topic_modeling:
                            photo_tags = set(filter(None, item[11].lower().split(";"))) #[1:-1] removes curly brackets, second [1:-1] removes quotes
                            #Filter tags based on two stoplists
                            if cfg.ignore_stoplists:
                                count_tags = len(photo_tags)
                                count_skipped = 0
                            else:
                                photo_tags,count_tags,count_skipped = Utils.filterTags(photo_tags,cfg.sort_out_always_set,cfg.sort_out_always_instr_set)
                            count_tags_global += count_tags
                            count_tags_skipped += count_skipped
                        if cfg.cluster_emoji:
                            emojis_filtered = set(Utils.extract_emojis(photo_caption))
                            if not len(emojis_filtered) == 0:
                                count_emojis_global += len(emojis_filtered)
                                overallNumOfEmojis_global.update(emojis_filtered)
                                photo_tags = set.union(emojis_filtered)
                        #photo_tags = ";" + item[11] + ";"
                        photo_thumbnail = None#item[17]
                        photo_comments = None#item[14]
                        photo_mediatype = None#item[19]
                        photo_locName = item[4] #guid
                        #empty for Instagram:
                        photo_mTags = ""
                        photo_dateTaken = ""
                        photo_views = 0
                        if not item[8] == "":
                            try:
                                photo_views = int(item[8])
                            except TypeError:
                                pass
                elif cfg.data_source == "fromLBSN_old":
                    if len(item) < 15:
                        #skip
                        skippedCount += 1
                        continue
                    else:
                        photo_source = item[0] #LocMediaCode
                        photo_guid = item[1] #guid
                        photo_userid = item[7] #guid
                        photo_owner = ""#item[1] ##!!!
                        photo_shortcode = None#item[18]
                        photo_uploadDate = item[8] #guid
                        photo_idDate = None#photo_uploadDate #use upload date as sorting ID
                        #Process Spatial Query first (if skipping necessary)
                        if cfg.sort_out_places:
                            if not item[4] == "":
                                if item[4] in cfg.sort_out_places_set:
                                    skippedCount += 1
                                    continue
                        if item[2] == "" or item[3] == "":
                            count_non_geotagged += 1
                            continue #skip non-geotagged medias
                        else:
                            if cfg.correct_places and not item[4] and item[4] in cfg.correct_place_latlng_dict:
                                photo_latitude = Decimal(cfg.correct_place_latlng_dict[item[4]][0]) #correct lat/lng
                                photo_longitude = Decimal(cfg.correct_place_latlng_dict[item[4]][1]) #correct lat/lng
                            else:
                                photo_latitude = Decimal(item[2]) #guid
                                photo_longitude = Decimal(item[3]) #guid
                            setLatLngBounds(photo_latitude,photo_longitude)
                        photo_locID = str(photo_latitude) + ':' + str(photo_longitude) #create loc_id from lat/lng
                        #assign lat/lng coordinates from dict
                        if cfg.shapefile_intersect:
                            #skip all outside shapefile
                            if photo_locID in shapeFileExcludelocIDhash:
                                skippedCount += 1
                                continue
                            if not photo_locID in shapeFileIncludedlocIDhash:
                                LngLatPoint = Point(photo_longitude, photo_latitude)
                                if not LngLatPoint.within(shp_geom):
                                    skippedCount += 1
                                    shapeFileExcludelocIDhash.add(photo_locID)
                                    continue
                                else:
                                    shapeFileIncludedlocIDhash.add(photo_locID)
                        if cfg.cluster_tags or cfg.cluster_emoji or cfg.topic_modeling:
                            photo_caption = item[9]
                        else:
                            photo_caption = ""
                        photo_likes = 0
                        if not item[9] == "":
                            try:
                                photo_likes = int(item[13])
                            except TypeError:
                                pass
                            except ValueError:
                                pass
                        photo_tags = set()
                        if cfg.cluster_tags or cfg.topic_modeling:
                            photo_tags = set(filter(None, item[11].strip('"').lstrip('{').rstrip('}').lower().split(","))) #[1:-1] removes curly brackets, second [1:-1] removes quotes
                            #Filter tags based on two stoplists
                            if cfg.ignore_stoplists:
                                count_tags = len(photo_tags)
                                count_skipped = 0
                            else:
                                photo_tags,count_tags,count_skipped = Utils.filterTags(photo_tags,cfg.sort_out_always_set,cfg.sort_out_always_instr_set)
                            count_tags_global += count_tags
                            count_tags_skipped += count_skipped
                        if cfg.cluster_emoji:
                            emojis_filtered = set(Utils.extract_emojis(photo_caption))
                            if not len(emojis_filtered) == 0:
                                count_emojis_global += len(emojis_filtered)
                                overallNumOfEmojis_global.update(emojis_filtered)
                                photo_tags = set.union(emojis_filtered)
                        #photo_tags = ";" + item[11] + ";"
                        photo_thumbnail = None#item[17]
                        photo_comments = None#item[14]
                        photo_mediatype = None#item[19]
                        photo_locName = item[4] #guid
                        #empty for Instagram:
                        photo_mTags = ""
                        photo_dateTaken = ""
                        photo_views = 0
                        #if not item[8] == "":
                        #    try:
                        #        photo_views = int(item[8])
                        #    except TypeError:
                        #        pass
                elif cfg.data_source == "fromSensorData_InfWuerz":
                    if len(item) < 5:
                        #skip
                        skippedCount += 1
                        continue
                    else:
                        photo_source = Sourcecode #LocMediaCode
                        photo_guid = item[1] #guid
                        photo_userid = item[4] #meta_device_id
                        photo_owner = ""#item[1] ##!!!
                        photo_shortcode = ""
                        photo_uploadDate = item[3] #meta_timestamp_received
                        photo_idDate = item[2] #meta_timestamp_recorded
                        photo_caption = item[8]
                        if not len(photo_caption) == 0:
                            removeSpecialChars = photo_caption.translate ({ord(c): " " for c in "?.!/;:,[]()'-&#"})
                            wordlist = [word for word in removeSpecialChars.lower().split(' ') if not word == "" and len(word) > 1]
                            photo_tags = set(wordlist)
                        else:
                            photo_tags = set()
                        photo_tags_filtered = set()
                        for tag in photo_tags:
                            count_tags_global += 1
                            #exclude numbers and those tags that are in cfg.sort_out_always_set
                            if tag.isdigit() or tag in cfg.sort_out_always_set:
                                count_tags_skipped += 1
                                continue
                            for inStr in cfg.sort_out_always_instr_set:
                                if inStr in tag:
                                    count_tags_skipped += 1
                                    break
                            else:
                                photo_tags_filtered.add(tag)
                        photo_tags = photo_tags_filtered
                        if item[6] == "" or item[7] == "":
                            count_non_geotagged += 1
                            continue #skip non-geotagged medias
                        else:
                            photo_latitude = Decimal(item[7]) #guid
                            photo_longitude = Decimal(item[6]) #guid
                            setLatLngBounds(photo_latitude,photo_longitude)
                        photo_locID = str(photo_latitude) + ':' + str(photo_longitude) #create loc_id from lat/lng
                        #empty for SensorWuerz:
                        photo_likes = ""
                        photo_thumbnail = ""
                        photo_comments = ""
                        photo_mediatype = ""
                        photo_locName = ""
                        photo_mTags = ""
                        photo_dateTaken = ""
                        photo_views = 0
                #this code will union all tags of a single user for each location
                #further information is derived from the first image for each user-location
                photo_locIDUserID =  photo_locID + '::' + str(photo_userid) #create userid_loc_id
                distinctLocations_set.add(photo_locID)
                #print(f'Added: {photo_locID} to distinctLocations_set (len: {len(distinctLocations_set)})')
                distinctUserLocations_set.add(photo_locIDUserID)
                #print(f'Added: {photo_locIDUserID} to distinctUserLocations_set (len: {len(distinctUserLocations_set)})')
                if not photo_userid in LocationsPerUserID_dict or not photo_locID in LocationsPerUserID_dict[photo_userid]:
                    LocationsPerUserID_dict[photo_userid] |= {photo_locID} # Bit wise or and assignment in one step. -> assign locID to UserDict list if not already contained
                    count_loc += 1
                    UserLocationsFirstPhoto_dict[photo_locIDUserID] = (photo_source,
                                                                       photo_guid,
                                                                       photo_owner,
                                                                       photo_userid,
                                                                       photo_caption,
                                                                       photo_thumbnail,
                                                                       photo_dateTaken,
                                                                       photo_uploadDate,
                                                                       photo_views,
                                                                       photo_tags,
                                                                       photo_mTags,
                                                                       photo_likes,
                                                                       photo_comments,
                                                                       photo_shortcode,
                                                                       photo_mediatype,
                                                                       photo_locName,
                                                                       photo_locID)
                UserLocationTagList_dict[photo_locIDUserID] |= photo_tags #union tags per userid/unique location
                removeSpecialChars = photo_caption.translate ({ord(c): " " for c in "?.!/;:,[]()'-&#"})
                if cfg.tokenize_japanese:
                    wordlist = [word for word in jTokenize(input_sentence) for input_sentence in removeSpecialChars.split(' ')]
                else:
                    wordlist = [word for word in removeSpecialChars.lower().split(' ') if len(word) > 2]  #first replace specia characters in caption, then split by space-character
                UserLocationWordList_dict[photo_locIDUserID] |= set(wordlist) #union words per userid/unique location
                count_glob += 1

                ##Calculate toplists
                if photo_tags:
                    UserDict_TagCounters_global[photo_userid].update(photo_tags) #add tagcount of this media to overall tagcount or this user, initialize counter for user if not already done
                    TotalTagCount_Counter_global.update(photo_tags)
                msg = f'Cleaned output to {len(distinctLocations_set):02d} distinct locations from {count_glob:02d} photos (File {partcount} of {len(filelist)}) - Skipped Media: {skippedCount} - Skipped Tags: {count_tags_skipped} of {count_tags_global}'
                print(msg, end='\r')
            #else:
            #    #Append last message directly to log file
            #    log.propagate = False
            #    log.info(msg)
            #    log.propagate = True
    total_distinct_locations = len(distinctLocations_set)
    log.info(f'\nTotal users: {len(LocationsPerUserID_dict)} (UC)')
    log.info(f'Total photos: {count_glob:02d} (PC)')
    log.info(f'Total tags (PTC): {count_tags_global}')
    log.info(f'Total emojis (PEC): {count_emojis_global}')
    log.info(f'Total user photo locations (UPL): {len(distinctUserLocations_set)}')

    #boundary:
    log.info(f'Bounds are: Min {float(limLngMin)} {float(limLatMin)} Max {float(limLngMax)} {float(limLatMax)}')

    #create structure for tuple with naming for easy referencing
    cleanedPhotoLocation_tuple = namedtuple('cleanedPhotoLocation_tuple', 'source lat lng photo_guid photo_owner userid photo_caption photo_dateTaken photo_uploadDate photo_views photo_tags photo_thumbnail photo_mTags photo_likes photo_comments photo_shortcode photo_mediatype photo_locName photo_locID')
    cleanedPhotoDict = defaultdict(cleanedPhotoLocation_tuple)
    with open("02_Output/Output_cleaned.txt", 'w', encoding='utf8') as csvfile:
        csvfile.write("SOURCE,Latitude,Longitude,PhotoID,Owner,UserID,Name,DateTaken,UploadDate,Views,Tags,URL,MTags,Likes,Comments,Shortcode,Type,LocName,LocID," + '\n')
        datawriter = csv.writer(csvfile, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for user_key, locationhash in LocationsPerUserID_dict.items():
            for location in locationhash:
                locIDUserID = str(location) + '::' + str(user_key)
                photo_latlng = location.split(':')
                photo = UserLocationsFirstPhoto_dict.get(locIDUserID,(" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "))
                #create tuple with cleaned photo data
                cleanedPhotoLocation = cleanedPhotoLocation_tuple(photo[0],#Source = 0
                              float(photo_latlng[0]), #Lat = 1
                              float(photo_latlng[1]), #Lng = 2
                              photo[1],#photo_guid = 3
                              photo[2],#photo_owner = 4
                              user_key, #userid = 5
                              UserLocationWordList_dict.get(locIDUserID,("",)),#photo_caption = 6
                              photo[6],#photo_dateTaken = 7
                              photo[7],#photo_uploadDate = 8
                              photo[8],#photo_views = 9
                              UserLocationTagList_dict.get(locIDUserID,("",)),#photo_tags = 10
                              photo[5],#photo_thumbnail = 11
                              photo[10],#photo_mTags = 12
                              photo[11],#photo_likes = 13
                              photo[12],#photo_comments = 14
                              photo[13],#photo_shortcode = 15
                              photo[14],#photo_mediatype = 16
                              photo[15],#photo_locName = 17
                              photo[16]#photo_locID = 18
                              )
                if cfg.write_cleaned_data:
                    ###optional Write Cleaned Data to CSV/TXT
                    datawriter.writerow([cleanedPhotoLocation.source,#Source = 0
                                  cleanedPhotoLocation.lat, #Lat = 1
                                  cleanedPhotoLocation.lng, #Lng = 2
                                  cleanedPhotoLocation.photo_guid,#photo_guid = 3
                                  cleanedPhotoLocation.photo_owner,#photo_owner = 4
                                  cleanedPhotoLocation.userid, #userid = 5
                                  ";".join(cleanedPhotoLocation.photo_caption),#photo_caption = 6
                                  cleanedPhotoLocation.photo_dateTaken,#photo_dateTaken = 7
                                  cleanedPhotoLocation.photo_uploadDate,#photo_uploadDate = 8
                                  cleanedPhotoLocation.photo_views,#photo_views = 9
                                  ";".join(cleanedPhotoLocation.photo_tags),#photo_tags = 10
                                  cleanedPhotoLocation.photo_thumbnail,#photo_thumbnail = 11
                                  cleanedPhotoLocation.photo_mTags,#photo_mTags = 12
                                  cleanedPhotoLocation.photo_likes,#photo_likes = 13
                                  cleanedPhotoLocation.photo_comments,#photo_comments = 14
                                  cleanedPhotoLocation.photo_shortcode,#photo_shortcode = 15
                                  cleanedPhotoLocation.photo_mediatype,#photo_mediatype = 16
                                  cleanedPhotoLocation.photo_locName,#photo_locName = 17
                                  cleanedPhotoLocation.photo_locID]#photo_locID = 18
                                  )
                ##optional Write Cleaned Search Terms to CSV for Topic Modeling
                #topics = cleanedPhotoLocation.photo_caption.union(cleanedPhotoLocation.photo_tags)
                if cfg.topic_modeling:
                    if not len(cleanedPhotoLocation.photo_tags) == 0:
                        UserTopicList_dict[user_key] |= cleanedPhotoLocation.photo_tags
                        UserTopicList_dict[user_key] |= cleanedPhotoLocation.photo_caption #also use descriptions for Topic Modeling
                        UserPhotoIDS_dict[user_key] |= {cleanedPhotoLocation.photo_guid} # Bit wise or and assignment in one step. -> assign PhotoGuid to UserDict list if not already contained
                        #UserPhotoFirstThumb_dict[user_key] = photo[5]
                cleanedPhotoDict[cleanedPhotoLocation.photo_guid] = cleanedPhotoLocation
    if cfg.topic_modeling:
        #export list of cleaned topics on a per user basis for LDA/TSNE etc.
        with open("02_Output/Output_usertopics_anonymized.csv", 'w', encoding='utf8') as csvfile:
            csvfile.write("TOPICS,PhotoIDs,UserID" + '\n')
            datawriter = csv.writer(csvfile, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            for user_key, topics in UserTopicList_dict.items():
                datawriter.writerow([" ".join(topics),"{" + ",".join([hashlib.sha3_256(photoid.encode("utf8")).hexdigest() for photoid in UserPhotoIDS_dict.get(user_key,None)]) + "}",hashlib.sha3_256(user_key.encode("utf8")).hexdigest()])
        with open("02_Output/Output_usertopics.csv", 'w', encoding='utf8') as csvfile:
            csvfile.write("TOPICS,PhotoIDs,UserID" + '\n')
            datawriter = csv.writer(csvfile, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            for user_key, topics in UserTopicList_dict.items():
                datawriter.writerow([" ".join(topics),"{" + ",".join(UserPhotoIDS_dict.get(user_key,None)) + "}",str(user_key)])

    if (cfg.cluster_tags or cfg.cluster_emoji):
        log.info("########## STEP 2 of 6: Tag Ranking ##########")
        overallNumOfUsersPerTag_global = collections.Counter()
        for user_key, taghash in UserDict_TagCounters_global.items():
            #taghash contains unique values (= strings) for each user, thus summing up these taghashes counts each user only once per tag
            overallNumOfUsersPerTag_global.update(taghash)

        global topTagsList
        log.info(f"Total unique tags: {len(overallNumOfUsersPerTag_global)}")

        topTagsList = overallNumOfUsersPerTag_global.most_common(tmax)
        #remove all tags that are used by less than x {cfg.limit_bottom_user_count} photographers
        if cfg.remove_long_tail is True:
            indexMin = next((i for i, (t1, t2) in enumerate(topTagsList) if t2 < cfg.limit_bottom_user_count), None)
            if indexMin:
                lenBefore = len(topTagsList)
                del topTagsList[indexMin:]
                lenAfter = len(topTagsList)
                tmax = lenAfter
                if not lenBefore == lenAfter:
                    log.info(f'Long tail removal: Filtered {lenBefore - lenAfter} Tags that were used by less than {cfg.limit_bottom_user_count} users.')

        # Calculate Total Tags for selected topTagsList (Long Tail Stat)
        totalTagCount = 0
        for tag in topTagsList:
            count = TotalTagCount_Counter_global.get(tag[0])
            if count:
                totalTagCount += count
        #print(TotalTagCount_Counter_global.most_common(3))
        log.info(f'Total tags count for selected Tags List (Top {tmax}): {totalTagCount}.')

        #optional write topemojis to file
        globalEmojiSet = {}
        if cfg.cluster_emoji:
            topEmojisList = overallNumOfEmojis_global.most_common()
            globalEmojiSet =  {tuple[0] for tuple in topEmojisList}
            if (not len(globalEmojiSet) == 0):
                topemojis = ''.join("%s,%i" % v + '\n' for v in topEmojisList)
                with open("02_Output/Output_topemojis.txt", 'w', encoding="utf8") as file: #overwrite
                    file.write("emoji,usercount\n")
                    file.write(topemojis)

        if cfg.cluster_tags:
            #optional write toptags to file
            toptags = ''.join("%s,%i" % v + '\n' for v in topTagsList if not v[0] in globalEmojiSet)
            if (not len(topTagsList) == 0):
                with open("02_Output/Output_toptags.txt", 'w', encoding="utf8") as file: #overwrite
                    file.write("tag,usercount\n")
                    file.write(toptags)

        if cfg.statistics_only == False:
            singleMostUsedtag = topTagsList[0]
            now = time.time()
            log.info("########## STEP 3 of 6: Tag Location Clustering ##########")
            #prepare some variables
            label_size = 10
            #plt.rcParams['xtick.labelsize'] = label_size
            #plt.rcParams['ytick.labelsize'] = label_size
            plot_kwds = {'alpha' : 0.5, 's' : 10, 'linewidths':0}
            sys.stdout.flush()

            distY = 0
            distX = 0
            global limYMin, limYMax, limXMin, limXMax, imgRatio, floaterX, floaterY

            #Optional: set global plotting bounds
            #plt.gca().set_xlim([limXMin, limXMax])
            #plt.gca().set_ylim([limYMin, limYMax])
            global cleanedPhotoList
            cleanedPhotoList = list(cleanedPhotoDict.values())
            df = pd.DataFrame(cleanedPhotoList)
            points = df.as_matrix(['lng','lat'])
            limYMin,limYMax,limXMin,limXMax = Utils.getRectangleBounds(points)
            bound_points_shapely = geometry.MultiPoint([(limXMin, limYMin), (limXMax, limYMax)])
            distYLat = limYMax - limYMin
            distXLng = limXMax - limXMin
            #distYLat = Utils.haversine(limXMin,limYMax,limXMin,limYMin)
            #distXLng = Utils.haversine(limXMax,limYMin,limXMin,limYMin)
            #imgRatio = distXLng/(distYLat*2)

            imgRatio = distXLng/(distYLat*2)
            distY = Utils.haversine(limXMin, limYMin, limXMin, limYMax)
            distX = Utils.haversine(limXMin, limYMin, limXMax, limYMin)
            global clusterTreeCuttingDist
            clusterTreeCuttingDist = (min(distX,distY)/100)*7 #4% of research area width/height (max) = default value #223.245922725 #= 0.000035 radians dist

            ######### TKinter Preparation ###########
            class App(tk.Tk):
                def __init__(self):
                    tk.Tk.__init__(self)
                    self.overrideredirect(True) #this is needed to make the root disappear
                    self.geometry('%dx%d+%d+%d' % (0, 0, 0, 0))
                    #create separate floating window
                    self.floater = FloatingWindow(self)

            class FloatingWindow(tk.Toplevel):
                #global app
                def __init__(self, *args, **kwargs):
                    tk.Toplevel.__init__(self, *args, **kwargs)
                    self.overrideredirect(True)
                    self.configure(background='gray7')
                    #self.label = tk.Label(self, text="Click on the grip to move")
                    self.grip = tk.Label(self, bitmap="gray25")
                    self.grip.pack(side="left", fill="y")
                    #self.label.pack(side="right", fill="both", expand=True)
                    self.grip.bind("<ButtonPress-1>", self.StartMove)
                    self.grip.bind("<ButtonRelease-1>", self.StopMove)
                    self.grip.bind("<B1-Motion>", self.OnMotion)
                    #center Floating Window
                    w = self.winfo_reqwidth()
                    h = self.winfo_reqheight()
                    ws = self.winfo_screenwidth()
                    hs = self.winfo_screenheight()
                    x = (ws/2) - (w/2)
                    y = (hs/2) - (h/2)
                    self.geometry('+%d+%d' % (x, y))
                def StartMove(self, event):
                    self.x = event.x
                    self.y = event.y

                def StopMove(self, event):
                    self.x = None
                    self.y = None

                def OnMotion(self, event):
                    deltax = event.x - self.x
                    deltay = event.y - self.y
                    x = self.winfo_x() + deltax
                    y = self.winfo_y() + deltay
                    self.geometry("+%s+%s" % (x, y))

            #Initialize TKinter Interface
            app = App()
            #necessary override for error reporting during tkinter mode:
            import traceback
            def report_callback_exception(self, exc, val, tb):
                showerror("Error", message=str(val))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("*** print_tb:")
                traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
                print("*** print_exception:")
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)
                print("*** print_exc:")
                traceback.print_exc()
                print("*** format_exc, first and last line:")
                formatted_lines = traceback.format_exc().splitlines()
                print(formatted_lines[0])
                print(formatted_lines[-1])
                print("*** format_exception:")
                print(repr(traceback.format_exception(exc_type, exc_value,
                                                      exc_traceback)))
                print("*** extract_tb:")
                print(repr(traceback.extract_tb(exc_traceback)))
                print("*** format_tb:")
                print(repr(traceback.format_tb(exc_traceback)))
                print("*** tb_lineno:", exc_traceback.tb_lineno)
            tk.Tk.report_callback_exception = report_callback_exception

            #the following code part is a bit garbled due to using TKinter interface
            ######################################################################################################################################################
            ######################################################################################################################################################
            ######################################################################################################################################################

            #definition of global vars for interface and graph design
            canvasWidth = 1320
            canvasHeight = 440
            #Cluster preparation
            sns.set_context('poster')
            sns.set_style('white')
            #sns.set_color_codes()
            #matplotlib.style.use('ggplot')
            plt.style.use('ggplot')
            graphFrame = None

            genPreviewMap = tk.IntVar(value = 0)
            createMinimumSpanningTree = False
            autoselectClusters = False


            def quitTkinter():
                #exits Tkinter gui and continues with code execution after mainloop()
                #global app
                #app.floater.destroy()
                #tkinter.messagebox.showinfo("Closing App", "Closing App")
                #plt.quit()
                global abort
                abort = True
                app.update() #see https://stackoverflow.com/questions/35040168/python-tkinter-error-cant-evoke-event-command
                app.destroy()
                app.quit() ##root.quit() causes mainloop to exit, see https://stackoverflow.com/questions/2307464/what-is-the-difference-between-root-destroy-and-root-quit
            def proceedWithCluster():
                global proceedClusting
                global fig1
                proceedClusting = True
            #def vis_tag(tag):
                #tkinter.messagebox.showinfo("Proceed", "Proceed")
                #if plt.figure(1):
                #    plt.figure(1).clf()
                app.update() #see https://stackoverflow.com/questions/35040168/python-tkinter-error-cant-evoke-event-command
                app.destroy()
                app.quit()

            def sel_photos(tag,cleanedPhotoList):
                #select photos from list based on a specific tag
                distinctLocalLocationCount = set()
                selectedPhotoList_Guids = []
                for cleanedPhotoLocation in cleanedPhotoList:
                    if tag in (cleanedPhotoLocation.photo_tags) or (tag in cleanedPhotoLocation.photo_caption):
                        selectedPhotoList_Guids.append(cleanedPhotoLocation.photo_guid)
                        distinctLocalLocationCount.add(cleanedPhotoLocation.photo_locID)
                return selectedPhotoList_Guids, len(distinctLocalLocationCount)

            def cluster_tag(toptag=None,preview=None,silent=None):
                if preview is None:
                    preview = False
                if silent is None:
                    silent = False
                global currentDisplayTag
                global tnum
                global limYMin, limYMax, limXMin, limXMax, imgRatio, floaterX, floaterY
                global fig1, fig2, fig3, fig4
                selectedPhotoList_Guids, distinctLocalLocationCount = sel_photos(toptag[0],cleanedPhotoList)
                percentageOfTotalLocations = distinctLocalLocationCount/(total_distinct_locations/100)
                if silent:
                    if toptag[0] in globalEmojiSet:
                        text = unicode_name(toptag[0])
                    else:
                        text = toptag[0]
                    print(f'({tnum} of {tmax}) Found {len(selectedPhotoList_Guids)} photos (UPL) for tag \'{text}\' ({percentageOfTotalLocations:.0f}% of total distinct locations in area)', end=" ")


                #clustering
                if len(selectedPhotoList_Guids) < 2:
                    return [], selectedPhotoList_Guids
                selectedPhotoList = [cleanedPhotoDict[x] for x in selectedPhotoList_Guids]
                #only used for tag clustering, otherwise (photo location clusters), global vars are used (df, points)
                df = pd.DataFrame(selectedPhotoList)
                points = df.as_matrix(['lng','lat']) #converts pandas data to numpy array (limit by list of column-names)

                #only return preview fig without clustering
                if preview == True:
                    #only map data
                    if genPreviewMap.get() == 1:
                        if fig1:
                            plt.figure(1).clf() #clear figure 1
                            #earth = Basemap()
                            #earth.bluemarble(alpha=0.42)
                            #earth.drawcoastlines(color='#555566', linewidth=1)
                            plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                            #reuse window of figure 1 for new figure
                            plt.scatter(points.T[0], points.T[1], color='red', **plot_kwds)
                            fig1 = plt.figure(num=1,figsize=(11, int(11*imgRatio)), dpi=80)
                            fig1.canvas.set_window_title('Preview Map')
                            #displayImgPath = pathname + '/Output/ClusterImg/00_displayImg.png'
                            #fig1.figure.savefig(displayImgPath)
                        else:

                            plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                            plt.scatter(points.T[0], points.T[1], color='red', **plot_kwds)
                            fig1 = plt.figure(num=1,figsize=(11, int(11*imgRatio)), dpi=80)
                            #earth = Basemap()
                            #earth.bluemarble(alpha=0.42)
                            #earth.drawcoastlines(color='#555566', linewidth=1)
                            fig1.canvas.set_window_title('Preview Map')
                        plt.gca().set_xlim([limXMin, limXMax])
                        plt.gca().set_ylim([limYMin, limYMax])
                        plt.tick_params(labelsize=10)
                        currentDisplayTag = toptag
                else:
                    #cluster data
                    tagRadiansData = np.radians(points) #conversion to radians for HDBSCAN (does not support decimal degrees)
                    #for each tag in overallNumOfUsersPerTag_global.most_common(1000) (descending), calculate HDBSCAN Clusters

                    minClusterSize = max(2,int(((len(selectedPhotoList_Guids))/100)*5)) #4% optimum
                    clusterer = hdbscan.HDBSCAN(min_cluster_size=minClusterSize,gen_min_span_tree=createMinimumSpanningTree,allow_single_cluster=True,min_samples=1)
                    #clusterer = hdbscan.HDBSCAN(min_cluster_size=minClusterSize,gen_min_span_tree=True,min_samples=1)
                    #clusterer = hdbscan.HDBSCAN(min_cluster_size=10,metric='haversine',gen_min_span_tree=False,allow_single_cluster=True)
                    #clusterer = hdbscan.robust_single_linkage_.RobustSingleLinkage(cut=0.000035)
                    #srsl_plt = hdbscan.robust_single_linkage_.plot()

                    #Start clusterer on different thread to prevent GUI from freezing
                    #See: http://stupidpythonideas.blogspot.de/2013/10/why-your-gui-app-freezes.html
                    #https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
                    #if silent:
                    #    #on silent command line operation, don't use multiprocessing
                    #    clusterer = fit_cluster(clusterer,tagRadiansData)
                    #else:
                    with warnings.catch_warnings():
                        #disable joblist multithread warning
                        warnings.simplefilter('ignore', UserWarning)
                        async_result = pool.apply_async(Utils.fit_cluster, (clusterer, tagRadiansData))
                        clusterer = async_result.get()
                        #clusterer.fit(tagRadiansData)
                        #updateNeeded = False

                    if autoselectClusters:
                        sel_labels = clusterer.labels_ #auto selected clusters
                    else:
                        sel_labels = clusterer.single_linkage_tree_.get_clusters(Utils.getRadiansFromMeters(clusterTreeCuttingDist), min_cluster_size=2) #0.000035 without haversine: 223 m (or 95 m for 0.000015)

                    #exit function in case final processing loop (no figure generating)
                    if silent:
                        return sel_labels, selectedPhotoList_Guids
                    mask_noisy = (sel_labels == -1)
                    number_of_clusters = len(np.unique(sel_labels[~mask_noisy])) #len(sel_labels)
                    #palette = sns.color_palette("hls", )
                    #palette = sns.color_palette(None, len(sel_labels)) #sns.color_palette("hls", ) #sns.color_palette(None, 100)
                    palette = sns.color_palette("husl", number_of_clusters+1)
                    sel_colors = [palette[x] if x >= 0
                                  else (0.5, 0.5, 0.5)
                                  #for x in clusterer.labels_ ]
                                  for x in sel_labels] #clusterer.labels_ (best selection) or sel_labels (cut distance)
                    #tkinter.messagebox.showinfo("Num of clusters: ", str(len(sel_colors)) + " " + str(sel_colors[1]))
                    #output/update matplotlib figures

                    if fig1:
                        plt.figure(1).clf()
                        plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold') #plt references the last figure accessed
                        ax = plt.scatter(points.T[0], points.T[1], color=sel_colors, **plot_kwds)
                        fig1 = plt.figure(num=1,figsize=(11, int(11*imgRatio)), dpi=80)
                        fig1.canvas.set_window_title('Cluster Preview')
                        distText = ''
                        if autoselectClusters == False:
                            distText = '@ ' + str(clusterTreeCuttingDist) +'m'
                        plt.title(f'Cluster Preview {distText}', fontsize=12,loc='center')
                        #plt.title('Cluster Preview')
                        #xmax = ax.get_xlim()[1]
                        #ymax = ax.get_ylim()[1]
                        noisyTxt = '{}/{}'.format(mask_noisy.sum(), len(mask_noisy))
                        plt.text(limXMax, limYMax,f'{number_of_clusters} Cluster (Noise: {noisyTxt})',fontsize=10,horizontalalignment='right',verticalalignment='top',fontweight='bold')
                    else:
                        plt.scatter(points.T[0], points.T[1], c=sel_colors, **plot_kwds)
                        fig1 = plt.figure(num=1,figsize=(11, int(11*imgRatio)), dpi=80)
                        fig1.canvas.set_window_title('Cluster Preview')
                        plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                        distText = ''
                        if autoselectClusters == False:
                            distText = '@ ' + str(clusterTreeCuttingDist) +'m'
                        plt.title(f'Cluster Preview {distText}', fontsize=12,loc='center')
                        #xmax = fig1.get_xlim()[1]
                        #ymax = fig1.get_ylim()[1]
                        noisyTxt = '{} / {}'.format(mask_noisy.sum(), len(mask_noisy))
                        plt.text(limXMax, limYMax,f'{number_of_clusters} Clusters (Noise: {noisyTxt})',fontsize=10,horizontalalignment='right',verticalalignment='top',fontweight='bold')
                    plt.gca().set_xlim([limXMin, limXMax])
                    plt.gca().set_ylim([limYMin, limYMax])
                    plt.tick_params(labelsize=10)
                    #if len(tagRadiansData) < 10000:
                    if fig2:
                        plt.figure(2).clf()
                        plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                        #plt.title('Condensed Tree', fontsize=12,loc='center')
                        clusterer.condensed_tree_.plot(select_clusters=False, selection_palette=sel_colors)#,label_clusters=False
                        #tkinter.messagebox.showinfo("Num of clusters: ", str(len(sel_colors)) + " " + str(sel_colors[0]))
                    else:
                        plt.figure(2).canvas.set_window_title('Condensed Tree')
                        fig2 = clusterer.condensed_tree_.plot(select_clusters=False, selection_palette=sel_colors)#,label_clusters=False
                        #tkinter.messagebox.showinfo("Num of clusters: ", str(len(sel_colors)) + " " + str(sel_colors[1]))
                        #fig2 = clusterer.condensed_tree_.plot(select_clusters=False, selection_palette=sel_colors,label_clusters=True)
                        #plt.title('Condensed Tree', fontsize=12,loc='center')
                        plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                    plt.tick_params(labelsize=10)
                    if fig3:
                        plt.figure(3).clf()
                        plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                        plt.title('Single Linkage Tree', fontsize=12,loc='center')
                        #clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=50)
                        ax = clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=max(50,min(number_of_clusters*10,256))) #p is the number of max count of leafs in the tree, this should at least be the number of clusters*10, not lower than 50 [but max 500 to not crash]
                        #tkinter.messagebox.showinfo("messagr", str(type(ax)))
                        #plot cutting distance
                        y = Utils.getRadiansFromMeters(clusterTreeCuttingDist)
                        xmin = ax.get_xlim()[0]
                        xmax = ax.get_xlim()[1]
                        line, = ax.plot([xmin, xmax], [y, y], color='k', label=f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                        line.set_label(f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                        ax.legend(fontsize=10)
                        vals = ax.get_yticks()
                        ax.set_yticklabels(['{:3.1f}m'.format(Utils.getMetersFromRadians(x)) for x in vals])
                    else:
                        plt.figure(3).canvas.set_window_title('Single Linkage Tree')
                        fig3 = clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=max(50,min(number_of_clusters*10,256)))
                        plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                        plt.title('Single Linkage Tree', fontsize=12,loc='center')
                        #tkinter.messagebox.showinfo("messagr", str(type(fig3)))
                        #plot cutting distance
                        y = Utils.getRadiansFromMeters(clusterTreeCuttingDist)
                        xmin = fig3.get_xlim()[0]
                        xmax = fig3.get_xlim()[1]
                        line, = fig3.plot([xmin, xmax], [y, y], color='k', label=f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                        line.set_label(f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                        fig3.legend(fontsize=10)
                        vals = fig3.get_yticks()
                        fig3.set_yticklabels([f'{Utils.getMetersFromRadians(x):3.1f}m' for x in vals])
                    plt.tick_params(labelsize=10)
                    if createMinimumSpanningTree:
                        if fig4:
                            plt.figure(4).clf()
                            plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                            #plt.title('Single Linkage Tree', fontsize=12,loc='center')
                            #clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=50)
                            ax = clusterer.minimum_spanning_tree_.plot(edge_cmap='viridis',
                                          edge_alpha=0.6,
                                          node_size=10,
                                          edge_linewidth=1) #tkinter.messagebox.showinfo("messagr", str(type(ax)))
                            fig4.canvas.set_window_title('Minimum Spanning Tree')
                            plt.title(f'Minimum Spanning Tree @ {clusterTreeCuttingDist}m', fontsize=12,loc='center')
                            ax.legend(fontsize=10)
                            #ax=plt.gca()        #plt.gca() for current axis, otherwise set appropriately.
                            #im=ax.images        #this is a list of all images that have been plotted
                            #cb=im[0].colorbar  ##in this case I assume to be interested to the last one plotted, otherwise use the appropriate index
                            #cb.ax.tick_params(labelsize=10)
                            #vals = cb.ax.get_yticks()
                            #cb.ax.set_yticklabels(['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals])
                        else:
                            plt.figure(4).canvas.set_window_title('Minimum Spanning Tree')
                            fig4 = clusterer.minimum_spanning_tree_.plot(edge_cmap='viridis',
                                          edge_alpha=0.6,
                                          node_size=10,
                                          edge_linewidth=1) #tkinter.messagebox.showinfo("messagr", str(type(ax)))
                            plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                            plt.title(f'Minimum Spanning Tree @ {clusterTreeCuttingDist}m', fontsize=12,loc='center')
                            fig4.legend(fontsize=10)
                            #ax=plt.gca()        #plt.gca() for current axis, otherwise set appropriately.
                            #im=ax.images        #this is a list of all images that have been plotted
                            #cb=im[0].colorbar  ##in this case I assume to be interested to the last one plotted, otherwise use the appropriate index
                            #cb.ax.tick_params(labelsize=10)
                            #vals = cb.ax.get_yticks()
                            #cb.ax.set_yticklabels(['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals])
                    plt.tick_params(labelsize=10)
                    #adjust scalebar limits
                    global tkScalebar
                    tkScalebar.configure(from_=(clusterTreeCuttingDist/100), to=(clusterTreeCuttingDist*2))

            def change_clusterDist(val):
                #tkinter.messagebox.showinfo("messagr", val)
                global clusterTreeCuttingDist
                #global canvas
                #global tkScalebar
                clusterTreeCuttingDist = float(val)#tkScalebar.get()

            def onselect(evt):
                # Note here that Tkinter passes an event object to onselect()
                global lastselectionList
                global tnum
                w = evt.widget
                if lastselectionList: #if not empty
                    changedSelection = set(lastselectionList).symmetric_difference(set(w.curselection()))
                    lastselectionList = w.curselection()
                else:
                    lastselectionList = w.curselection()
                    changedSelection = w.curselection()
                index = int(list(changedSelection)[0])
                value = w.get(index)
                #tkinter.messagebox.showinfo("You selected ", value)
                tnum = 1
                cluster_tag(topTagsList[index],True) #generate only preview map
                #plt.close('all')
            def cluster_currentDisplayTag():
                if currentDisplayTag:
                    #tkinter.messagebox.showinfo("Clustertag: ", str(currentDisplayTag))
                    cluster_tag(currentDisplayTag)
                else:
                    cluster_tag(topTagsList[0])
            def scaletest_currentDisplayTag():
                global tkScalebar
                global fig1
                if currentDisplayTag:
                    clustertag = currentDisplayTag
                else:
                    clustertag = topTagsList[0]
                scalecalclist = []
                dmax = int(clusterTreeCuttingDist*10)
                dmin = int(clusterTreeCuttingDist/10)
                dstep = int(((clusterTreeCuttingDist*10)-(clusterTreeCuttingDist/10))/100)
                for i in range(dmin,dmax,dstep):
                    change_clusterDist(i)
                    tkScalebar.set(i)
                    app.update()
                    #clusterTreeCuttingDist = i
                    clusters, selectedPhotoList_Guids = cluster_tag(clustertag, None, True)
                    mask_noisy = (clusters == -1)
                    number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
                    if number_of_clusters == 1:
                        break
                    form_string = f'{i},{number_of_clusters},{mask_noisy.sum()},{len(mask_noisy)},\n'
                    scalecalclist.append(form_string)
                with open(f'02_Output/scaletest_{clustertag[0]}.txt', "w", encoding='utf-8') as logfile_a:
                    for scalecalc in scalecalclist:
                        logfile_a.write(scalecalc)
                plt.figure(1).clf()
                plt.suptitle(clustertag[0].upper(), fontsize=18, fontweight='bold') #plt references the last figure accessed
                fig1 = plt.figure(num=1,figsize=(11, int(11*imgRatio)), dpi=80)
                fig1.canvas.set_window_title('Cluster Preview')
                distText = ''
                if autoselectClusters == False:
                    distText = f'@ {clusterTreeCuttingDist}m'
                plt.title(f'Cluster Preview {distText}', fontsize=12,loc='center')
                noisyTxt = f'{mask_noisy.sum()}/{len(mask_noisy)}'
                plt.text(limXMax, limYMax,f'{number_of_clusters} Cluster (Noise: {noisyTxt})',fontsize=10,horizontalalignment='right',verticalalignment='top',fontweight='bold')

            def delete(listbox):
                global topTagsList
                global lastselectionList
                lastselectionList = []
                # Delete from Listbox
                selection = listbox.curselection()
                for index in selection[::-1]:
                    listbox.delete(index)
                    del(topTagsList[index])
            ######################################################################################################################################################
            ######################################################################################################################################################
            ######################################################################################################################################################

            #A frame is created for each window/part of the gui; after it is used, it is destroyed with frame.destroy()

            listboxFrame = tk.Frame(app.floater)
            canvas = tk.Canvas(listboxFrame, width=150, height=200, highlightthickness=0,background="gray7")
            l = tk.Label(canvas, text="Optional: Exclude tags.", background="gray7",fg="gray80",font="Arial 10 bold")
            l.pack(padx=10, pady=10)
            l = tk.Label(canvas, text="Select all tags you wish to exclude from analysis \n and click on remove to proceed.", background="gray7",fg="gray80")
            l.pack(padx=10, pady=10)
            #if cfg.data_source == "fromInstagram_PGlbsnEmoji":
            #    listbox_font = ("twitter Color Emoji", 12, "bold")
            #    #listbox_font = ("Symbola", 12, "bold")
            #else:
            listbox_font = None
            listbox = tk.Listbox(canvas,selectmode=tk.MULTIPLE, bd=0,background="gray29",fg="gray91",width=30,font=listbox_font)
            listbox.bind('<<ListboxSelect>>', onselect)
            scroll = tk.Scrollbar(canvas, orient=tk.VERTICAL,background="gray20",borderwidth=0)
            scroll.configure(command=listbox.yview)
            scroll.pack(side="right", fill="y")
            listbox.pack()
            listbox.config(yscrollcommand=scroll.set)
            for item in topTagsList: #only for first 500 entries: use topTagsList[:500]
                try:
                    listbox.insert(tk.END, f'{item[0]} ({item[1]} user)')
                except tk.TclError:
                    #print(item[0].encode("utf-8"))
                    emoji = "".join(unicode_name(c) for c in item[0]) #Utils.with_surrogates()
                    listbox.insert(tk.END, f'{emoji} ({item[1]} user)')
            canvas.pack(fill='both',padx=0, pady=0)
            listboxFrame.pack(fill='both',padx=0, pady=0)
            buttonsFrame = tk.Frame(app.floater)
            canvas = tk.Canvas(buttonsFrame, width=150, height=200, highlightthickness=0,background="gray7")
            b = tk.Button(canvas, text = "Remove Tag(s)", command = lambda: delete(listbox), background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
            b.pack(padx=10, pady=10)
            c = tk.Checkbutton(canvas, text="Map Tags", variable=genPreviewMap,background="gray7",fg="gray80",borderwidth=0,font="Arial 10 bold")
            c.pack(padx=10, pady=10)
            global tkScalebar
            tkScalebar = tk.Scale(canvas, from_=(clusterTreeCuttingDist/100), to=(clusterTreeCuttingDist*2), orient=tk.HORIZONTAL,resolution=0.1,command=change_clusterDist,length=300,label="Cluster Cut Distance (in Meters)",background="gray20",borderwidth=0,fg="gray80",font="Arial 10 bold")
            tkScalebar.set(clusterTreeCuttingDist)#(clusterTreeCuttingDist*10) - (clusterTreeCuttingDist/10)/2) #set position of slider to center
            tkScalebar.pack()
            b = tk.Button(canvas, text = "Cluster Preview", command=cluster_currentDisplayTag, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
            b.pack(padx=10, pady=10,side="left")
            b = tk.Button(canvas, text = "Scale Test", command=scaletest_currentDisplayTag, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
            b.pack(padx=10, pady=10,side="left")
            b = tk.Button(canvas, text = "Proceed..", command=proceedWithCluster, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
            b.pack(padx=10, pady=10,side="left")
            b = tk.Button(canvas, text = "Quit", command=quitTkinter, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
            b.pack(padx=10, pady=10,side="left")
            canvas.pack(fill='both',padx=0, pady=0)
            buttonsFrame.pack(fill='both',padx=0, pady=0)

            #END OF TKINTER LOOP, welcome back to command line interface
            app.mainloop()
            plt.close("all")

            noClusterPhotos_perTag_DictOfLists = defaultdict(list)
            clustersPerTag = defaultdict(list)
            if proceedClusting:
                #Proceed with clustering all tags
                crs_wgs = pyproj.Proj(init='epsg:4326') #data always in lat/lng WGS1984
                if cfg.override_crs is None:
                    #Calculate best UTM Zone SRID/EPSG Code
                    input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
                    input_lat_center = bound_points_shapely.centroid.coords[0][1]
                    epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
                    crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}')
                project = lambda x, y: pyproj.transform(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init=f'epsg:{epsg_code}'), x, y)
                #geom_proj = transform(project, alphaShapeAndMeta[0])

                if cfg.local_saturation_check:
                    clusters, selectedPhotoList_Guids = cluster_tag(singleMostUsedtag, None, True)
                    numpy_selectedPhotoList_Guids = np.asarray(selectedPhotoList_Guids)
                    mask_noisy = (clusters == -1)
                    number_of_clusters = len(np.unique(clusters[~mask_noisy]))
                    print(f'--> {number_of_clusters} cluster.')
                    clusterPhotosGuidsList = []
                    for x in range(number_of_clusters):
                        currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
                        clusterPhotosGuidsList.append(currentClusterPhotoGuids)
                    noClusterPhotos_perTag_DictOfLists[singleMostUsedtag[0]] = list(numpy_selectedPhotoList_Guids[clusters==-1])
                    # Sort descending based on size of cluster: https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
                    clusterPhotosGuidsList.sort(key=len, reverse=True)
                    if not len(clusterPhotosGuidsList) == 0:
                        clustersPerTag[singleMostUsedtag[0]] = clusterPhotosGuidsList
                global tnum
                tnum = 1
                for toptag in topTagsList:
                    if cfg.local_saturation_check and tnum == 1 and toptag[0] in clustersPerTag:
                        #skip toptag if already clustered due to local saturation
                        continue
                    clusters, selectedPhotoList_Guids = cluster_tag(toptag, None, True)
                    #print("baseDataList: ")
                    #print(str(type(selectedPhotoList)))
                    #for s in selectedPhotoList[:2]:
                    #    print(*s)
                    #print("resultData: ")
                    ##for s in clusters[:2]:
                    ##    print(*s)
                    #print(str(type(clusters)))
                    #print(clusters)
                    #clusters contains the cluster values (-1 = no cluster, 0 maybe, >0 = cluster
                    # in the same order, selectedPhotoList contains all original photo data, thus clusters[10] and selectedPhotoList[10] refer to the same photo

                    numpy_selectedPhotoList_Guids = np.asarray(selectedPhotoList_Guids)
                    mask_noisy = (clusters == -1)
                    if len(selectedPhotoList_Guids) == 1:
                        number_of_clusters = 0
                    else:
                        number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
                    #if number_of_clusters > 200:
                    #    log.info("--> Too many, skipped for this scale.")
                    #    continue
                    if not number_of_clusters == 0:
                        print(f'--> {number_of_clusters} cluster.')
                        tnum += 1
                        photo_num = 0
                        #clusternum_photolist = zip(clusters,selectedPhotoList)
                        #clusterPhotosList = [[] for x in range(number_of_clusters)]
                        clusterPhotosGuidsList = []
                        for x in range(number_of_clusters):
                            currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
                            clusterPhotosGuidsList.append(currentClusterPhotoGuids)
                        noClusterPhotos_perTag_DictOfLists[toptag[0]] = list(numpy_selectedPhotoList_Guids[clusters==-1])
                        # Sort descending based on size of cluster: https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
                        clusterPhotosGuidsList.sort(key=len, reverse=True)
                        if not len(clusterPhotosGuidsList) == 0:
                            clustersPerTag[toptag[0]] = clusterPhotosGuidsList
                    else:
                        print("--> No cluster.")
                        noClusterPhotos_perTag_DictOfLists[toptag[0]] = list(numpy_selectedPhotoList_Guids)
                    #for x in clusters:
                    #    #photolist = []
                    #    if x >= 0: # no clusters: x = -1
                    #        clusterPhotosList[x].append([selectedPhotoList[photo_num]])
                    #        #clusterPhotosArray_dict[x].add(selectedPhotoList[photo_num])
                    #    else:
                    #        noClusterPhotos_perTag_DictOfLists[toptag[0]].append(selectedPhotoList[photo_num])
                    #    photo_num+=1

                    #print("resultList: ")
                    #for s in clusterPhotosList[:2]:
                    #    print(*s)
                    #print(str(toptag) + " - Number of clusters: " + str(len(clusterPhotosList)) + " Photo num: " + str(photo_num))

                    #plt.autoscale(enable=True)

                    #if tnum == 50:
                    #    break
                        #plt.savefig('foo.png')
                        #sys.exit()
                sys.stdout.flush()
                log.info("########## STEP 4 of 6: Generating Alpha Shapes ##########")
                #if (tnum % 50 == 0):#modulo: if division has no remainder, force update cmd output
                #sys.stdout.flush()
                #for each cluster of points, calculate boundary shape and add statistics (HImpTag etc.)
                listOfAlphashapesAndMeta = []
                tnum = 0
                if cfg.local_saturation_check:
                    #calculate total area of Top1-Tag for 80% saturation check for lower level tags
                    saturationExcludeCount = 0
                    clusterPhotoGuidList = clustersPerTag.get(singleMostUsedtag[0], None)
                    #print("Toptag: " + str(singleMostUsedtag[0]))
                    if clusterPhotoGuidList is None:
                        sys.exit(f'No Photos found for toptag: {singleMostUsedtag}')
                    toptagArea = Utils.generateClusterShape(toptag,clusterPhotoGuidList,cleanedPhotoDict,crs_wgs,crs_proj,clusterTreeCuttingDist,cfg.local_saturation_check)[1]
                for toptag in topTagsList:
                    tnum += 1
                    clusterPhotoGuidList = clustersPerTag.get(toptag[0], None)
                    #Generate tag Cluster Shapes
                    if clusterPhotoGuidList:
                        listOfAlphashapesAndMeta_tmp,tagArea = Utils.generateClusterShape(toptag,clusterPhotoGuidList,cleanedPhotoDict,crs_wgs,crs_proj,clusterTreeCuttingDist,cfg.local_saturation_check)
                        if cfg.local_saturation_check and not tagArea == 0 and not tnum == 1:
                            localSaturation = tagArea/(toptagArea/100)
                            #print("Local Saturation for Tag " + toptag[0] + ": " + str(round(localSaturation,0)))
                            if localSaturation > 60:
                                #skip tag entirely due to saturation (if total area > 80% of total area of toptag clusters)
                                #print("Skipped: " + toptag[0] + " due to saturation (" + str(round(localSaturation,0)) + "%).")
                                saturationExcludeCount += 1
                                continue #next toptag

                        if len(listOfAlphashapesAndMeta_tmp) > 0:
                            listOfAlphashapesAndMeta.extend(listOfAlphashapesAndMeta_tmp)

                    singlePhotoGuidList = noClusterPhotos_perTag_DictOfLists.get(toptag[0], None)
                    if singlePhotoGuidList:
                        shapetype = "Single cluster"
                        #print("Single: " + str(len(singlePhotoGuidList)))
                        photos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
                        for single_photo in photos:
                            #project lat/lng to UTM
                            x, y = pyproj.transform(crs_wgs, crs_proj, single_photo.lng, single_photo.lat)
                            pcoordinate = geometry.Point(x, y)
                            result_polygon = pcoordinate.buffer(clusterTreeCuttingDist/4,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                            #result_polygon = pcoordinate.buffer(min(distXLng,distYLat)/100,resolution=3)
                            if result_polygon is not None and not result_polygon.is_empty:
                                listOfAlphashapesAndMeta.append((result_polygon,1,max(single_photo.photo_views,single_photo.photo_likes),1,str(toptag[0]),toptag[1],1,1,1,shapetype))
                log.info(f'{len(listOfAlphashapesAndMeta)} Alpha Shapes. Done.')
                if cfg.local_saturation_check and not saturationExcludeCount == 0:
                    log.info(f'Excluded {saturationExcludeCount} Tags on local saturation check.')
                ##Output Boundary Shapes in merged Shapefile##
                log.info("########## STEP 5 of 6: Writing Results to Shapefile ##########")

               ##Calculate best UTM Zone SRID/EPSG Code
               #input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
               #input_lat_center = bound_points_shapely.centroid.coords[0][1]
               #epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
               #project = lambda x, y: pyproj.transform(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:{0}'.format(epsg_code)), x, y)

                # Define polygon feature geometry
                schema = {
                    'geometry': 'Polygon',
                    'properties': {'Join_Count': 'int',
                                   'Views': 'int',
                                   'COUNT_User': 'int',
                                   'ImpTag': 'str',
                                   'TagCountG': 'int',
                                   'HImpTag': 'int',
                                   'Weights': 'float',
                                   'WeightsV2': 'float',
                                   'WeightsV3': 'float',
                                   #'shapetype': 'str',
                                   'emoji': 'int'},
                }

                #Normalization of Values (1-1000 Range), precalc Step:
                #######################################
                weightsv1_range = [x[6] for x in listOfAlphashapesAndMeta] #get the n'th column out for calculating the max/min
                weightsv2_range = [x[7] for x in listOfAlphashapesAndMeta]
                weightsv3_range = [x[8] for x in listOfAlphashapesAndMeta]
                weightsv1_min = min(weightsv1_range)
                weightsv1_max = max(weightsv1_range)
                weightsv2_min = min(weightsv2_range)
                weightsv2_max = max(weightsv2_range)
                weightsv3_min = min(weightsv3_range)
                weightsv3_max = max(weightsv3_range)
                #precalc
                #https://stats.stackexchange.com/questions/70801/how-to-normalize-data-to-0-1-range
                weightsv1_mod_a = (1000-1)/(weightsv1_max-weightsv1_min)
                weightsv1_mod_b = 1000 - weightsv1_mod_a * weightsv1_max
                weightsv2_mod_a = (1000-1)/(weightsv2_max-weightsv2_min)
                weightsv2_mod_b = 1000 - weightsv2_mod_a * weightsv2_max
                weightsv3_mod_a = (1000-1)/(weightsv3_max-weightsv3_min)
                weightsv3_mod_b = 1000 - weightsv3_mod_a * weightsv3_max
                #######################################
                # Write a new Shapefile
                # WGS1984
                if (cfg.cluster_tags == False and cfg.cluster_emoji == True):
                    shapefileName = "allEmojiCluster"
                else:
                    shapefileName = "allTagCluster"
                with fiona.open(f'02_Output/{shapefileName}.shp', mode='w', encoding='UTF-8', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
                    # Normalize Weights to 0-1000 Range
                    idx = 0
                    for alphaShapeAndMeta in listOfAlphashapesAndMeta:
                        if idx == 0:
                            HImP = 1
                        else:
                            if listOfAlphashapesAndMeta[idx][4] != listOfAlphashapesAndMeta[idx-1][4]:
                                HImP = 1
                            else:
                                HImP = 0
                        #emoName = unicode_name(alphaShapeAndMeta[4])
                        #Calculate Normalized Weights Values based on precalc Step
                        if not alphaShapeAndMeta[6] == 1:
                            weight1_normalized = weightsv1_mod_a * alphaShapeAndMeta[6] + weightsv1_mod_b
                        else:
                            weight1_normalized = 1
                        if not alphaShapeAndMeta[7] == 1:
                            weight2_normalized = weightsv2_mod_a * alphaShapeAndMeta[7] + weightsv2_mod_b
                        else:
                            weight2_normalized = 1
                        if not alphaShapeAndMeta[8] == 1:
                            weight3_normalized = weightsv3_mod_a * alphaShapeAndMeta[8] + weightsv3_mod_b
                        else:
                            weight3_normalized = 1
                        idx += 1
                        #project data
                        #geom_proj = transform(project, alphaShapeAndMeta[0])
                        #c.write({
                        #    'geometry': geometry.mapping(geom_proj),
                        if cfg.cluster_emoji and alphaShapeAndMeta[4] in globalEmojiSet:
                            emoji = 1
                            ImpTagText = ""
                        else:
                            emoji = 0
                            ImpTagText = f'{alphaShapeAndMeta[4]}'
                        c.write({
                            'geometry': geometry.mapping(alphaShapeAndMeta[0]),
                            'properties': {'Join_Count': alphaShapeAndMeta[1],
                                           'Views': alphaShapeAndMeta[2],
                                           'COUNT_User': alphaShapeAndMeta[3],
                                           'ImpTag': ImpTagText,
                                           'TagCountG': alphaShapeAndMeta[5],
                                           'HImpTag': HImP,
                                           'Weights': weight1_normalized,
                                           'WeightsV2': weight2_normalized,
                                           'WeightsV3': weight3_normalized,
                                           #'shapetype': alphaShapeAndMeta[9],
                                           'emoji': emoji},
                        })
                if cfg.cluster_emoji:
                    with open("02_Output/emojiTable.csv", "w", encoding='utf-8') as emojiTable:
                        emojiTable.write("FID,Emoji\n")
                        idx = 0
                        for alphaShapeAndMeta in listOfAlphashapesAndMeta:
                            if alphaShapeAndMeta[4] in globalEmojiSet:
                                ImpTagText = f'{alphaShapeAndMeta[4]}'
                            else:
                                ImpTagText = ""
                            emojiTable.write(f'{idx},{ImpTagText}\n')
                            idx += 1

    else:
        print(f'\nUser abort.')
    if abort == False and cfg.cluster_photos == True:
        log.info("########## STEP 6 of 6: Calculating Overall Photo Location Clusters ##########")

        #if not 'clusterTreeCuttingDist' in locals():
        #global clusterTreeCuttingDist
        if clusterTreeCuttingDist == 0:
            clusterTreeCuttingDist = int(input("Specify Cluster (Cut) Distance:\n"))
        selectedPhotoList_Guids = []
        #if not 'cleanedPhotoList' in locals():
        #global cleanedPhotoList
        if len(cleanedPhotoList) == 0:
            cleanedPhotoList = list(cleanedPhotoDict.values())
        for cleanedPhotoLocation in cleanedPhotoList:
            selectedPhotoList_Guids.append(cleanedPhotoLocation.photo_guid)
        selectedPhotoList = cleanedPhotoList
        df = pd.DataFrame(selectedPhotoList)
        points = df.as_matrix(['lng','lat'])
        tagRadiansData = np.radians(points)
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2,gen_min_span_tree=False,allow_single_cluster=False,min_samples=1)
        #clusterer.fit(tagRadiansData)
        with warnings.catch_warnings():
            #disable joblist multithread warning
            warnings.simplefilter('ignore', UserWarning)
            async_result = pool.apply_async(Utils.fit_cluster, (clusterer, tagRadiansData))
            clusterer = async_result.get()
        clusters = clusterer.single_linkage_tree_.get_clusters(Utils.getRadiansFromMeters(clusterTreeCuttingDist/8), min_cluster_size=2)
        listOfPhotoClusters = []
        numpy_selectedPhotoList_Guids = np.asarray(selectedPhotoList_Guids)
        mask_noisy = (clusters == -1)
        number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
        print(f'--> {number_of_clusters} Photo cluster.')
        #clusternum_photolist = zip(clusters,selectedPhotoList)
        #clusterPhotosList = [[] for x in range(number_of_clusters)]
        clusterPhotosGuidsList = []
        for x in range(number_of_clusters):
            currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
            clusterPhotosGuidsList.append(currentClusterPhotoGuids)
        noClusterPhotos = list(numpy_selectedPhotoList_Guids[clusters==-1])
        clusterPhotosGuidsList.sort(key=len,reverse=True)
        if cfg.cluster_tags is False:
            #detect projection if not already
            limYMin,limYMax,limXMin,limXMax = Utils.getRectangleBounds(points)
            bound_points_shapely = geometry.MultiPoint([(limXMin, limYMin), (limXMax, limYMax)])
            crs_wgs = pyproj.Proj(init='epsg:4326') #data always in lat/lng WGS1984
            if cfg.override_crs is None:
                #Calculate best UTM Zone SRID/EPSG Code
                input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
                input_lat_center = bound_points_shapely.centroid.coords[0][1]
                epsg_code = Utils.convert_wgs_to_utm(input_lon_center, input_lat_center)
                crs_proj = pyproj.Proj(init=f'epsg:{epsg_code}')
        for photo_cluster in clusterPhotosGuidsList:
            photos = [cleanedPhotoDict[x] for x in photo_cluster]
            uniqueUserCount = len(set([photo.userid for photo in photos]))
            #get points and project coordinates to suitable UTM
            points = [geometry.Point(pyproj.transform(crs_wgs, crs_proj, photo.lng, photo.lat))
                      for photo in photos]
            point_collection = geometry.MultiPoint(list(points))
            result_polygon = point_collection.convex_hull #convex hull
            result_centroid = result_polygon.centroid
            if result_centroid is not None and not result_centroid.is_empty:
                listOfPhotoClusters.append((result_centroid,uniqueUserCount))
            #clusterPhotoGuidList = clustersPerTag.get(None, None)
        #noclusterphotos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
        for photoGuid_noCluster in noClusterPhotos:
            photo = cleanedPhotoDict[photoGuid_noCluster]
            x, y = pyproj.transform(crs_wgs, crs_proj, photo.lng, photo.lat)
            pcenter = geometry.Point(x, y)
            if pcenter is not None and not pcenter.is_empty:
                listOfPhotoClusters.append((pcenter,1))
        # Define a polygon feature geometry with one attribute
        schema = {
            'geometry': 'Point',
            'properties': {'Join_Count': 'int'},
        }

        # Write a new Shapefile
        # WGS1984
        with fiona.open('02_Output/allPhotoCluster.shp', mode='w', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
            ## If there are multiple geometries, put the "for" loop here
            idx = 0
            for photoCluster in listOfPhotoClusters:
                idx += 1
                c.write({
                    'geometry': geometry.mapping(photoCluster[0]),
                    'properties': {'Join_Count': photoCluster[1]},
                    })
    print("Writing log file..")
    later = time.time()
    hours, rem = divmod(later-now, 3600)
    minutes, seconds = divmod(rem, 60)
    difference = int(later - now)
    log.info(f'\nDone.\n{int(hours):0>2} Hours {int(minutes):0>2} Minutes and {seconds:05.2f} Seconds passed.')
    #log_texts_list.append(reportMsg)
    #with open(log_file, "w", encoding='utf-8') as logfile_a:
    #    for logtext in log_texts_list:
    #        logfile_a.write(logtext)
    #print(reportMsg)
    input("Press any key to exit...")
    sys.exit()

if __name__ == "__main__":
    main()
