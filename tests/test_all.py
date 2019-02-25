"""
Run Integration test for tagMaps
This will check complete process of main() as if
evoked with tagmaps --autoMode --maxItems 50
"""

import sys
import os
import traceback
from pathlib import Path
from tagmaps.__main__ import main as tm_main


def tagmaps_system_integration_test():
    """Test complete method integration using main()"""
    # override resource path
    os.environ["TAGMAPS_RESOURCES"] = str(Path.cwd() / "resources")
    try:
        tm_main()
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    tagmaps_system_integration_test()
