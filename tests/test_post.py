#!/usr/bin/env python
# coding: utf-8
# test tag clusters


# test_capitalize.py

def capital_case(x):
    return x.capitalize()


def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'

# Emojitest
#n = '❤️👨‍⚕️'
#n = '😍,146'
# print(n.encode("utf-8"))
# n = '👨‍⚕️' #medical emoji with zero-width joiner (http://www.unicode.org/emoji/charts/emoji-zwj-sequences.html)
#nlist = Utils.extract_emojis(n)
# with open("emojifile.txt", "w", encoding='utf-8') as emojifile:
#    emojifile.write("Original: " + n + '\n')
#    for xstr in nlist:
#        emojifile.write('Emoji Extract: U+%04x' % ord(xstr) + '\n')
#        emojifile.write(xstr + '\n')
#    for _c in n:
#        emojifile.write(str(unicode_name(_c)) + '\n')
#        emojifile.write('Each Codepoint: U+%04x' % ord(_c) +  '\n')
# initialize global variables for analysis bounds (lat, lng coordinates)
