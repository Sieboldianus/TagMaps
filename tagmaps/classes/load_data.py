# -*- coding: utf-8 -*-

import sys
import os
import ntpath
import csv
from pathlib import Path
from _csv import QUOTE_MINIMAL
from glob import glob
from .utils import Utils

class LoadData():
    """Main Class for ingesting data and building summary statistics.

    - will process CSV data into dict/set structures
    - will filter data, cleaned output can be stored
    - will generate statistics
    """

    def loop_input_records(records, transferlimit, import_mapper, config):
        """Loops input json or csv records, converts to ProtoBuf structure and adds to records_dict

        Returns statistic-counts, modifies (adds results to) import_mapper
        """

        finished = False
        processed_records = 0
        db_row_number = 0
        for record in records:
            processed_records += 1
            if config.is_local_input:
                single_record = record
            else:
                db_row_number = record[0]
                single_record = record[2]
            if LoadData.skip_empty_or_other(single_record):
                continue
            if config.local_file_type == 'json' or not config.is_local_input:
                import_mapper.parseJsonRecord(single_record, config.input_lbsn_type)
            elif config.local_file_type in ('txt','csv'):
                import_mapper.parse_csv_record(single_record)
            else:
                exit(f'Format {config.local_file_type} not supportet.')

            if (transferlimit and processed_records >= transferlimit) or \
               (not config.is_local_input and config.end_with_db_row_number and db_row_number >= config.end_with_db_row_number):
                finished = True
                break
        return processed_records, finished

    @staticmethod
    def fetch_csv_data_from_file(source_config):
        """Read csv entries from file (either *.txt or *.csv).

        The actual CSV formatting is not setable in config yet. There are many specifics, e.g.
        #QUOTE_NONE is used here because media saved from Flickr does not contain any quotes ""
        """
        records = []
        loc_file = loc_filelist[start_file_id]
        HF.log_main_debug(f'\nCurrent file: {ntpath.basename(loc_file)}')
        with open(loc_file, 'r', encoding="utf-8", errors='replace') as file:
            reader = csv.reader(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
            next(reader, None)  # skip headerline
            records = list(reader)
        if not records:
            return None
        return records

    @staticmethod
    def read_local_files(config):
       """Read Local Files according to config parameters and returns list of file-paths"""
       input_path = config.input_folder
       filelist = list(input_path.glob(f'*.{config.source["Main"]["file_extension"]}'))
       input_count = len(filelist)
       if input_count == 0:
           sys.exit("No input files found.")
       else:
           return filelist

    @staticmethod
    def skip_empty_or_other(single_record):
        """Detect empty records"""
        if not single_record:
            return False
        return True


