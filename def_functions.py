#!/usr/bin/env python
# coding: utf8
# TimeTransponse_from_json definition of functions file
import sys
import tkinter as tk
import emoji
import unicodedata
import math

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

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

from math import radians, cos, sin, asin, sqrt
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

#This function is not really needed, makes no difference! (really?)
#def checkEmojiType(strEmo):
#    if unicodedata.name(strEmo).startswith(("EMOJI MODIFIER","VARIATION SELECTOR","ZERO WIDTH JOINER")):
#        return False
#    else:
#        return True
#    #see https://stackoverflow.com/questions/43852668/using-collections-counter-to-count-emojis-with-different-colors
#    # we want to ignore fitzpatrick modifiers and treat all differently colored emojis the same
#    #https://stackoverflow.com/questions/38100329/some-emojis-e-g-have-two-unicode-u-u2601-and-u-u2601-ufe0f-what-does
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

    
#https://github.com/carpedm20/emoji/
#https://github.com/carpedm20/emoji/issues/75
def extract_emojis(str):
  #str = str.decode('utf-32').encode('utf-32', 'surrogatepass')
  return list(c for c in str if c in emoji.UNICODE_EMOJI)
  #return list(c for c in str if c in emoji.UNICODE_EMOJI and checkEmojiType(c) is True)
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
import re
_nonbmp = re.compile(r'[\U00010000-\U0010FFFF]')
def _surrogatepair(match):
    char = match.group()
    assert ord(char) > 0xffff
    encoded = char.encode('utf-16-le')
    return (
        chr(int.from_bytes(encoded[:2], 'little')) + 
        chr(int.from_bytes(encoded[2:], 'little')))
def with_surrogates(text):
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

#class WinImg(Frame):
#    def __init__(self,parent):
#        Frame.__init__(self,parent)

        