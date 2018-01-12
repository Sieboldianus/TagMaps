#!/usr/bin/env python
# coding: utf8
# iExtractAllGeoMedia

"""
generateTagClusters.py

- will read in geotagged (lat/lng) decimal degree point data
- will generate HDBSCAN Cluster Hierarchy
- will output Alpha Shapes/Delauney for cluster cut at specific distance
"""

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
import def_functions
import datetime


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
from time import sleep



##Needed for Shapefilestuff

#enable for map display
#from mpl_toolkits.basemap import Basemap
#from PIL import Image

import fiona #Fiona needed for reading Shapefile
from fiona.crs import from_epsg
import shapely.geometry as geometry
#from shapely.geometry import Polygon
#from shapely.geometry import shape
#from shapely.geometry import Point
from decimal import Decimal

__author__      = "Alexander Dunkel"
__license__   = "GNU GPLv3"
__version__ = "0.9.1"

######################    
####config section####
######################
log_file = "Output/log.txt"

##Load Filterlists
SortOutAlways_file = "SortOutAlways.txt"
SortOutAlways_inStr_file = "SortOutAlways_inStr.txt"
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
parser.add_argument("source")     # naming it "source"
args = parser.parse_args()    # returns data from the options specified (source)
DSource = args.source

pathname = os.getcwd()
if not os.path.exists(pathname + '/Output/'):
    os.makedirs(pathname + '/Output/')
    print("Folder /Output was created")
if not os.path.exists(pathname + '/Output/ClusterImg/'):
    os.makedirs(pathname + '/Output/ClusterImg/')
    print("Folder /Output/ClusterImg/ was created")

# READ All JSON in Current Folder and join to list
#partnum = 0
guid_list = set() #global list of guids
count_glob = 0
partcount = 0
#filenameprev = ""
if (DSource == "fromFlickr_CSV"):
    filelist = glob('Input/*.txt')
    timestamp_columnNameID = 8 #DateTaken
    GMTTimetransform = 0
    guid_columnNameID = 5 #guid   
    Sourcecode = 2
else:
    sys.exit("Source not supported yet.")

print('\n')
print("########## STEP 1 of 5: Data Cleanup ##########")
if (len(filelist) == 0):
    sys.exit("No *.json/csv files found.")
else:
    print("Files to process: " + str(len(filelist)))
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
    filename = "Output/" + os.path.basename(file_name)
    with open(filename, 'a', encoding='utf8') as file:
        file.write("ID_Date,SOURCE,Latitude,Longitude,PhotoID,Owner,UserID,Name,URL,DateTaken,UploadDate,Views,Tags,MTags,Likes,Comments,Shortcode,Type,LocName,LocID" + '\n')
        file.write('"2000-01-01 00:00:00","TESTLINE","43.2544706","28.023467","24PHOTOID3534","testowner","812643S9812644","testcaption","https://scontent.cdninstagram.com/t/s640x640/22344798_1757535311005731_6649353052090269696_n.jpg","2000-01-01 00:00:00","2000-01-01 00:00:00","22",";blacksea;romania;ig;seaside;mareaneagra;travel;getfit;trip;travelog;sun;beachy;avenit;mytinyatlas;islandhopping;flashesofdelight;beachvibes;beautiful;waves;barbershop;sea;love;photooftheday;picoftheday;vsco;vscocam;snapshot;instatravel;instamood;ich;io;summer;photography;europa;happy;end;je;lacrusesc;contrejour;chiaroscuro;morninsunshine;treadmill;gainz;workout;sunshine;getstrong;eu;rumunsko;calatoriecupasiune;superduper;selfie;lazyday;","TESTMTAG","50","25","BaE5OZpgfRu","Image","Sunshine Boulevard Sunshine Boulevard Sunshine Bou","821648SS21642"' +'\n')

    photolist = [] # clear photolist for every file
    ##f_count += 1
    ##if f_count > 25:
    ##    break
    #    guid_list.clear() #duplicate detection only for last 500k items
    with open(file_name, newline='', encoding='utf8') as f: # On input, if newline is None, universal newlines mode is enabled. Lines in the input can end in '\n', '\r', or '\r\n', and these are translated into '\n' before being returned to the caller.
        partcount += 1
        if (DSource == "fromInstagram_LocMedia_CSV" or DSource == "fromInstagram_UserMedia_CSV" or DSource == "fromFlickr_CSV"):
            photolist = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE) #QUOTE_NONE is important because media saved from php/Flickr does not contain any " check; only ',' are replaced
            next(photolist, None)  # skip headerline
        elif (DSource == "fromInstagram_HashMedia_JSON"):
            photolist = photolist + json.loads(f.read())
        PhotosPerDayLists = defaultdict(list)
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
            
            #this code will union all tags of a single user for each location
            #further information is derived from the first omage for each user-location
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
            removeSpecialChars = photo_caption.translate ({ord(c): " " for c in "?.!/;:,[]()'-"})
            wordlist = [word for word in removeSpecialChars.split(' ') if len(word) > 2]  #first replace specia characters in caption, then split by space-character
            UserLocationWordList_dict[photo_locIDUserID] |= set(wordlist) #union words per userid/unique location              
            count_glob += 1
            
            ##Calculate toplists
            if photo_tags:
                UserDict_TagCounters_global[photo_userid].update(photo_tags) #add tagcount of this media to overall tagcount or this user, initialize counter for user if not already done 
            print("Cleaned output to " + "%02d" % (count_loc,)  + " photolocations from " + "%02d" % (count_glob,)+ " (File " + str(partcount) + " of " + str(len(filelist)) + ") - Skipped Media: " + str(skippedCount) + " - Skipped Tags: " + str(count_tags_skipped) +" of " + str(count_tags_global), end='\r')
            

