"""
Run Integration test for tagMaps
This will check complete process of main() as if
evoked with tagmaps --autoMode --maxItems 50
"""

import sys
import tagmaps
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--autoMode', action="store_true")
    parser.add_argument('maxItems', default='some_file.txt')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    # TODO: Go do something with args.input and args.filename

    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = args.unittest_args
    tagmaps.__main__.main()
