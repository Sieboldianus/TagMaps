#!/usr/bin/env python
# coding: utf8
# generateTagClusters

"""
generateTagClusters.py

- will read in geotagged (lat/lng) decimal degree point data
- will generate HDBSCAN Cluster Hierarchy
- will output Alpha Shapes/Delauney for cluster cut at specific distance
"""

__author__      = "Alexander Dunkel"
__license__   = "GNU GPLv3"
__version__ = "0.9.1"

import csv
import os
os.system('mode con: cols=197 lines=40')
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
import def_functions
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

#enable for map display
#from mpl_toolkits.basemap import Basemap
#from PIL import Image

import fiona #Fiona needed for reading Shapefile
from fiona.crs import from_epsg
import shapely.geometry as geometry
import pyproj #import Proj, transform
#https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects
from shapely.ops import transform
#from shapely.geometry import Polygon
#from shapely.geometry import shape
#from shapely.geometry import Point
from decimal import Decimal

#alternative Shapefile module pure Python
#https://github.com/GeospatialPython/pyshp#writing-shapefiles
#import shapefile

######################    
####config section####
######################
log_file = "02_Output/log.txt"
log_texts_list = []

def print_store_log(text,end=None):
    if end is None:
        addEnd = False
        end = '\n'
    else:
        addEnd = True
    #watch out for non-printable characters in console
    try:
        print(text,end=end)
    except UnicodeEncodeError:
        print("#".join(re.findall("[a-zA-Z]+", text)))
    log_texts_list.append(text + end)

##Load Filterlists
SortOutAlways_file = "00_Config/SortOutAlways.txt"
SortOutAlways_inStr_file = "00_Config/SortOutAlways_inStr.txt"
SortOutAlways_set = set()
SortOutAlways_inStr_set = set()
if not os.path.isfile(SortOutAlways_file):
    print(SortOutAlways_file + "not found.")
#else read logfile
else:
    with open(SortOutAlways_file, newline='', encoding='utf8') as f: #read each unsorted file and sort lines based on datetime (as string)
        SortOutAlways_set = set([line.lower().rstrip('\r\n') for line in f])
    print("Loaded " + str(len(SortOutAlways_set)) + " stoplist items.")
if not os.path.isfile(SortOutAlways_inStr_file):
    print(SortOutAlways_inStr_file + "not found.")
#else read logfile
else:
    with open(SortOutAlways_inStr_file, newline='', encoding='utf8') as f: #read each unsorted file and sort lines based on datetime (as string)
        SortOutAlways_inStr_set = set([line.lower().rstrip('\r\n') for line in f])
    print("Loaded " + str(len(SortOutAlways_inStr_set)) + " inStr stoplist items.")

writeGISCompLine = True # writes placeholder entry after headerline for avoiding GIS import format issues

#Choose one of four options for Input data type:
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', "--source", default= "fromFlickr_CSV")     # naming it "source"
parser.add_argument('-r', "--removeLongTail", default= True)
parser.add_argument('-e', "--EPSG", default= None)  
args = parser.parse_args()    # returns data from the options specified (source)
DSource = args.source
removeLongTail = args.removeLongTail
overrideCRS = args.EPSG
if overrideCRS is not None and overrideCRS.isdigit() is False:
    overrideCRS = None
else:
    #try loading Custom CRS at beginning
    crs_proj = pyproj.Proj(init='epsg:{0}'.format(overrideCRS))
    print("Custom CRS set: " + str(crs_proj.srs))
    epsg_code = overrideCRS
#print(str(removeLongTail))
pathname = os.getcwd()
if not os.path.exists(pathname + '/02_Output/'):
    os.makedirs(pathname + '/02_Output/')
    print("Folder /02_Output was created")
#if not os.path.exists(pathname + '/Output/ClusterImg/'):
#    os.makedirs(pathname + '/Output/ClusterImg/')
#    print("Folder /Output/ClusterImg/ was created")

# READ All JSON in Current Folder and join to list
#partnum = 0
guid_list = set() #global list of guids
count_glob = 0
partcount = 0
#filenameprev = ""
if (DSource == "fromFlickr_CSV"):
    filelist = glob('01_Input/*.txt')
    timestamp_columnNameID = 8 #DateTaken
    GMTTimetransform = 0
    guid_columnNameID = 5 #guid   
    Sourcecode = 2
    quoting_opt = csv.QUOTE_NONE
elif (DSource == "fromInstagram_PGlbsnEmoji"):
    filelist = glob('01_Input/*.csv')
    timestamp_columnNameID = 7 #DateTaken
    GMTTimetransform = 0    
    guid_columnNameID = 2 #guid    
    Sourcecode = 1
    quoting_opt = csv.QUOTE_ALL
elif (DSource == "fromSensorData_InfWuerz"):
    filelist = glob('01_Input/*.csv')
    timestamp_columnNameID = 2 #DateTaken
    GMTTimetransform = 0    
    guid_columnNameID = 1 #guid    
    Sourcecode = 11
    quoting_opt = csv.QUOTE_NONE
else:
    sys.exit("Source not supported yet.")