total_distinct_locations = len(distinctLocations_set)
print("\nTotal distinct locations: " + str(total_distinct_locations))
#boundary:
print("Bounds are: Min " + str(float(limLngMin)) + " " + str(float(limLatMin)) + " Max " + str(float(limLngMax)) + " " + str(float(limLatMax)))
#cleanedPhotoList = []

#create structure for tuple with naming for easy referencing
cleanedPhotoLocation_tuple = namedtuple('cleanedPhotoLocation_tuple', 'source lat lng photo_guid photo_owner userid photo_caption photo_dateTaken photo_uploadDate photo_views photo_tags photo_thumbnail photo_mTags photo_likes photo_comments photo_shortcode photo_mediatype photo_locName photo_locID')
cleanedPhotoDict = defaultdict(cleanedPhotoLocation_tuple)
with open("Output/Output_cleaned.txt", 'w', encoding='utf8') as csvfile:
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
            #cleanedPhotoList.append(cleanedPhotoLocation)
            cleanedPhotoDict[cleanedPhotoLocation.photo_guid] = cleanedPhotoLocation

print("########## STEP 2 of 5: Tag Ranking ##########")
overallNumOfUsersPerTag_global = collections.Counter()
for user_key, taghash in UserDict_TagCounters_global.items():
    #taghash contains unique values (= strings) for each user, thus summing up these taghashes counts each user only once per tag
    overallNumOfUsersPerTag_global.update(taghash)
toptags = ''.join("%s,%i" % v + '\n' for v in overallNumOfUsersPerTag_global.most_common(1000))
with open("Output/Output_toptags.txt", 'w', encoding="utf8") as file: #overwrite
    file.write(toptags)

tmax = 1000
topTagsList = overallNumOfUsersPerTag_global.most_common(tmax)

print("########## STEP 3 of 5: Tag Location Clustering ##########")
#prepare some variables
tnum = 0
first = True
label_size = 10
#plt.rcParams['xtick.labelsize'] = label_size
#plt.rcParams['ytick.labelsize'] = label_size 
plot_kwds = {'alpha' : 0.5, 's' : 10, 'linewidths':0}
sys.stdout.flush()
proceedClusting = False
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
distY = 0
distX = 0
imgRatio = 0
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
distY = limYMax - limYMin
distX = limXMax - limXMin
imgRatio = distX/(distY*2) 
distY = def_functions.haversine(limXMin, limYMin, limXMin, limYMax)
distX = def_functions.haversine(limXMin, limYMin, limXMax, limYMin) 

