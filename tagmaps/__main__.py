# -*- coding: utf-8 -*-


"""
Tag Maps Clustering Package

Package to cluster data (locations, tags or emoji)
and output shapefile containing Alpha Shapes
and statistics.

Package can be executed directly (__main__) or
imported using from tagmaps import TagMaps as TM
"""

from __future__ import absolute_import

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"


import sys
import time

from tagmaps.tagmaps_ import TagMaps
from tagmaps.classes.load_data import LoadData
from tagmaps.classes.utils import Utils
from tagmaps.config.config import BaseConfig


def main():
    """Main tag maps method for direct execution of package.

    The order of execution is pretty linear:
        1. LoadData (apply basic filters, stoplists etc.) - /01_Input/
        2. PrepareData (global statistics, remove long tail, prepare
           cleaned data structure)
        3. Optional: user input for cluster distance/item selection
        4. Cluster Step: calculate itemized / global clusters
        5. Alpha Shapes: for each cluter, calculate spatial shape/ boundary
        6. Compile Output: normalize results, add statistics, shapefile
        7. Write results: Write Shapefile to file  - /02_Output/
    """

    # initialize config from args
    cfg = BaseConfig()
    # init main procedure settings
    Utils.init_main()

    print('\n')
    # set logger with file pointer

    log = Utils.set_logger(cfg.output_folder, cfg.logging_level)
    log.info(
        "########## "
        "STEP 1 of 6: Data Cleanup "
        "##########")
    input_data = LoadData(
        cfg, user_variety_input=True, console_reporting=True)
    # initialize tag maps
    tagmaps = TagMaps(
        tag_cluster=cfg.cluster_tags,
        emoji_cluster=cfg.cluster_emoji,
        location_cluster=cfg.cluster_locations,
        output_folder=cfg.output_folder,
        remove_long_tail=cfg.remove_long_tail,
        limit_bottom_user_count=cfg.limit_bottom_user_count,
        topic_modeling=cfg.topic_modeling,
        local_saturation_check=cfg.local_saturation_check,
        max_items=cfg.max_items,
        logging_level=cfg.logging_level)

    if cfg.load_from_intermediate or input_data.is_intermediate():
        # load data from intermediate (already filtered) results
        if not cfg.load_from_intermediate:
            # if path empty, get first file
            filename = next(iter(input_data.filelist))
            cfg.write_cleaned_data = False
        else:
            filename = cfg.load_from_intermediate
        tagmaps.load_intermediate(input_path=filename)
    else:
        # read and process unfiltered input records from csv
        with input_data as records:
            for record in records:
                tagmaps.add_record(record)
        # get statistics for
        # unfiltered input data
        input_data.input_stats_report()

    # prepare loaded data for clustering
    tagmaps.prepare_data()
    # show statistics for ingested data
    tagmaps.global_stats_report()

    # get current time for monitoring
    now = time.time()

    if (cfg.cluster_tags or cfg.cluster_emoji):
        log.info(
            "\n########## "
            "STEP 2 of 6: Tag Ranking "
            "##########")
    # calculate and report item stats
    tagmaps.item_stats_report()

    if cfg.write_cleaned_data and not cfg.load_from_intermediate:
        # write intermediate results
        tagmaps.write_cleaned_data()
        # tagmaps.write_toplists()
        if cfg.topic_modeling:
            tagmaps.write_topics()

    if cfg.statistics_only is False:
        # restart time monitoring for
        # actual cluster step
        now = time.time()
        log.info(
            "\n########## "
            "STEP 3 of 6: Tag & Emoji "
            "Location Clustering "
            "##########")
        # get user input for cluster distances
        continue_proc = True
        if not cfg.auto_mode:
            # open user interface for optional user input
            continue_proc = tagmaps.user_interface()

        if continue_proc is True:
            tagmaps.cluster_tags()
            tagmaps.cluster_emoji()
            log.info(
                "########## "
                "STEP 4 of 6: Generating Alpha Shapes "
                "##########")
            tagmaps.gen_tagcluster_shapes()
            tagmaps.gen_emojicluster_shapes()
            log.info(
                "########## "
                "STEP 5 of 6: Writing Results to Shapefile "
                "##########")
            tagmaps.write_tagemoji_shapes()
        else:
            print(f'\nUser abort.')
    if cfg.cluster_locations and continue_proc is True:
        log.info(
            "\n########## "
            "STEP 6 of 6: Calculating Overall Location Clusters "
            "##########")
        tagmaps.cluster_locations()
        tagmaps.gen_location_centroids()
        tagmaps.write_location_shapes()

    # time reporting
    later = time.time()
    hours, rem = divmod(later-now, 3600)
    minutes, seconds = divmod(rem, 60)
    # difference = int(later - now)
    log.info(f'\nDone.\n{int(hours):0>2} Hours '
             f'{int(minutes):0>2} Minutes and '
             f'{seconds:05.2f} Seconds passed.')
    if not cfg.auto_mode:
        input("Press any key to exit...")
    sys.exit(0)


if __name__ == "__main__":
    main()
