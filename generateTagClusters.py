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
import seaborn as sns
import sklearn.datasets as data
import pandas as pd
import hdbscan

##Needed for Shapefilestuff
#import fiona #Fiona needed for reading Shapefile
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
print("########## STEP 1 of 4: Data Cleanup ##########")
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
                    photo_latitude = Decimal(item[1])
                    photo_longitude = Decimal(item[2])
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
            print("Cleaned output of " + "%02d" % (count_loc,)  + " photolocations from " + "%02d" % (count_glob,)+ " (File " + str(partcount) + " of " + str(len(filelist)) + ") - Skipped Media: " + str(skippedCount) + " - Skipped Tags: " + str(count_tags_skipped) +" of " + str(count_tags_global), end='\r')
            

total_distinct_locations = len(distinctLocations_set)
print("Total distinct locations: " + str(total_distinct_locations))
cleanedPhotoList = []
#create structure for tuple with naming for easy referencing
cleanedPhotoLocation_tuple = namedtuple('cleanedPhotoLocation_tuple', 'source lat lng photo_guid photo_owner userid photo_caption photo_dateTaken photo_uploadDate photo_views photo_tags photo_thumbnail photo_mTags photo_likes photo_comments photo_shortcode photo_mediatype photo_locName photo_locID')
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
            cleanedPhotoList.append(cleanedPhotoLocation)

print("########## STEP 2 of 4: Tag Ranking ##########")
overallNumOfUsersPerTag_global = collections.Counter()
for user_key, taghash in UserDict_TagCounters_global.items():
    #taghash contains unique values (= strings) for each user, thus summing up these taghashes counts each user only once per tag
    overallNumOfUsersPerTag_global.update(taghash)
toptags = ''.join("%s,%i" % v + '\n' for v in overallNumOfUsersPerTag_global.most_common(1000))
with open("Output/Output_toptags.txt", 'w', encoding="utf8") as file: #overwrite
    file.write(toptags)

tmax = 1000
topTagsList = overallNumOfUsersPerTag_global.most_common(tmax)

print("########## STEP 3 of 4: Tag Location Clustering ##########")
#prepare some variables
tnum = 0
first = True
plot_kwds = {'alpha' : 0.5, 's' : 10, 'linewidths':0}
sys.stdout.flush()
#Query user for optional removing of tags removing
#User GUI query for excluding tags
top_Tkinter_Root_Window = def_functions.initMainTk() #Tk()
frame = def_functions.Win(top_Tkinter_Root_Window)
#necessary override for error reporting during tkinter mode
#def report_callback_exception(self, exc, val, tb):
#    showerror("Error", message=str(val))
#tk.Tk.report_callback_exception = report_callback_exception
    
#the following code part is a bit garbled due to using TKinter interface
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################
    
