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
from tagmaps.__main__ import main as tm_main

if __name__ == '__main__':
    os.environ["TAGMAPS_RESOURCES"] = str(Path.cwd() / "resources")
    tm_main()