clusterTreeCuttingDist = (distX/100)*4 #4% of research area width = default value #223.245922725 #= 0.000035 radians dist


#tkinter.messagebox.showinfo("messagr", str(distY))
#tkinter.messagebox.showinfo("messagr", str(distX))

#if first == True: #init
#    #calculate once boundary for all points
#    df = pd.DataFrame(cleanedPhotoList)
#    points = df.as_matrix(['lng','lat'])
#    limYMin = np.min(points.T[1])
#    limYMax = np.max(points.T[1])
#    limXMin = np.min(points.T[0])
#    limXMax = np.max(points.T[0])
#    #set global plotting bounds for matplotlib
#    plt.gca().set_xlim([limXMin, limXMax]) 
#    plt.gca().set_ylim([limYMin, limYMax])
#    #calculate imageRatio from distance covered
#    distY = limYMax - limYMin
#    distX = limXMax - limXMin
#    imgRatio = distX/(distY*2) #multiply by 2 because lat = 90 and lng = 180!
#    ws = app.winfo_screenwidth()
#    hs = app.winfo_screenheight()
#    floaterX = (ws/2) - (canvasWidth/2)
#    floaterY = (hs/2) - (canvasHeight/2)
#    #app.floater.geometry('+%d+%d' % (floaterX, floaterY))
#    #app.title("Select Cluster Distance")
#    first = False

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

