#!/usr/bin/env python
# coding: utf-8
# test tag clusters

"""Emoji test module

This file is still on the TO_DO list
"""
# test_capitalize.py


def capital_case(x):
    return x.capitalize()


def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'

# Emojitest
# n = '❤️👨‍⚕️'
# n = '😍,146'
# n = '👨‍👩‍👦‍👦' (grapheme cluster)
# print(n.encode("utf-8"))
# n = '👨‍⚕️' #medical emoji with zero-width joiner
# see:
# http://www.unicode.org/emoji/charts/emoji-zwj-sequences.html)
# nlist = Utils.extract_emojis(n)
# with open("emojifile.txt", "w", encoding='utf-8') as emojifile:
#    emojifile.write("Original: " + n + '\n')
#    for xstr in nlist:
#        emojifile.write('Emoji Extract: U+%04x' % ord(xstr) + '\n')
#        emojifile.write(xstr + '\n')
#    for _c in n:
#        emojifile.write(str(unicode_name(_c)) + '\n')
#        emojifile.write('Each Codepoint: U+%04x' % ord(_c) +  '\n')
# initialize global variables for
# analysis bounds (lat, lng coordinates)

# see
# https://stackoverflow.com/questions/43852668/using-collections-counter-to-count-emojis-with-different-colors
# we want to ignore fitzpatrick modifiers
# and treat all differently colored emojis the same
# https://stackoverflow.com/questions/38100329/some-emojis-e-g-have-two-unicode-u-u2601-and-u-u2601-ufe0f-what-does
# COOKING
# OK HAND SIGN
# EMOJI MODIFIER FITZPATRICK TYPE-1-2
# GRINNING FACE WITH SMILING EYES
# HEAVY BLACK HEART
# WEARY CAT FACE
# SMILING FACE WITH HEART-SHAPED EYES
# OK HAND SIGN
# EMOJI MODIFIER FITZPATRICK TYPE-1-2
# GRINNING FACE WITH SMILING EYES
# PERSON WITH FOLDED HANDS
# EMOJI MODIFIER FITZPATRICK TYPE-3
# WEARY CAT FACE

# def cleanEmoji(c):
#    tuple = (u'\ufeff',u'\u200b',u'\u200d')
#    for ex in tuple:
#        c.replace(ex,"")
#    return(c)
# https://github.com/carpedm20/emoji/
# https://github.com/carpedm20/emoji/issues/75
# tc unicode problem
# https://stackoverflow.com/questions/40222971/python-find-equivalent-surrogate-pair-from-non-bmp-unicode-char

# @staticmethod
# def _extract_emoji_slow(string_with_emoji):
#     return [x.encode('utf-8') for x
#             in gc.grapheme_clusters(
#             string_with_emoji)]

# @staticmethod
# def _is_flag_emoji(c):
#     return "\U0001F1E6\U0001F1E8" <= c <= "\U0001F1FF\U0001F1FC" \
#            or c in [
#            "\U0001F3F4\U000e0067\U000e0062\U000e0065\U000e006e" \
#            "\U000e0067\U000e007f", "\U0001F3F4\U000e0067\U000e0062" \
#            "\U000e0073\U000e0063\U000e0074\U000e007f",
#            "\U0001F3F4\U000e0067\U000e0062\U000e0077\U000e006c" \
#            "\U000e0073\U000e007f"]

# enable for map display
# from mpl_toolkits.basemap import Basemap
# from PIL import Image
# https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects
# alternative Shapefile module pure Python
# https://github.com/GeospatialPython/pyshp#writing-shapefiles
# import shapefile
# to test:
# bba9f14180134069a9da5b3eb3539130822f917a55fc42d4adcc816018f79d9e "bei;bilzbad;flamingos;radebeul;@mcfitti;👯🎉😋;30grad;und","radebeul;bilzbad;flamingos","🐬;🌊;😋;🎉;👯"
