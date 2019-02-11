"""
Run Integration test for tagMaps
This will check complete process of main() as if
evoked with tagmaps --autoMode --maxItems 50
"""

import sys
import os
import tagmaps
import argparse
from pathlib import Path
from tagmaps.__main__ import main as tm

if __name__ == '__main__':
    os.environ["TAGMAPS_RESOURCES"] = str(Path.cwd() / "resources")
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--autoMode', action="store_true")
    # parser.add_argument('--maxItems', default=50)
    # parser.add_argument(
    #     '--inputFolder', default=Path.cwd() / "resources" / "01_Input")
    # parser.add_argument(
    #     '--configFolder', default=Path.cwd() / "resources" / "00_Config")
    # parser.add_argument('unittest_args', nargs='*')
    #
    # args = parser.parse_args()
    # # TODO: Go do something with args.input and args.filename
    # print(Path.cwd() / "resources" / "01_Input")
    # # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    # sys.argv[1:] = args.unittest_args
    tm()