def cluster_tag(toptag,preview=None,silent=None):
    if preview is None:
        preview = False
    if silent is None:
        silent = False        
    global first
    global currentDisplayTag
    global limYMin, limYMax, limXMin, limXMax, distY, distX, imgRatio, floaterX, floaterY
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
        print("(" + str(tnum) + " of " + str(tmax) + ") Found " + str(len(selectedPhotoList_Guids)) + " photos for tag " + "'" + toptag[0] + "' (" + str(round(percentageOfTotalLocations,0)) + "% of total distinct locations in area)", end=" ")
    #clustering
    selectedPhotoList = [cleanedPhotoDict[x] for x in selectedPhotoList_Guids]
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
        #minClusterSize = 2
        clusterer = hdbscan.HDBSCAN(min_cluster_size=minClusterSize,gen_min_span_tree=createMinimumSpanningTree,allow_single_cluster=True,min_samples=1)
        #clusterer = hdbscan.HDBSCAN(min_cluster_size=minClusterSize,gen_min_span_tree=True,min_samples=1)
        #clusterer = hdbscan.HDBSCAN(min_cluster_size=10,metric='haversine',gen_min_span_tree=False,allow_single_cluster=True)
        #clusterer = hdbscan.robust_single_linkage_.RobustSingleLinkage(cut=0.000035)
        #srsl_plt = hdbscan.robust_single_linkage_.plot()
        
        #Start clusterer on different thread to prevent GUI from freezing
        #See: http://stupidpythonideas.blogspot.de/2013/10/why-your-gui-app-freezes.html
        #https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
        if silent:
            #on silent command line operation, don't use multiprocessing
            clusterer = fit_cluster(clusterer,tagRadiansData)
        else:
            async_result = pool.apply_async(fit_cluster, (clusterer, tagRadiansData))
            clusterer = async_result.get()
            #clusterer.fit(tagRadiansData)
            #updateNeeded = False
        if autoselectClusters:
            sel_labels = clusterer.labels_ #auto selected clusters
        else:
            sel_labels = clusterer.single_linkage_tree_.get_clusters(getRadiansFromMeters(clusterTreeCuttingDist), min_cluster_size=2) #0.000035 without haversine: 223 m (or 95 m for 0.000015)

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
            y = getRadiansFromMeters(clusterTreeCuttingDist)
            xmin = ax.get_xlim()[0]
            xmax = ax.get_xlim()[1]
            line, = ax.plot([xmin, xmax], [y, y], color='k', label='Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')
            line.set_label('Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')             
            ax.legend(fontsize=10)
            vals = ax.get_yticks()
            ax.set_yticklabels(['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals])
        else:
            plt.figure(3).canvas.set_window_title('Single Linkage Tree')
            fig3 = clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=max(50,min(number_of_clusters*10,256)))
            plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
            plt.title('Single Linkage Tree', fontsize=12,loc='center')
            #tkinter.messagebox.showinfo("messagr", str(type(fig3)))
            #plot cutting distance
            y = getRadiansFromMeters(clusterTreeCuttingDist)
            xmin = fig3.get_xlim()[0]
            xmax = fig3.get_xlim()[1]
            line, = fig3.plot([xmin, xmax], [y, y], color='k', label='Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')
            line.set_label('Cluster (Cut) Distance ' + str(clusterTreeCuttingDist) +'m')
            fig3.legend(fontsize=10)
            vals = fig3.get_yticks()
            fig3.set_yticklabels(['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals])     
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
        
def getRadiansFromMeters(dist):
    dist = dist/1000
    degreesDist = dist/111.325
    radiansDist = degreesDist/57.2958
    return radiansDist
    #https://www.mathsisfun.com/geometry/radians.html
    #1 Radian is about 57.2958 degrees.
    #then see https://sciencing.com/convert-distances-degrees-meters-7858322.html
    #Multiply the number of degrees by 111.325
    #To convert this to meters, multiply by 1,000. So, 2 degrees is 222,65 meters.    
def getMetersFromRadians(dist):
    dist = dist * 57.2958
    dist = dist * 111.325
    metersDist = round(dist * 1000,1)

    return metersDist
    #1 Radian is about 57.2958 degrees.
    #then see https://sciencing.com/convert-distances-degrees-meters-7858322.html
    #Multiply the number of degrees by 111.325
    #To convert this to meters, multiply by 1,000. So, 2 degrees is 222,65 meters.    
    #plt.close('all') #clear memory
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
listbox = tk.Listbox(canvas,selectmode=tk.MULTIPLE, bd=0,background="gray29",fg="gray91",width=30)
listbox.bind('<<ListboxSelect>>', onselect)
scroll = tk.Scrollbar(canvas, orient=tk.VERTICAL,background="gray20",borderwidth=0)
scroll.configure(command=listbox.yview)
scroll.pack(side="right", fill="y")
listbox.pack()
listbox.config(yscrollcommand=scroll.set)
for item in topTagsList[:500]: #only for first 100 entries
    listbox.insert(tk.END, item[0] + " ("+ str(item[1]) + " user)")
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
        area = math.sqrt(s*(s-a)*(s-b)*(s-c))
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
        number_of_clusters = len(np.unique(clusters[~mask_noisy])) #mit noisy (=0)
        print("--> " + str(number_of_clusters) + " cluster.")
        tnum += 1
        photo_num = 0
        #clusternum_photolist = zip(clusters,selectedPhotoList)
        #clusterPhotosList = [[] for x in range(number_of_clusters)]
        clusterPhotosGuidsList = []
        for x in range(number_of_clusters):
            currentClusterPhotoGuids = numpy_selectedPhotoList_Guids[clusters==x]
            clusterPhotosGuidsList.append(currentClusterPhotoGuids)
        noClusterPhotos_perTag_DictOfLists[toptag[0]] = list(numpy_selectedPhotoList_Guids[clusters==-1])
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
        # Sort descending based on size of cluster: https://stackoverflow.com/questions/30346356/how-to-sort-list-of-lists-according-to-length-of-sublists
        clusterPhotosGuidsList.sort(key=len, reverse=True)
        if not len(clusterPhotosGuidsList) == 0:
            clustersPerTag[toptag[0]] = clusterPhotosGuidsList
        #plt.autoscale(enable=True)
        
        #if tnum == 50:
        #    break
            #plt.savefig('foo.png')
            #sys.exit()
    print("########## STEP 4 of 5: Generating Alpha Shapes ##########")
    sys.stdout.flush()
    #for each cluster of points, calculate boundary shape and add statistics (HImpTag etc.)
    listOfAlphashapesAndMeta = []
    tnum = 1
    for toptag in topTagsList:
        tnum += 1
        clusterPhotoGuidList = clustersPerTag.get(toptag[0], None)
        #print(toptag[0])
        if clusterPhotoGuidList:
            #clusterPhotoList = clustersPerTag[toptag[0]]
            #print(str(len(clusterPhotoGuidList)))
            firstCluster = True
            for photo_guids in clusterPhotoGuidList:
                if firstCluster:
                    HImP = 1
                    firstCluster = False
                else:
                    HImP = 0
                #try:
                #    print(*photos[:10])
                #except UnicodeEncodeError:
                #    print("skipped\n")
                #get full photo data from dict as list
                photos = [cleanedPhotoDict[x] for x in photo_guids]
                
                uniqueUserCount = len(set([photo.userid for photo in photos]))
                sumViews = sum([photo.photo_views for photo in photos])
                points = [geometry.Point(photo.lng, photo.lat)
                          for photo in photos]
                x = [p.coords.xy[0] for p in points]
                y = [p.coords.xy[1] for p in points]
                point_collection = geometry.MultiPoint(list(points))
                result_polygon = None
                if len(points) > 10:
                    if len(points) < 20:
                        result_polygon = point_collection.convex_hull #convex hull
                        result_polygon = result_polygon.buffer((limLngMax-limLngMin)/200,resolution=3)
                    else:
                        result_polygon = alpha_shape(points,alpha=clusterTreeCuttingDist*10) #concave hull/alpha shape
                        if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                            #repeat generating alpha shapes with smaller alpha value if Multigon is generated
                            result_polygon = alpha_shape(points,alpha=clusterTreeCuttingDist*5)
                            if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                                result_polygon = alpha_shape(points,alpha=clusterTreeCuttingDist)
                                if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                                    #if still of type multipolygon, try to remove holes and do a convex_hull
                                    result_polygon = result_polygon.convex_hull
                        result_polygon = result_polygon.buffer((limLngMax-limLngMin)/200,resolution=3)
                elif 2 <= len(points) < 5: 
                    #calc distance between points http://www.mathwarehouse.com/algebra/distance_formula/index.php
                    #bdist = math.sqrt((points[0].coords.xy[0][0]-points[1].coords.xy[0][0])**2 + (points[0].coords.xy[1][0]-points[1].coords.xy[1][0])**2)
                    #print(str(bdist))
                    result_polygon = point_collection.buffer((limLngMax-limLngMin)/200,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                elif len(points)==1 or type(result_polygon) is geometry.point.Point or result_polygon is None:
                    result_polygon = point_collection.buffer((limLngMax-limLngMin)/200,resolution=3) #single dots are presented as buffer with 0.5% of width-area
                #final check for multipolygon
                if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                        result_polygon = result_polygon.convex_hull
                #Geom, Join_Count, Views,  COUNT_User,ImpTag,TagCountG,HImpTag

                listOfAlphashapesAndMeta.append((result_polygon,len(photo_guids),sumViews,uniqueUserCount,toptag[0],toptag[1],HImP))
                #print(str(listOfPolygons[len(listOfPolygons)-1])+'\n')
                #plot_polygon(result_polygon)
                #plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                #plt.gca().set_xlim([float(limLngMin), float(limLngMax)]) 
                #plt.gca().set_ylim([float(limLatMin), float(limLatMax)])
                #plt.plot(x,y,'o',ms=5)
                #plt.waitforbuttonpress()
                #plt.close()
        singlePhotoGuidList = noClusterPhotos_perTag_DictOfLists.get(toptag[0], None)
        if singlePhotoGuidList:
            #print("Single: " + str(len(singlePhotoGuidList)))
            photos = [cleanedPhotoDict[x] for x in singlePhotoGuidList]
            points = [geometry.Point(photo.lng, photo.lat)
                      for photo in photos]
            x = [p.coords.xy[0] for p in points]
            y = [p.coords.xy[1] for p in points]
            point_collection = geometry.MultiPoint(list(points))
            result_polygon = point_collection.buffer((limLngMax-limLngMin)/200,resolution=3)
            if type(result_polygon) is geometry.multipolygon.MultiPolygon:
                for polygon in result_polygon:
                    listOfAlphashapesAndMeta.append((result_polygon,1,0,1,toptag[0],toptag[1],0))
            else:
                listOfAlphashapesAndMeta.append((result_polygon,1,0,1,toptag[0],toptag[1],0))
            
        #if tnum == 50:
        #    break
        #if toptag in noClusterPhotos_perTag_DictOfLists:
        #    singlePhotoList = noClusterPhotos_perTag_DictOfLists[toptag]
        #    #for singlePhoto in singlePhotoList:
        #    #point = geometry.Point(singlePhoto[2], singlePhoto[1])
        #    points = [geometry.Point(point[2], point[1])
        #              for point in singlePhotoList]
        #    x = [p.coords.xy[0] for p in points]
        #    y = [p.coords.xy[1] for p in points]
        #    point_collection = geometry.MultiPoint(list(points))
        #    result_polygon = point_collection.buffer((limLngMax-limLngMin)/200,resolution=3)
        #    if type(result_polygon) is geometry.multipolygon.MultiPolygon:
        #        for polygon in result_polygon:
        #            listOfPolygons.append(result_polygon)
        #    else:
        #        listOfPolygons.append(result_polygon)
            
    print(str(len(listOfAlphashapesAndMeta)) + " Alpha Shapes. Done.")
    ##Output Boundary Shapes in merged Shapefile##
    print("########## STEP 5 of 5: Writing Results to Shapefile ##########")
    
    # Define a polygon feature geometry with one attribute
    schema = {
        'geometry': 'Polygon',
        'properties': {'Join_Count': 'int', 
                       'Views': 'int',
                       'COUNT_User': 'int',
                       'ImpTag': 'str',
                       'TagCountG': 'int',
                       'HImpTag': 'int'},
    }
    
    # Write a new Shapefile
    # WGS1984
    with fiona.open('Output/allTagClusters.shp', mode='w', driver='ESRI Shapefile', schema=schema,crs=from_epsg(4326)) as c:
        ## If there are multiple geometries, put the "for" loop here
        idx = 0
        for alphaShapeAndMeta in listOfAlphashapesAndMeta:
            idx += 1
            c.write({
                'geometry': geometry.mapping(alphaShapeAndMeta[0]),
                'properties': {'Join_Count': alphaShapeAndMeta[1], 
                               'Views': alphaShapeAndMeta[2],
                               'COUNT_User': alphaShapeAndMeta[3],
                               'ImpTag': alphaShapeAndMeta[4],
                               'TagCountG': alphaShapeAndMeta[5],
                               'HImpTag': alphaShapeAndMeta[6]},
            })
    
    print("\n" + "Done.")
else:
    print("\n" + "User abort.")

##see https://pypkg.com/pypi/hdbscan-with-cosine-distance/f/hdbscan/plots.py for retrieving clusters at specific lambda values
##class CondensedTree(object):
##    def __init__(self, condensed_tree_array):
##        self._raw_tree = condensed_tree_array
##
##    def get_plot_data(self, leaf_separation=1, log_size=False):
##        """Generates data for use in plotting the 'icicle plot' or dendrogram 
##        plot of the condensed tree generated by HDBSCAN.
##
##        Parameters
##        ----------
##        leaf_separation : float, optional
##                          How far apart to space the final leaves of the 
##                          dendrogram. (default 1)
##
##        log_size : boolean, optional
##                   Use log scale for the 'size' of clusters (i.e. number of
##                   points in the cluster at a given lambda value).
##                   (default False)
##        
##        Returns
##        -------
##        plot_data : dict
##                    Data associated to bars in a bar plot:
##                        `bar_centers` x coordinate centers for bars
##                        `bar_tops` heights of bars in lambda scale
##                        `bar_bottoms` y coordinate of bottoms of bars
##                        `bar_widths` widths of the bars (in x coord scale)
##                        `bar_bounds` a 4-tuple of [left, right, bottom, top]
##                                     giving the bounds on a full set of 
##                                     cluster bars
##                    Data associates with cluster splits:
##                        `line_xs` x coordinates for horiontal dendrogram lines
##                        `line_ys` y coordinates for horiontal dendrogram lines
##        """