def cluster_tags():
    global top_Tkinter_Root_Window
    #global def_functions
    #global plt
    global tnum
    global first
    global plot_kwds
    global cleanedPhotoList
    global topTagsList
    global frame
    #calculate once boundary for all points
    df = pd.DataFrame(cleanedPhotoList)
    points = df.as_matrix(['lng','lat'])
    if first == True:
        limYMin = np.min(points.T[1])
        limYMax = np.max(points.T[1])
        limXMin = np.min(points.T[0])
        limXMax = np.max(points.T[0])
        #set global plotting bounds for matplotlib
        plt.gca().set_xlim([limXMin, limXMax]) 
        plt.gca().set_ylim([limYMin, limYMax])
        first = False
    #calculate imageRatio from distance covered
    distY = limYMax - limYMin
    distX = limXMax - limXMin
    imgRatio = distX/(distY*2) #multiply by 2 because lat = 90 and lng = 180!
    def cluster_tag(toptag):
        global cleanedPhotoList
        global pathname
        global tnum
        global tmax
        global plot_kwds
        global first
        global frame
        #frame.destroy()
        #global plt
        nonlocal canvas
        nonlocal l
        nonlocal distY
        nonlocal distX
        nonlocal limYMin
        nonlocal limYMax
        nonlocal limXMin
        nonlocal limXMax
        nonlocal imgRatio
        distinctLocalLocationCount = set()
        selectedPhotoList = []
        for cleanedPhotoLocation in cleanedPhotoList:
            if toptag[0] in (cleanedPhotoLocation.photo_tags) or (toptag in cleanedPhotoLocation.photo_caption):
                selectedPhotoList.append(cleanedPhotoLocation)
                distinctLocalLocationCount.add(cleanedPhotoLocation.photo_locID)
        percentageOfTotalLocations = len(distinctLocalLocationCount)/(total_distinct_locations/100)
        print("(" + str(tnum) + " of " + str(tmax) + ") Found " + str(len(selectedPhotoList)) + " photos for tag " + "'" + toptag[0] + "' (" + str(round(percentageOfTotalLocations,0)) + "% of total distinct locations in area)")
        #clustering
        df = pd.DataFrame(selectedPhotoList)
        points = df.as_matrix(['lng','lat']) #converts pandas dataframe to numpy array (limit by list of column-names)
        test_data = np.radians(points) #conversion to radians for HDBSCAN (does not support decimal degrees)
        #for each tag in overallNumOfUsersPerTag_global.most_common(1000) (descending), calculate HDBSCAN Clusters
        minClusterSize = int(((len(selectedPhotoList))/100)*5) #4% optimum
        #minClusterSize = 2
        clusterer = hdbscan.HDBSCAN(min_cluster_size=minClusterSize,gen_min_span_tree=True,allow_single_cluster=True,min_samples=1)
        #clusterer = hdbscan.robust_single_linkage_.RobustSingleLinkage(cut=0.000035)
        #srsl_plt = hdbscan.robust_single_linkage_.plot()
        clusterer.fit(test_data)
        sel_labels = clusterer.single_linkage_tree_.get_clusters(0.000035, min_cluster_size=2) #0.000035 without haversine: 223 m (or 95 m for 0.000015)
        #if toptag[0] == "water":
        #    print(sel_labels)
        palette = sns.color_palette(None, len(sel_labels)) #sns.color_palette("hls", ) #sns.color_palette(None, 100)
        sel_colors = [palette[x] if x >= 0
                      else (0.5, 0.5, 0.5)
                      #for x in clusterer.labels_ ]
                      for x in sel_labels] #clusterer.labels_ (best selection) or sel_labels (cut distance)
        if tnum < 20:
            fig = plt.figure(figsize=(11, int(11*imgRatio)), dpi=80)
            fig.suptitle(toptag[0].upper(), fontsize=24, fontweight='bold')
            fig = plt.scatter(points.T[0], points.T[1], color='red', **plot_kwds)
            fig.figure.savefig(pathname + '/Output/ClusterImg/graph_' + "%04d" % (tnum,) + '.png')
            fig2 = plt.figure(figsize=(11, 11), dpi=80)
            fig2.suptitle(toptag[0].upper(), fontsize=24, fontweight='bold')
            #selected clusters herin don't match get_clusters at cut = 0.000035!!
            fig2 = clusterer.condensed_tree_.plot(select_clusters=False, selection_palette=sel_colors,label_clusters=True)
            fig2.figure.savefig(pathname + '/Output/ClusterImg/graph_' + "%04d" % (tnum,) + '_clusterTree.png')
            fig3 = plt.figure(figsize=(11, 11), dpi=80)
            fig3.suptitle(toptag[0].upper(), fontsize=24, fontweight='bold')   
            fig3 = clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=50)
            fig3.figure.savefig(pathname + '/Output/ClusterImg/graph_' + "%04d" % (tnum,) + '_Tree.png')
            #create map with cluster-colors from cut
            fig4 = plt.figure(figsize=(11, int(11*imgRatio)), dpi=80)
            fig4.suptitle(toptag[0].upper(), fontsize=24, fontweight='bold')
            fig4 = plt.scatter(points.T[0], points.T[1], c=sel_colors, **plot_kwds)
            fig4.figure.savefig(pathname + '/Output/ClusterImg/graph_' + "%04d" % (tnum,) + '_cluster.png')
        
        #first tag, train cut distance by human observer
        if tnum == 1:
            #frame.configure(background='gray7')
            def quitTkinter():
                global top_Tkinter_Root_Window
                top_Tkinter_Root_Window.update() #see https://stackoverflow.com/questions/35040168/python-tkinter-error-cant-evoke-event-command
                frame.update()
                frame.destroy()
                top_Tkinter_Root_Window.destroy()
            w = frame.winfo_reqwidth()
            h = frame.winfo_reqheight()
            ws = frame.winfo_screenwidth()
            hs = frame.winfo_screenheight()
            x = (ws/2) - (w/2)
            y = (hs/2) - (h/2)
            top_Tkinter_Root_Window.geometry('+%d+%d' % (x, y))
            
            l = tk.Label(canvas, text="Optional: Exclude tags.", background="gray7",fg="gray80",font="Arial 10 bold")
            l.pack(padx=10, pady=10)
            l = tk.Label(canvas, text="Select all tags you wish to exclude from analysis \n and click on remove to proceed.", background="gray7",fg="gray80")
            l.pack(padx=10, pady=10)
            image = tk.PhotoImage(file=pathname + '/Output/ClusterImg/graph_' + "%04d" % (tnum,) + '_cluster.png')
            label = tk.Label(canvas,image=image,background="gray29",fg="gray91")
            label.pack()
            #listbox = Listbox(canvas,selectmode=MULTIPLE, bd=0,background="gray29",fg="gray91")
            #listbox.pack()
            #for item in topTagsList[:100]: #only for first 100 entries
            #    listbox.insert(END, item[0] + " ("+ str(item[1]) + " photos)")
            b = tk.Button(canvas, text = "Proceed", command=quitTkinter, background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
            b.pack(padx=10, pady=10)
            canvas.pack(fill='both',padx=10, pady=10)
            frame.pack()
            top_Tkinter_Root_Window.update()    
        
    canvas = tk.Canvas(frame, width=1320, height=440, highlightthickness=0,background="gray7")
    top_Tkinter_Root_Window.title("Select Cluster Distance")
    l = tk.Label(canvas, text="########## STEP 3 of 4: Tag Location Clustering ##########", background="gray7",fg="gray80")
    l.pack()
    #
    #Cluster preparation
    sns.set_context('poster')
    sns.set_style('white')
    sns.set_color_codes()
    matplotlib.style.use('ggplot')
    #photo selection
    
    for toptag in topTagsList:
        tnum += 1
        cluster_tag(toptag)
        #plt.close()
        if tnum > 3:
            break
    #plt.close('all') #clear memory    
######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################

w = frame.winfo_reqwidth()
h = frame.winfo_reqheight()
ws = frame.winfo_screenwidth()
hs = frame.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
top_Tkinter_Root_Window.title("Optional: Exclude tags")
top_Tkinter_Root_Window.geometry('+%d+%d' % (x, y))
canvas = tk.Canvas(frame, width=150, height=400, highlightthickness=0,background="gray7")
l = tk.Label(canvas, text="Optional: Exclude tags.", background="gray7",fg="gray80",font="Arial 10 bold")
l.pack(padx=10, pady=10)
l = tk.Label(canvas, text="Select all tags you wish to exclude from analysis \n and click on remove to proceed.", background="gray7",fg="gray80")
l.pack(padx=10, pady=10)
listbox = tk.Listbox(canvas,selectmode=tk.MULTIPLE, bd=0,background="gray29",fg="gray91")
listbox.pack()
for item in topTagsList[:100]: #only for first 100 entries
    listbox.insert(tk.END, item[0] + " ("+ str(item[1]) + " photos)")
#tagsRemoved = False
def delete(listbox):
    global topTagsList
    global tagsRemoved
    global cluster_tags
    # Delete from Listbox
    selection = listbox.curselection()
    for index in selection[::-1]:
        listbox.delete(index)
        del(topTagsList[index])
    cluster_tags()
b = tk.Button(canvas, text = "Remove and Proceed", command = lambda: delete(listbox), background="gray20",fg="gray80",borderwidth=0,font="Arial 10 bold")
b.pack(padx=10, pady=10)
canvas.pack(fill='both',padx=10, pady=10)
frame.pack()
#top_Tkinter_Root_Window.update()
    
top_Tkinter_Root_Window.mainloop()        
    #Radians to meters:
    #https://www.mathsisfun.com/geometry/radians.html
    #1 Radian is about 57.2958 degrees.
    #then see https://sciencing.com/convert-distances-degrees-meters-7858322.html
    #Multiply the number of degrees by 111.325
    #To convert this to meters, multiply by 1,000. So, 2 degrees is 222,65 meters.
    
print("########## STEP 4 of 4: Calculation of Tag Cluster Shapes ##########")
#for each cluster of points, calculate boundary shape and add statistics (HImpTag etc.)

##Output Boundary Shapes in merged Shapefile##

print("\n" + "Done.")

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