print('\n')
print_store_log("########## STEP 1 of 6: Data Cleanup ##########")
if (len(filelist) == 0):
    sys.exit("No *.json/csv/txt files found.")
else:
    inputtext = input("Files to process: " + str(len(filelist)) + ". \nOptional: Enter a Number for the variety of Tags to process (Default is 1000)\nPress Enter to proceed.. \n")
if inputtext == "" or not inputtext.isdigit():
    tmax = 1000
else:
    tmax = int(inputtext)
   
skippedCount = 0
appendToAlreadyExist = False
count_non_geotagged = 0
count_outside_shape = 0
count_tags_global = 0
count_tags_skipped = 0
shapeFileExcludelocIDhash = set()
shapeFileIncludedlocIDhash  = set()

#initialize global variables for analysis bounds (lat, lng coordinates)
limLatMin = None
limLatMax = None
limLngMin = None
limLngMax = None
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
LocationsPerUserID_dict = defaultdict(set)
UserLocationTagList_dict = defaultdict(set)
UserLocationWordList_dict = defaultdict(set)
UserLocationsFirstPhoto_dict = defaultdict(set)

#UserDict_TagCounters = defaultdict(set)
UserDict_TagCounters_global = defaultdict(set)
#UserIDsPerLocation_dict = defaultdict(set)
#PhotoLocDict = defaultdict(set)
distinctLocations_set = set()
count_loc = 0
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
        if (DSource == "fromInstagram_LocMedia_CSV" or DSource == "fromInstagram_UserMedia_CSV" or DSource == "fromFlickr_CSV" or DSource == "fromInstagram_PGlbsnEmoji" or DSource == "fromSensorData_InfWuerz"):
            photolist = csv.reader(f, delimiter=',', quotechar='"', quoting=quoting_opt) #QUOTE_NONE is important because media saved from php/Flickr does not contain any " check; only ',' are replaced
            next(photolist, None)  # skip headerline
        elif (DSource == "fromInstagram_HashMedia_JSON"):
            photolist = photolist + json.loads(f.read())
        #PhotosPerDayLists = defaultdict(list)
        #keyCreatedHash = set()     
        for item in photolist:
            if (DSource == "fromInstagram_LocMedia_CSV"):
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
                        if shapefileIntersect:
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
            elif DSource == "fromInstagram_UserMedia_CSV":
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
                        if shapefileIntersect:
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
            elif DSource == "fromFlickr_CSV":
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
                    photo_tags = set(filter(None, item[11].lower().split(";"))) #filter empty strings from photo_tags list and convert to set (hash) with unique values
                    #Filter tags based on two stoplists
                    photo_tags_filtered = set()
                    for tag in photo_tags:
                        count_tags_global += 1
                        #exclude numbers and those tags that are in SortOutAlways_set
                        if tag.isdigit() or tag in SortOutAlways_set:
                            count_tags_skipped += 1
                            continue
                        for inStr in SortOutAlways_inStr_set:
                            if inStr in tag:
                                count_tags_skipped += 1
                                break
                        else:
                            photo_tags_filtered.add(tag)
                    photo_tags = photo_tags_filtered
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
            elif (DSource == "fromInstagram_HashMedia_JSON"):
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
                    if shapefileIntersect:
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
            elif DSource == "fromInstagram_PGlbsnEmoji":
                if len(item) < 15:
                    #skip
                    skippedCount += 1
                    continue
                else:
                    photo_source = Sourcecode #LocMediaCode
                    photo_guid = item[1] #guid
                    photo_userid = item[7] #guid
                    photo_owner = ""#item[1] ##!!!
                    photo_shortcode = item[18]
                    photo_uploadDate = item[8] #guid
                    photo_idDate = photo_uploadDate #use upload date as sorting ID
                    photo_caption = item[9]
                    photo_likes = item[13]
                    #photo_tags = ";" + item[11] + ";"
                    tags_filtered = def_functions.extract_emojis(photo_caption)
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
            elif DSource == "fromSensorData_InfWuerz":
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
                        #exclude numbers and those tags that are in SortOutAlways_set
                        if tag.isdigit() or tag in SortOutAlways_set:
                            count_tags_skipped += 1
                            continue
                        for inStr in SortOutAlways_inStr_set:
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
            wordlist = [word for word in removeSpecialChars.split(' ') if len(word) > 2]  #first replace specia characters in caption, then split by space-character
            UserLocationWordList_dict[photo_locIDUserID] |= set(wordlist) #union words per userid/unique location              
            count_glob += 1
            
            ##Calculate toplists
            if photo_tags:
                UserDict_TagCounters_global[photo_userid].update(photo_tags) #add tagcount of this media to overall tagcount or this user, initialize counter for user if not already done 
            print("Cleaned output to " + "%02d" % (count_loc,)  + " photolocations from " + "%02d" % (count_glob,)+ " (File " + str(partcount) + " of " + str(len(filelist)) + ") - Skipped Media: " + str(skippedCount) + " - Skipped Tags: " + str(count_tags_skipped) +" of " + str(count_tags_global), end='\r')
            
