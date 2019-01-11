#!/usr/bin/env python
# coding: utf-8
# TimeTransponse_from_json definition of functions file

"""Module with general utility methods used in tag maps package.
"""

import os
import sys
import tkinter as tk
import emoji
import unicodedata
import math
import numpy as np
import math
from math import radians, cos, sin, asin, sqrt
import re
import hashlib
import io
import logging
import fiona #Fiona needed for reading Shapefile
from fiona.crs import from_epsg
import shapely.geometry as geometry
import pyproj #import Proj, transform
#https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects
from shapely.ops import transform, cascaded_union, polygonize
#from shapely.geometry import Polygon
#from shapely.geometry import shape
#from shapely.geometry import Point
from decimal import Decimal
from descartes import PolygonPatch
from scipy.spatial import Delaunay
import argparse
from tagmaps.config.config import BaseConfig
from tagmaps.classes.shared_structure import CleanedPost

class Utils():
    """Collection of various tools and helper functions

    Primarily @classmethods and @staticmethods
    """
    @staticmethod
    def default_empty_cstructure():
        """Generates a tuple of parametric length with
        empty strings:
        (" "," "," "," "," "," "," "," "," "," "," "," ")
        """
        empty_string_list = list()
        for _ in range(len(CleanedPost._fields)):
            empty_string_list.append(" ")
        empty_string_tuple = tuple(empty_string_list)
        return empty_string_tuple

    @staticmethod
    def encode_string(s):
        """Encode string in Sha256, produce hex

        - returns a string of double length, containing only hexadecimal digits"""
        encoded_string = hashlib.sha3_256(s.encode("utf8")).hexdigest()
        return encoded_string

    @staticmethod
    def remove_special_chars(s):
        """Removes any special char from string"""
        SPECIAL_CHARS = "?.!/;:,[]()'-&#"
        s_cleaned = s.translate(
            {ord(c): " " for c in SPECIAL_CHARS})
        return s_cleaned

    @staticmethod
    def is_number(s):
        """Check if variable is number (float)"""
        try:
            float(s)
            return True
        except ValueError:
            return False

    @classmethod
    def init_main(cls):
        """Initializing main procedure if package is executed directly"""
    
        # set console view parameters
        os.system('mode con: cols=197 lines=40')
        # initialize logger
        log = cls.set_logger()
        logging.getLogger("fiona.collection").disabled = True
        cfg = BaseConfig()
        # create output dir if not exists
        Utils.init_output_dir()
    
        return cfg, log

    @classmethod
    def set_logger(cls):
        """ Set logging handler manually, 
        so we can also print to console while logging to file
        """
        
        cls.init_output_dir()
        __log_file = "02_Output/log.txt"
    
        # Set Output to Replace in case of encoding issues (console/windows)
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), sys.stdout.encoding, 'replace')
        # Create logger with specific name
        log = logging.getLogger("tagmaps")
        log.format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
        log.datefmt = '%H:%M:%S'
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.FileHandler(__log_file, 'w', 'utf-8'))
        log.addHandler(logging.StreamHandler())
        # flush once to clear console
        sys.stdout.flush()
        return log

    @staticmethod
    def init_output_dir():
        """Creates local output dir if not exists"""

        pathname = os.getcwd()
        if not os.path.exists(pathname + '/02_Output/'):
            os.makedirs(pathname + '/02_Output/')
            print("Folder /02_Output was created")
    
    @staticmethod
    def query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("'yes' or 'no' "
                                 "(or 'y' or 'n').\n")
    @staticmethod
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371* c
        m = km*1000
        return m

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def checkEmojiType(strEmo):
        """Is this function really needed, makes no difference! (really?)"""
        if unicodedata.name(strEmo).startswith(("EMOJI MODIFIER","VARIATION SELECTOR","ZERO WIDTH")):
            return False
        return True

    @staticmethod
    def extract_emoji(str):
        """Extracts emoji from string

        str = str.decode('utf-32').encode('utf-32', 'surrogatepass')
        return list(c for c in str if c in emoji.UNICODE_EMOJI)
        """
        emoji_list = list(c for c in str if c in
                          emoji.UNICODE_EMOJI and
                          Utils.checkEmojiType(c) is True)
        return emoji_list

        #see https://stackoverflow.com/questions/43852668/using-collections-counter-to-count-emojis-with-different-colors
        # we want to ignore fitzpatrick modifiers and treat all differently colored emojis the same
        #https://stackoverflow.com/questions/38100329/some-emojis-e-g-have-two-unicode-u-u2601-and-u-u2601-ufe0f-what-does
    #COOKING
    #OK HAND SIGN
    #EMOJI MODIFIER FITZPATRICK TYPE-1-2
    #GRINNING FACE WITH SMILING EYES
    #HEAVY BLACK HEART
    #WEARY CAT FACE
    #SMILING FACE WITH HEART-SHAPED EYES
    #OK HAND SIGN
    #EMOJI MODIFIER FITZPATRICK TYPE-1-2
    #GRINNING FACE WITH SMILING EYES
    #PERSON WITH FOLDED HANDS
    #EMOJI MODIFIER FITZPATRICK TYPE-3
    #WEARY CAT FACE

    ##Emojitest
    #n = '❤️👨‍⚕️'
    ##n = '👨‍⚕️' #medical emoji with zero-width joiner (http://www.unicode.org/emoji/charts/emoji-zwj-sequences.html)
    #nlist = def_functions.extract_emojis(n)
    #with open("emojifile.txt", "w", encoding='utf-8') as emojifile:
    #    emojifile.write("Original: " + n + '\n')
    #    for xstr in nlist:
    #        emojifile.write('Emoji Extract: U+%04x' % ord(xstr) + '\n')
    #        emojifile.write(xstr + '\n')
    #    for _c in n:
    #        emojifile.write(str(unicode_name(_c)) + '\n')
    #        emojifile.write('Each Codepoint: U+%04x' % ord(_c) +  '\n')
    #def cleanEmoji(c):
    #    tuple = (u'\ufeff',u'\u200b',u'\u200d')
    #    for ex in tuple:
    #        c.replace(ex,"")
    #    return(c)
    #https://github.com/carpedm20/emoji/
    #https://github.com/carpedm20/emoji/issues/75


    #this class is needed to override tkinter window with drag&drop option when overrideredirect = true
    #class App:
    #    global tk
    #    def __init__(self):
    #        self.root = tk.Tk()
    #        #tk.Tk.__init__(self,master)
    #        self.root.overrideredirect(True)
    #        self.root.configure(background='gray7')
    #        self.root._offsetx = 0
    #        self.root._offsety = 0
    #        self.root.bind('<ButtonPress-1>',self.clickwin)
    #        self.root.bind('<B1-Motion>',self.dragwin)
    #
    #    def dragwin(self,event):
    #        x = self.root.winfo_pointerx() - self._offsetx
    #        y = self.root.winfo_pointery() - self._offsety
    #        self.root.geometry('+{x}+{y}'.format(x=x,y=y))
    #
    #    def clickwin(self,event):
    #        self.root._offsetx = event.x
    #        self.root._offsety = event.y

    #tc unicode problem
    #https://stackoverflow.com/questions/40222971/python-find-equivalent-surrogate-pair-from-non-bmp-unicode-char

    
    def _surrogatepair(match):
        char = match.group()
        assert ord(char) > 0xffff
        encoded = char.encode('utf-16-le')
        return (
            chr(int.from_bytes(encoded[:2], 'little')) +
            chr(int.from_bytes(encoded[2:], 'little')))

    def with_surrogates(text):
        _nonbmp = re.compile(r'[\U00010000-\U0010FFFF]')
        return _nonbmp.sub(_surrogatepair, text)

    #https://stackoverflow.com/questions/40132542/get-a-cartesian-projection-accurate-around-a-lat-lng-pair
    def convert_wgs_to_utm(lon, lat):
        utm_band = str((math.floor((lon + 180) / 6 ) % 60) + 1)
        if len(utm_band) == 1:
            utm_band = '0'+utm_band
        if lat >= 0:
            epsg_code = '326' + utm_band
        else:
            epsg_code = '327' + utm_band
        return epsg_code

    #def str2bool(v):
    #    if v.lower() in ('yes', 'true', 't', 'y', '1'):
    #        return True
    #    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
    #        return False
    #    else:
    #        raise argparse.ArgumentTypeError('Boolean value expected.')

    def generateClusterShape(toptag,clusterPhotoGuidList,cleanedPhotoDict,crs_wgs,crs_proj,clusterTreeCuttingDist,localSaturationCheck):
        #we define a new list of Temp Alpha Shapes outside the loop, so that it is not overwritten each time
        listOfAlphashapesAndMeta_tmp = []
        #points = []
        tagArea = 0
        for photo_guids in clusterPhotoGuidList:
            #for each cluster for this toptag
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
                    shapetype = "between 5 and 10 points_convexHull"
                    #result_polygon = result_polygon.buffer(min(distXLng,distYLat)/100,resolution=3)
                else:
                    if len(points) > 500:
                        startalpha = 1000000
                    elif len(points) > 200:
                        startalpha = 10000
                    else:
                        startalpha = 9000
                    result_polygon = Utils.alpha_shape(points,alpha=clusterTreeCuttingDist/startalpha) #concave hull/alpha shape /50000
                    shapetype = "Initial Alpha Shape + Buffer"
                    if type(result_polygon) is geometry.multipolygon.MultiPolygon or isinstance(result_polygon, bool):
                        #repeat generating alpha shapes with smaller alpha value if Multigon is generated
                        #smaller alpha values mean less granularity of resulting polygon
                        #but too large alpha may result in empty polygon
                        #(this branch is sometimes executed for larger scales)
                        for i in range(1,6):
                            #try decreasing alpha
                            alpha = startalpha + (startalpha * (i**i)) #** means cube
                            result_polygon = Utils.alpha_shape(points,alpha=clusterTreeCuttingDist/alpha)#/100000
                            if not type(result_polygon) is geometry.multipolygon.MultiPolygon and not isinstance(result_polygon, bool):
                                shapetype = "Multipolygon Alpha Shape /" + str(alpha)
                                break
                        if type(result_polygon) is geometry.multipolygon.MultiPolygon or isinstance(result_polygon, bool):
                            #try increasing alpha
                            for i in range(1,6):
                                #try decreasing alpha
                                alpha = startalpha / (i*i)
                                result_polygon = Utils.alpha_shape(points,alpha=clusterTreeCuttingDist/alpha)#/100000
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
                if localSaturationCheck:
                    tagArea += result_polygon.area
                listOfAlphashapesAndMeta_tmp.append((result_polygon,photoCount,sumViews,uniqueUserCount,toptag[0],toptag[1],weightsv1,weightsv2,weightsv3,shapetype))
        if len(listOfAlphashapesAndMeta_tmp) > 0:
            # finally sort and append all cluster shapes for this tag
            listOfAlphashapesAndMeta_tmp = sorted(listOfAlphashapesAndMeta_tmp,key=lambda x: -x[6])
        return listOfAlphashapesAndMeta_tmp, tagArea

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

    def fit_cluster(clusterer, data):
        clusterer.fit(data)
        return clusterer
        
    def getRectangleBounds(points):
        limYMin = np.min(points.T[1])
        limYMax = np.max(points.T[1])
        limXMin = np.min(points.T[0])
        limXMax = np.max(points.T[0])
        return limYMin, limYMax, limXMin, limXMax

    def filterTags(taglist,SortOutAlways_set,SortOutAlways_inStr_set):
        count_tags = 0
        count_skipped = 0
        #Filter tags based on two stoplists
        photo_tags_filtered = set()
        for tag in taglist:
            count_tags += 1
            #exclude numbers and those tags that are in SortOutAlways_set
            if len(tag) == 1 or tag == '""' or tag.isdigit() or tag in SortOutAlways_set:
                count_skipped += 1
                continue
            for inStr in SortOutAlways_inStr_set:
                if inStr in tag:
                    count_skipped += 1
                    break
            else:
                photo_tags_filtered.add(tag)
        return photo_tags_filtered,count_tags,count_skipped