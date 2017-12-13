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
import def_functions
import datetime
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
if (len(filelist) == 0):
    sys.exit("No *.json/csv files found.")
else:
    print("Files to process:" + str(len(filelist)))
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
PhotoLocDict = defaultdict(set)
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
                          ";".join(UserLocationWordList_dict.get(locIDUserID,("",))),#photo_caption = 6
                          photo[6],#photo_dateTaken = 7
                          photo[7],#photo_uploadDate = 8
                          int(photo[8]),#photo_views = 9
                          ";".join(UserLocationTagList_dict.get(locIDUserID,("",))),#photo_tags = 10
                          photo[5],#photo_thumbnail = 11
                          photo[10],#photo_mTags = 12
                          photo[11],#photo_likes = 13
                          photo[12],#photo_comments = 14
                          photo[13],#photo_shortcode = 15
                          photo[14],#photo_mediatype = 16
                          photo[15],#photo_locName = 17
                          photo[16]#photo_locID = 18
                          )
            datawriter.writerow(cleanedPhotoLocation)
            cleanedPhotoList.append(cleanedPhotoLocation)

#tagcounters
overallNumOfUsersPerTag_global = collections.Counter()
for user_key, taghash in UserDict_TagCounters_global.items():
    #taghash contains unique values (= strings) for each user, thus summing up these taghashes counts each user only once per tag
    overallNumOfUsersPerTag_global.update(taghash)
toptags = ''.join("%s,%i" % v + '\n' for v in overallNumOfUsersPerTag_global.most_common(1000))
with open("Output/Output_toptags.txt", 'w', encoding="utf8") as file: #overwrite
    file.write(toptags)         
print("\n" + "Done.")