log_texts_list.append("Cleaned output to " + "%02d" % (count_loc,)  + " photolocations from " + "%02d" % (count_glob,)+ " (File " + str(partcount) + " of " + str(len(filelist)) + ") - Skipped Media: " + str(skippedCount) + " - Skipped Tags: " + str(count_tags_skipped) +" of " + str(count_tags_global))
total_distinct_locations = len(distinctLocations_set)
print_store_log("\nTotal distinct locations: " + str(total_distinct_locations))
#boundary:
print_store_log("Bounds are: Min " + str(float(limLngMin)) + " " + str(float(limLatMin)) + " Max " + str(float(limLngMax)) + " " + str(float(limLatMax)))
#cleanedPhotoList = []

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
                          int(photo[8]),#photo_views = 9
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
            ##optional Write Cleaned Data to CSV/TXT
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
            cleanedPhotoDict[cleanedPhotoLocation.photo_guid] = cleanedPhotoLocation
now = time.time()
print_store_log("########## STEP 2 of 6: Tag Ranking ##########")
overallNumOfUsersPerTag_global = collections.Counter()
for user_key, taghash in UserDict_TagCounters_global.items():
    #taghash contains unique values (= strings) for each user, thus summing up these taghashes counts each user only once per tag
    overallNumOfUsersPerTag_global.update(taghash)


topTagsList = overallNumOfUsersPerTag_global.most_common(tmax)
#remove all tags that are used by less than two photographers
if removeLongTail is True:
    indexMin = next((i for i, (t1, t2) in enumerate(topTagsList) if t2 < 2), None)
    if indexMin:
        lenBefore = len(topTagsList)
        del topTagsList[indexMin:]
        lenAfter = len(topTagsList)
        tmax = lenAfter
        if not lenBefore == lenAfter:
            print("Filtered " + str(lenBefore - lenAfter) + " Tags that were only used by less than 2 users.")

    
#optional write toptags to file
toptags = ''.join("%s,%i" % v + '\n' for v in topTagsList)
with open("02_Output/Output_toptags.txt", 'w', encoding="utf8") as file: #overwrite
    file.write(toptags)

print_store_log("########## STEP 3 of 6: Tag Location Clustering ##########")
#prepare some variables
tnum = 0
first = True
label_size = 10
#plt.rcParams['xtick.labelsize'] = label_size
#plt.rcParams['ytick.labelsize'] = label_size 
plot_kwds = {'alpha' : 0.5, 's' : 10, 'linewidths':0}
sys.stdout.flush()
proceedClusting = False

distY = 0
distX = 0
imgRatio = 0

#Optional: set global plotting bounds
#plt.gca().set_xlim([limXMin, limXMax])
#plt.gca().set_ylim([limYMin, limYMax])
cleanedPhotoList = list(cleanedPhotoDict.values())
df = pd.DataFrame(cleanedPhotoList)
points = df.as_matrix(['lng','lat'])
limYMin = np.min(points.T[1])       
limYMax = np.max(points.T[1])    
limXMin = np.min(points.T[0])       
limXMax = np.max(points.T[0])
bound_points_shapely = geometry.MultiPoint([(limXMin, limYMin), (limXMax, limYMax)])
distYLat = limYMax - limYMin
distXLng = limXMax - limXMin
#distYLat = def_functions.haversine(limXMin,limYMax,limXMin,limYMin)
#distXLng = def_functions.haversine(limXMax,limYMin,limXMin,limYMin)
#imgRatio = distXLng/(distYLat*2)
imgRatio = distXLng/(distYLat*2) 
distY = def_functions.haversine(limXMin, limYMin, limXMin, limYMax)
distX = def_functions.haversine(limXMin, limYMin, limXMax, limYMin) 
clusterTreeCuttingDist = (min(distX,distY)/100)*7 #4% of research area width/height (max) = default value #223.245922725 #= 0.000035 radians dist

#print("distYLat DDegrees: " + str(limYMax - limYMin) + " distXLng DDegrees: " + str(limXMax - limXMin) + " Bsp:" + str(points[0]))
#print("DDegree Buffer dist: " + str(max(distXLng,distYLat)/200) + " Cluster Dist: " + str(clusterTreeCuttingDist) + " Alpha: " + str(clusterTreeCuttingDist*10))
#input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
#input_lat_center = bound_points_shapely.centroid.coords[0][1]
#epsg_code = def_functions.convert_wgs_to_utm(input_lon_center, input_lat_center)
#crs_wgs = pyproj.Proj(init='epsg:4326')
#crs_proj = pyproj.Proj(init='epsg:{0}'.format(epsg_code))

