# -*- coding: utf-8 -*-


"""
Tag Maps Clustering Package

Package to cluster data (locations, tags or emoji)
and output shapefile containing Alpha Shapes
and statistics.

Package can be executed directly (__main__) or
imported using from tagmaps import tagmaps.TagMaps as TM
"""

__author__ = "Alexander Dunkel"
__license__ = "GNU GPLv3"

import sys
import time

from tagmaps.classes.cluster import ClusterGen
from tagmaps.classes.compile_output import Compile
from tagmaps.classes.interface import UserInterface
from tagmaps.classes.load_data import LoadData
from tagmaps.classes.shared_structure import EMOJI, LOCATIONS, TAGS
from tagmaps.classes.utils import Utils


def main():
    """Main tag maps function for direct execution of package

    - will read from 01_Input/ folder
    - will output clustered data to 02_Output/
    """

    # initialize logger and config
    cfg, log = Utils.init_main()
    lbsn_data = LoadData(cfg)

    print('\n')
    log.info(
        "########## "
        "STEP 1 of 6: Data Cleanup "
        "##########")

    lbsn_data.parse_input_records()
    # get current time
    now = time.time()
    # get cleaned data for use in clustering
    cleaned_post_dict = lbsn_data.get_cleaned_post_dict()
    cleaned_post_list = list(cleaned_post_dict.values())
    # status report
    log.info(
        f'\nTotal user count (UC): '
        f'{len(lbsn_data.locations_per_userid_dict)}')
    log.info(
        f'Total post count (PC): '
        f'{lbsn_data.stats.count_glob:02d}')
    log.info(
        f'Total tag count (PTC): '
        f'{lbsn_data.stats.count_tags_global}')
    log.info(
        f'Total emoji count (PEC): '
        f'{lbsn_data.stats.count_emojis_global}')
    log.info(
        f'Total user post locations (UPL): '
        f'{len(lbsn_data.distinct_userlocations_set)}')
    log.info(
        lbsn_data.bounds.get_bound_report())

    # get prepared data for statistics and clustering
    prepared_data = lbsn_data.get_prepared_data()

    if (cfg.cluster_tags or cfg.cluster_emoji):
        log.info(
            "\n########## "
            "STEP 2 of 6: Tag Ranking "
            "##########")

        location_name_count = len(
            prepared_data.locid_locname_dict)
        if location_name_count > 0:
            log.info(
                f"Number of locations with names: "
                f"{location_name_count}")

        log.info(
            f'Total distinct tags (DTC): '
            f'{prepared_data.total_unique_tags}')
        log.info(
            f'Total distinct emoji (DEC): '
            f'{prepared_data.total_unique_emoji}')
        log.info(
            f'Total distinct locations (DLC): '
            f'{prepared_data.total_unique_locations}')
        log.info(
            f'Total tags count for the '
            f'{prepared_data.tmax} '
            f'most used tags in selected area: '
            f'{prepared_data.total_tag_count}.')
        log.info(
            f'Total emoji count for the '
            f'{prepared_data.emax} '
            f'most used emoji in selected area: '
            f'{prepared_data.total_emoji_count}.')

    if cfg.statistics_only is False:
        # restart time monitoring for monitoring of
        # actual cluster step
        now = time.time()
        log.info(
            "\n########## "
            "STEP 3 of 6: Tag & Emoji "
            "Location Clustering "
            "##########")
        # initialize list of types to cluster
        cluster_types = list()
        if cfg.cluster_tags:
            cluster_types.append(TAGS)
        if cfg.cluster_emoji:
            cluster_types.append(EMOJI)
        if cfg.cluster_locations:
            cluster_types.append(LOCATIONS)

        # initialize clusterers
        clusterer_list = list()
        for cls_type in cluster_types:
            clusterer = ClusterGen.new_clusterer(
                clusterer_type=cls_type,
                bounds=lbsn_data.bounds,
                cleaned_post_dict=cleaned_post_dict,
                cleaned_post_list=cleaned_post_list,
                prepared_data=prepared_data,
                local_saturation_check=cfg.local_saturation_check
            )
            clusterer_list.append(clusterer)

        # get user input for cluster distances
        if not cfg.auto_mode:
            user_intf = UserInterface(
                clusterer_list,
                prepared_data.locid_locname_dict)
            user_intf.start()

        if cfg.auto_mode or user_intf.abort is False:
            for clusterer in clusterer_list:
                if clusterer.cls_type == LOCATIONS:
                    # skip location clustering for now
                    continue
                if clusterer.cls_type == TAGS:
                    log.info("Tag clustering: ")
                else:
                    log.info("Emoji clustering: ")
                clusterer.get_itemized_clusters()
            log.info(
                "########## "
                "STEP 4 of 6: Generating Alpha Shapes "
                "##########")
            # store results for tags and emoji in one list
            shapes_and_meta_list = list()
            for clusterer in clusterer_list:
                if clusterer.cls_type == LOCATIONS:
                    # skip location clustering for now
                    continue
                cluster_shapes = clusterer.get_cluster_shapes()
                shapes_and_meta_list.append(cluster_shapes)
            log.info(
                "########## "
                "STEP 5 of 6: Writing Results to Shapefile "
                "##########")
            Compile.write_shapes(
                bounds=lbsn_data.bounds,
                shapes_and_meta_list=shapes_and_meta_list)
        else:
            print(f'\nUser abort.')
    if cfg.cluster_locations and user_intf.abort is False:
        log.info(
            "\n########## "
            "STEP 6 of 6: Calculating Overall Location Clusters "
            "##########")
        shapes_and_meta_list.clear()
        for clusterer in clusterer_list:
            if clusterer.cls_type == LOCATIONS:
                clusterer.get_overall_clusters()
                cluster_shapes = clusterer.get_cluster_centroids()
                shapes_and_meta_list.append(cluster_shapes)
        Compile.write_shapes(
            bounds=lbsn_data.bounds,
            shapes_and_meta_list=shapes_and_meta_list)
    # time reporting
    later = time.time()
    hours, rem = divmod(later-now, 3600)
    minutes, seconds = divmod(rem, 60)
    # difference = int(later - now)
    log.info(f'\nDone.\n{int(hours):0>2} Hours '
             f'{int(minutes):0>2} Minutes and '
             f'{seconds:05.2f} Seconds passed.')
    input("Press any key to exit...")
    sys.exit()


if __name__ == "__main__":
    main()
