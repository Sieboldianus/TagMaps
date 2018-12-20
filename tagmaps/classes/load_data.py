# -*- coding: utf-8 -*-

import os
import ntpath
import csv
from _csv import QUOTE_MINIMAL
from glob import glob
from .utils import Utils

class LoadData():
    """Main Class for ingesting data and building summary statistics
    for tag maps clustering.

    - will filter data, cleaned output can be stored
    - will process CSV data into dict/set structures
    - generate statistics
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
    def fetch_csv_data_from_file(loc_filelist, start_file_id=0):
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
    def skip_empty_or_other(single_record):
        """Detect  Rate Limiting Notice or empty records
           so they can be skipped.
        """
        skip = False
        if not single_record or (isinstance(single_record,dict) and single_record.get('limit')):
            skip = True
        return skip