#x, y = pyproj.transform(crs_wgs, crs_proj, Decimal(points[0][0]), Decimal(points[0][1]))
#print("distY Meters: " + str(distY) + " distX Meters: " + str(distX) + " Bsp:" + str(x) + " " + str(y))
#print("Meters Buffer dist: " + str(clusterTreeCuttingDist/4) + " Cluster Dist: " + str(clusterTreeCuttingDist) + " Alpha: " + str(clusterTreeCuttingDist*100))
#Tkinter Stuff
#####################################################################################################################################################
#def center(win):
#    """
#    centers a tkinter window
#    :param win: the root or Toplevel window to center
#    """
#    win.update_idletasks()
#    width = win.winfo_width()
#    frm_width = win.winfo_rootx() - win.winfo_x()
#    win_width = width + 2 * frm_width
#    height = win.winfo_height()
#    titlebar_height = win.winfo_rooty() - win.winfo_y()
#    win_height = height + titlebar_height + frm_width
#    x = win.winfo_screenwidth() // 2 - win_width // 2
#    y = win.winfo_screenheight() // 2 - win_height // 2
#    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
#    win.deiconify()
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
        
app = App()
#necessary override for error reporting during tkinter mode
def report_callback_exception(self, exc, val, tb):
    showerror("Error", message=str(val))
tk.Tk.report_callback_exception = report_callback_exception


#the following code part is a bit garbled due to using TKinter interface
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################

#definition of global vars for interface and graph design
canvasWidth = 1320
canvasHeight = 440
floaterX = 0
floaterY = 0
#Cluster preparation
sns.set_context('poster')
sns.set_style('white')
#sns.set_color_codes()
#matplotlib.style.use('ggplot')
plt.style.use('ggplot')
graphFrame = None
lastselectionList = []
currentDisplayTag = None
genPreviewMap = tk.IntVar(value = 0)
createMinimumSpanningTree = False
autoselectClusters = False
#definition of global figure for reusing windows
fig1 = None
fig2 = None
fig3 = None
fig4 = None

def quitTkinter():
    #exits Tkinter gui and continues with code execution after mainloop()
    #global app
    #app.floater.destroy()
    #tkinter.messagebox.showinfo("Closing App", "Closing App")
    #plt.quit()
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

def fit_cluster(clusterer, data):
    clusterer.fit(data)
    return clusterer
def cluster_tag(toptag=None,preview=None,silent=None):
    if preview is None:
        preview = False
    if silent is None:
        silent = False        
    global first
    global currentDisplayTag
    global limYMin, limYMax, limXMin, limXMax, imgRatio, floaterX, floaterY
    global fig1, fig2, fig3, fig4
    #global graphFrame
    #if graphFrame: #if 
    #    graphFrame.destroy()
    #graphFrame = tk.Frame(app.floater)
    #canvas = tk.Canvas(graphFrame, width=canvasWidth, height=canvasHeight, highlightthickness=0,background="gray7")
    #l = tk.Label(canvas, text="Preview Map", background="gray7",fg="gray80",font="Arial 10 bold")
    #l.pack()   
    selectedPhotoList_Guids, distinctLocalLocationCount = sel_photos(toptag[0],cleanedPhotoList)
    percentageOfTotalLocations = distinctLocalLocationCount/(total_distinct_locations/100)
    #tkinter.messagebox.showinfo("Num of clusters: ", "(" + str(tnum) + " of " + str(tmax) + ") Found " + str(len(selectedPhotoList)) + " photos for tag " + "'" + toptag[0] + "' (" + str(round(percentageOfTotalLocations,0)) + "% of total distinct locations in area)")
    if silent:
        print_store_log("(" + str(tnum) + " of " + str(tmax) + ") Found " + str(len(selectedPhotoList_Guids)) + " photos for tag " + "'" + toptag[0] + "' (" + str(round(percentageOfTotalLocations,0)) + "% of total distinct locations in area)", end=" ")

    
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
            async_result = pool.apply_async(fit_cluster, (clusterer, tagRadiansData))
            clusterer = async_result.get()
            #clusterer.fit(tagRadiansData)
            #updateNeeded = False

        if autoselectClusters:
            sel_labels = clusterer.labels_ #auto selected clusters
        else:
            sel_labels = clusterer.single_linkage_tree_.get_clusters(def_functions.getRadiansFromMeters(clusterTreeCuttingDist), min_cluster_size=2) #0.000035 without haversine: 223 m (or 95 m for 0.000015)

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
            plt.title('Cluster Preview ' + distText, fontsize=12,loc='center')
            #plt.title('Cluster Preview')
            #xmax = ax.get_xlim()[1]
            #ymax = ax.get_ylim()[1]
            noisyTxt = '{}/{}'.format(mask_noisy.sum(), len(mask_noisy))
            plt.text(limXMax, limYMax,str(number_of_clusters) + ' Cluster (Noise: ' + noisyTxt + ')',fontsize=10,horizontalalignment='right',verticalalignment='top',fontweight='bold')
        else:
            plt.scatter(points.T[0], points.T[1], c=sel_colors, **plot_kwds)
            fig1 = plt.figure(num=1,figsize=(11, int(11*imgRatio)), dpi=80)
            fig1.canvas.set_window_title('Cluster Preview')
            plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
            distText = ''
            if autoselectClusters == False:
                distText = '@ ' + str(clusterTreeCuttingDist) +'m'  
            plt.title('Cluster Preview ' + distText, fontsize=12,loc='center')
            #xmax = fig1.get_xlim()[1]
            #ymax = fig1.get_ylim()[1]
            noisyTxt = '{} / {}'.format(mask_noisy.sum(), len(mask_noisy))
            plt.text(limXMax, limYMax,str(number_of_clusters) + ' Clusters (Noise: ' + noisyTxt + ')',fontsize=10,horizontalalignment='right',verticalalignment='top',fontweight='bold')
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
            y = def_functions.getRadiansFromMeters(clusterTreeCuttingDist)
            xmin = ax.get_xlim()[0]
            xmax = ax.get_xlim()[1]
            line, = ax.plot([xmin, xmax], [y, y], color='k', label='Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')
            line.set_label('Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')             
            ax.legend(fontsize=10)
            vals = ax.get_yticks()
            ax.set_yticklabels(['{:3.1f}m'.format(def_functions.getMetersFromRadians(x)) for x in vals])
        else:
            plt.figure(3).canvas.set_window_title('Single Linkage Tree')
            fig3 = clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=max(50,min(number_of_clusters*10,256)))
            plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
            plt.title('Single Linkage Tree', fontsize=12,loc='center')
            #tkinter.messagebox.showinfo("messagr", str(type(fig3)))
            #plot cutting distance
            y = def_functions.getRadiansFromMeters(clusterTreeCuttingDist)
            xmin = fig3.get_xlim()[0]
            xmax = fig3.get_xlim()[1]
            line, = fig3.plot([xmin, xmax], [y, y], color='k', label='Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')
            line.set_label('Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')
            fig3.legend(fontsize=10)
            vals = fig3.get_yticks()
            fig3.set_yticklabels(['{:3.1f}m'.format(def_functions.getMetersFromRadians(x)) for x in vals])     
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
                plt.title('Minimum Spanning Tree @ ' + str(clusterTreeCuttingDist) +'m', fontsize=12,loc='center')
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
                plt.title('Minimum Spanning Tree @ ' + str(clusterTreeCuttingDist) +'m', fontsize=12,loc='center')
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
    global tkScalebar
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
    #plt.close('all')
def delete(listbox):
    global topTagsList
    global lastselectionList
    lastselectionList = []
    # Delete from Listbox
    selection = listbox.curselection()
    #tkinter.messagebox.showinfo("listbox.curselection()", str(selection))
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
#if DSource == "fromInstagram_PGlbsnEmoji":
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
        listbox.insert(tk.END, "{} ({} user)".format(item[0], item[1]))
    except tk.TclError:
        emoji = unicode_name(item[0]) #def_functions.with_surrogates()
        listbox.insert(tk.END, "{} ({} user)".format(emoji, item[1]))
canvas.pack(fill='both',padx=0, pady=0)
listboxFrame.pack(fill='both',padx=0, pady=0)
buttonsFrame = tk.Frame(app.floater)
canvas = tk.Canvas(buttonsFrame, width=150, height=200, highlightthickness=0,background="gray7")
b = tk.Button(canvas, text = "Remove Tag(s)", command = lambda: delete(listbox), background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
b.pack(padx=10, pady=10)
c = tk.Checkbutton(canvas, text="Map Tags", variable=genPreviewMap,background="gray7",fg="gray80",borderwidth=0,font="Arial 10 bold")
c.pack(padx=10, pady=10)
tkScalebar = tk.Scale(canvas, from_=(clusterTreeCuttingDist/100), to=(clusterTreeCuttingDist*2), orient=tk.HORIZONTAL,resolution=0.1,command=change_clusterDist,length=300,label="Cluster Cut Distance (in Meters)",background="gray20",borderwidth=0,fg="gray80",font="Arial 10 bold")
tkScalebar.set(clusterTreeCuttingDist)#(clusterTreeCuttingDist*10) - (clusterTreeCuttingDist/10)/2) #set position of slider to center
tkScalebar.pack()
b = tk.Button(canvas, text = "Cluster Preview", command=cluster_currentDisplayTag, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
b.pack(padx=10, pady=10)
b = tk.Button(canvas, text = "Proceed", command=proceedWithCluster, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
b.pack(padx=10, pady=10)
b = tk.Button(canvas, text = "Quit", command=quitTkinter, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
b.pack(padx=10, pady=10)
canvas.pack(fill='both',padx=0, pady=0)
buttonsFrame.pack(fill='both',padx=0, pady=0)

#end of tkinter main loop
#
app.mainloop()
plt.close("all")
from descartes import PolygonPatch
def plot_polygon(polygon):
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)
    margin = .3
    x_min, y_min, x_max, y_max = polygon.bounds
    ax.set_xlim([x_min-margin, x_max+margin])
    ax.set_ylim([y_min-margin, y_max+margin])
    patch = PolygonPatch(polygon, fc='#999999',
                         ec='#000000', fill=True,
                         zorder=-1)
    ax.add_patch(patch)
    return fig
from shapely.ops import cascaded_union, polygonize
from scipy.spatial import Delaunay
import math
from math import sqrt
def alpha_shape(points, alpha):
    """
    Alpha Shapes Code by KEVIN DWYER
    see http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/
    Compute the alpha shape (concave hull) of a set
    of points.
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull
    def add_edge(edges, edge_points, coords, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            return
        edges.add( (i, j) )
        edge_points.append(coords[ [i, j] ])
    coords = np.array([point.coords[0]
                       for point in points])
    
    #print(str(len(coords)))
    tri = Delaunay(coords)#,qhull_o}ptions = 'QJ') #To avoid this error, you can joggle the data by specifying the 'QJ' option to the DELAUNAY function. https://de.mathworks.com/matlabcentral/answers/94438-why-does-the-delaunay-function-in-matlab-7-0-r14-produce-an-error-when-passed-colinear-points?s_tid=gn_loc_drop
    #tri = Delaunay(coords,{'QJ'}) #Version 3.1 added triangulated output ('Qt'). It should be used for Delaunay triangulations instead of using joggled input ('QJ').
    edges = set()
    edge_points = []
    # loop over triangles:
    # ia, ib, ic = indices of corner points of the
    # triangle
    for ia, ib, ic in tri.vertices:
        pa = coords[ia]
        pb = coords[ib]
        pc = coords[ic]
        # Lengths of sides of triangle
        a = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
        b = math.sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
        c = math.sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)
        # Semiperimeter of triangle
        s = (a + b + c)/2.0
        # Area of triangle by Heron's formula
        try:
            area = math.sqrt(s*(s-a)*(s-b)*(s-c))
        except ValueError:
            return False
        if area == 0:
            return False
        circum_r = a*b*c/(4.0*area)
        # Here's the radius filter.
        #print circum_r
        if circum_r < 1.0/alpha:
            add_edge(edges, edge_points, coords, ia, ib)
            add_edge(edges, edge_points, coords, ib, ic)
            add_edge(edges, edge_points, coords, ic, ia)
    m = geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))
    return cascaded_union(triangles)#, edge_points
    #return geometry.polygon.asPolygon(edge_points,holes=None)

bdist = 0
noClusterPhotos_perTag_DictOfLists = defaultdict(list)
clustersPerTag = defaultdict(list)
if proceedClusting:
    #Proceed with clustering all tags
    crs_wgs = pyproj.Proj(init='epsg:4326') #data always in lat/lng WGS1984
    if overrideCRS is None:
        #Calculate best UTM Zone SRID/EPSG Code
        input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
        input_lat_center = bound_points_shapely.centroid.coords[0][1]
        epsg_code = def_functions.convert_wgs_to_utm(input_lon_center, input_lat_center)
        crs_proj = pyproj.Proj(init='epsg:{0}'.format(epsg_code))
    project = lambda x, y: pyproj.transform(pyproj.Proj(init='epsg:4326'), pyproj.Proj(init='epsg:{0}'.format(epsg_code)), x, y)
    #geom_proj = transform(project, alphaShapeAndMeta[0])
    
    tnum = 1
    for toptag in topTagsList:
        
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
        if not number_of_clusters == 0:
            print_store_log("--> " + str(number_of_clusters) + " cluster.")
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
            print_store_log("--> No cluster.")
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
    print_store_log("########## STEP 4 of 6: Generating Alpha Shapes ##########")
    #if (tnum % 50 == 0):#modulo: if division has no remainder, force update cmd output
    sys.stdout.flush()
    #for each cluster of points, calculate boundary shape and add statistics (HImpTag etc.)
    listOfAlphashapesAndMeta = []
    tnum = 1
    for toptag in topTagsList:
        tnum += 1
        clusterPhotoGuidList = clustersPerTag.get(toptag[0], None)
        #print(toptag[0])
        if clusterPhotoGuidList:
            #we define a new list of Temp Alpha Shapes outside the loop, so that it is not overwritten each time
            listOfAlphashapesAndMeta_tmp = []
            #points = []
            for photo_guids in clusterPhotoGuidList:
                photos = [cleanedPhotoDict[x] for x in photo_guids]
                photoCount = len(photo_guids)
                uniqueUserCount = len(set([photo.userid for photo in photos]))
                sumViews = sum([photo.photo_views for photo in photos])
                #calculate different weighting formulas
                #weightsv1 = 1+ photoCount *(sqrt(1/( photoCount / uniqueUserCount )**3)) #-> Standard weighting formula (x**y means x raised to the power y); +1 to UserCount: prevent 1-2 Range from being misaligned
                #weightsv2 = 1+ photoCount *(sqrt(1/( photoCount / uniqueUserCount )**2))
                weightsv1 = photoCount *(sqrt(1/( photoCount / (uniqueUserCount+1) )**3)) #-> Standard weighting formula (x**y means x raised to the power y); +1 to UserCount: prevent 1-2 Range from being misaligned
                weightsv2 = photoCount *(sqrt(1/( photoCount / (uniqueUserCount+1) )**2)) #-> less importance on User_Count in correlation to photo count [Join_Count]; +1 to UserCount: prevent 1-2 Range from being misaligned
                weightsv3 = sqrt((photoCount+(2*sqrt(photoCount)))*2) #-> Ignores User_Count, this will emphasize individual and very active users                  
                #points = [geometry.Point(photo.lng, photo.lat)
                #          for photo in photos]
                #instead of lat/lng for each photo, we use photo_locID to identify a list of distinct locations 
                distinctLocations = set([photo.photo_locID
                          for photo in photos])               
                #simple list comprehension without projection:
                #points = [geometry.Point(Decimal(location.split(':')[1]), Decimal(location.split(':')[0]))
                #          for location in distinctLocations]
                points = [geometry.Point(pyproj.transform(crs_wgs, crs_proj, Decimal(location.split(':')[1]), Decimal(location.split(':')[0])))
                          for location in distinctLocations]
                point_collection = geometry.MultiPoint(list(points))
                result_polygon = None
                
                if len(points) >= 5:
                    if len(points) < 10:
                        result_polygon = point_collection.convex_hull #convex hull
                        result_polygon = result_polygon.buffer(clusterTreeCuttingDist/4,resolution=3)
                        shapetype = "between 5 and 10 points_conexHull"
                        #result_polygon = result_polygon.buffer(min(distXLng,distYLat)/100,resolution=3)
                    else:
                        if len(points) > 100:
                            startalpha = 1000000
                        else:
                            startalpha = 10000
                        result_polygon = alpha_shape(points,alpha=clusterTreeCuttingDist/startalpha) #concave hull/alpha shape /50000
                        shapetype = "Initial Alpha Shape + Buffer"
                        if type(result_polygon) is geometry.multipolygon.MultiPolygon or isinstance(result_polygon, bool):
                            #repeat generating alpha shapes with smaller alpha value if Multigon is generated
                            #smaller alpha values mean less granularity of resulting polygon
                            #but too large alpha may result in empty polygon
                            #(this branch is sometimes executed for larger scales)
                            for i in range(1,6):
                                #try decreasing alpha
                                alpha = startalpha + (startalpha * (i**i)) #** means cube
                                result_polygon = alpha_shape(points,alpha=clusterTreeCuttingDist/alpha)#/100000
                                if not type(result_polygon) is geometry.multipolygon.MultiPolygon and not isinstance(result_polygon, bool):
                                    shapetype = "Multipolygon Alpha Shape /" + str(alpha)
                                    break
                            if type(result_polygon) is geometry.multipolygon.MultiPolygon or isinstance(result_polygon, bool):
                                #try increasing alpha
                                for i in range(1,6):
                                    #try decreasing alpha
                                    alpha = startalpha / (i*i)
                                    result_polygon = alpha_shape(points,alpha=clusterTreeCuttingDist/alpha)#/100000
                                    if not type(result_polygon) is geometry.multipolygon.MultiPolygon and not isinstance(result_polygon, bool):
                                        shapetype = "Multipolygon Alpha Shape /" + str(alpha)
                                        break                            
                            if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                                shapetype = "Multipolygon Alpha Shape -> Convex Hull"
                                #if still of type multipolygon, try to remove holes and do a convex_hull
                                result_polygon = result_polygon.convex_hull
                            #OR: in case there was a problem with generating alpha shapes (circum_r = a*b*c/(4.0*area) --> ZeroDivisionError: float division by zero) 
                            #this branch is rarely executed for large point clusters where alpha is perhaps set too small
                            elif isinstance(result_polygon, bool) or result_polygon.is_empty:
                                shapetype = "BoolAlpha -> Fallback to PointCloud Convex Hull"
                                result_polygon = point_collection.convex_hull #convex hull                        
                        #Finally do a buffer to smooth alpha
                        result_polygon = result_polygon.buffer(clusterTreeCuttingDist/4,resolution=3)
                        #result_polygon = result_polygon.buffer(min(distXLng,distYLat)/100,resolution=3)
                elif 2 <= len(points) < 5:
                    shapetype = "between 2 and 5 points_buffer"
                    #calc distance between points http://www.mathwarehouse.com/algebra/distance_formula/index.php
                    #bdist = math.sqrt((points[0].coords.xy[0][0]-points[1].coords.xy[0][0])**2 + (points[0].coords.xy[1][0]-points[1].coords.xy[1][0])**2)
                    #print(str(bdist))
                    result_polygon = point_collection.buffer(clusterTreeCuttingDist/4,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                    result_polygon = result_polygon.convex_hull
                    #result_polygon = point_collection.buffer(min(distXLng,distYLat)/100,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                elif len(points)==1 or type(result_polygon) is geometry.point.Point or result_polygon is None:
                    shapetype = "1 point cluster"
                    result_polygon = point_collection.buffer(clusterTreeCuttingDist/4,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                    #result_polygon = point_collection.buffer(min(distXLng,distYLat)/100,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                #final check for multipolygon
                if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                    #usually not executed
                    result_polygon = result_polygon.convex_hull
                #Geom, Join_Count, Views,  COUNT_User,ImpTag,TagCountG,HImpTag
                if result_polygon is not None and not result_polygon.is_empty:
                    listOfAlphashapesAndMeta_tmp.append((result_polygon,photoCount,sumViews,uniqueUserCount,str(toptag[0]),toptag[1],weightsv1,weightsv2,weightsv3,shapetype))
            if len(listOfAlphashapesAndMeta_tmp) > 0:
                #Sort on Weights1 Formula
                listOfAlphashapesAndMeta_tmp = sorted(listOfAlphashapesAndMeta_tmp,key=lambda x: -x[6])
                listOfAlphashapesAndMeta.extend(listOfAlphashapesAndMeta_tmp)
                    #plot_polygon(result_polygon)
                    #plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                    #plt.gca().set_xlim([float(limLngMin), float(limLngMax)]) 
                    #plt.gca().set_ylim([float(limLatMin), float(limLatMax)])
                    #plt.plot(x,y,'o',ms=5)
                    #plt.waitforbuttonpress()
                    #plt.close()
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
                    listOfAlphashapesAndMeta.append((result_polygon,1,single_photo.photo_views,1,str(toptag[0]),toptag[1],1,1,1,shapetype))   
    print_store_log(str(len(listOfAlphashapesAndMeta)) + " Alpha Shapes. Done.")
    ##Output Boundary Shapes in merged Shapefile##
    print_store_log("########## STEP 5 of 6: Writing Results to Shapefile ##########")
    
   ##Calculate best UTM Zone SRID/EPSG Code
   #input_lon_center = bound_points_shapely.centroid.coords[0][0] #True centroid (coords may be multipoint)
   #input_lat_center = bound_points_shapely.centroid.coords[0][1]
   #epsg_code = def_functions.convert_wgs_to_utm(input_lon_center, input_lat_center)
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
                       'shapetype': 'str'},
                       #'EmojiName': 'str'},
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
    with fiona.open('02_Output/allTagClusters.shp', mode='w', encoding='utf-8', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
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
            weight1_normalized = weightsv1_mod_a * alphaShapeAndMeta[6] + weightsv1_mod_b
            weight2_normalized = weightsv2_mod_a * alphaShapeAndMeta[7] + weightsv2_mod_b
            weight3_normalized = weightsv3_mod_a * alphaShapeAndMeta[8] + weightsv3_mod_b
            idx += 1
            #project data
            #geom_proj = transform(project, alphaShapeAndMeta[0])
            #c.write({
            #    'geometry': geometry.mapping(geom_proj),            
            c.write({
                'geometry': geometry.mapping(alphaShapeAndMeta[0]),
                'properties': {'Join_Count': alphaShapeAndMeta[1], 
                               'Views': alphaShapeAndMeta[2],
                               'COUNT_User': alphaShapeAndMeta[3],
                               'ImpTag': alphaShapeAndMeta[4],
                               'TagCountG': alphaShapeAndMeta[5],
                               'HImpTag': HImP,
                               'Weights': weight1_normalized,
                               'WeightsV2': weight2_normalized,
                               'WeightsV3': weight3_normalized,
                               'shapetype': alphaShapeAndMeta[9]},
                               #'EmojiName': emoName},
            })

    print_store_log("########## STEP 6 of 6: Calculating Overall Photo Location Clusters ##########")

    selectedPhotoList_Guids = []
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
        async_result = pool.apply_async(fit_cluster, (clusterer, tagRadiansData))
        clusterer = async_result.get()
    clusters = clusterer.single_linkage_tree_.get_clusters(def_functions.getRadiansFromMeters(clusterTreeCuttingDist/8), min_cluster_size=2)
    listOfPhotoClusters = []
    numpy_selectedPhotoList_Guids = np.asarray(selectedPhotoList_Guids)
    mask_noisy = (clusters == -1)
    number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
    print_store_log("--> " + str(number_of_clusters) + " Photo cluster.")
    tnum += 1
    photo_num = 0
    #clusternum_photolist = zip(clusters,selectedPhotoList)
    #clusterPhotosList = [[] for x in range(number_of_clusters)]
    clusterPhotosGuidsList = []
    for x in range(number_of_clusters):
        currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
        clusterPhotosGuidsList.append(currentClusterPhotoGuids)
    noClusterPhotos = list(numpy_selectedPhotoList_Guids[clusters==-1])   
    clusterPhotosGuidsList.sort(key=len,reverse=True)
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
    noclusterphotos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
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
    with fiona.open('02_Output/allPhotoClusters.shp', mode='w', driver='ESRI Shapefile', schema=schema,crs=from_epsg(epsg_code)) as c:
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
    print()
    difference = int(later - now)
    log_texts_list.append("\n" + "Done." + "\n{:0>2} Hours {:0>2} Minutes and {:05.2f} Seconds".format(int(hours),int(minutes),seconds) + " passed.")
    with open(log_file, "w", encoding='utf-8') as logfile_a:
        for logtext in log_texts_list:
            logfile_a.write(logtext)        
    print("\n" + "Done." + "\n{:0>2} Hours {:0>2} Minutes and {:05.2f} Seconds".format(int(hours),int(minutes),seconds) + " passed.")
    input("Press any key to continue...")
else:
    print("\n" + "User abort.")