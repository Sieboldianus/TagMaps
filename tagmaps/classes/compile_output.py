# -*- coding: utf-8 -*-

"""
Module for compiling TagMaps results and writing output
"""

from __future__ import absolute_import

from operator import itemgetter
from pathlib import Path
from typing import Dict, List, TextIO, Tuple
from math import sqrt

import shapely.geometry as geometry
import fiona
from fiona.crs import from_epsg

from tagmaps.classes.shared_structure import (EMOJI,
                                              AnalysisBounds)
from tagmaps.classes.utils import Utils


class Compile():
    """Compile results into shapefiles, add statistics, normalize."""
    @classmethod
    def write_shapes(cls,
                     bounds: AnalysisBounds,
                     shapes_and_meta_list,
                     output_folder: Path):
        """Main wrapper for writing
        all results to output

        shapes_and_meta_list is either:
        - List[[Tuple[List[],cls_type, itemized: bool = True]]]
        or:
          List[[Tuple[List[],cls_type, itemized: bool = False]]]
          (overall clusters)
        - List[] contains clustered shapes from ClusterGen and
            attached statistic information
        TODO: refactor into compile & write shapes; update output_folder
        """
        if output_folder:
            print("")
        bound_points_shapely = Utils.get_shapely_bounds(
            bounds)
        # data always in lat/lng WGS1984
        __, epsg_code = Utils.get_best_utmzone(
            bound_points_shapely)
        cls._compile_merge_shapes(shapes_and_meta_list, epsg_code)

    @classmethod
    def _compile_merge_shapes(cls, shapes_and_meta_list,
                              epsg_code):
        all_itemized_shapes = list()
        all_non_itemized_shapes = list()
        contains_emoji_output = False
        for shapes, cls_type, itemized in shapes_and_meta_list:
            if not shapes:
                continue
            if itemized:
                if cls_type == EMOJI:
                    contains_emoji_output = True
                # normalize types separately (e.g. emoji/tags)
                global_weights = cls._get_weights(shapes, [6, 7, 8])
                itemized_shapes = cls._getcompile_itemized_shapes(
                    shapes, cls_type, global_weights)
                # print(f'type itemized_shapes: {type(itemized_shapes)}\n')
                all_itemized_shapes.extend(itemized_shapes)
            else:
                global_weights = cls._get_weights(shapes, [1])
                non_itemized_shapes = cls._getcompile_nonitemized_shapes(
                    shapes, global_weights)
                all_non_itemized_shapes.extend(non_itemized_shapes)
        # writing step:
        if all_itemized_shapes:
            cls._write_all(
                all_itemized_shapes, True,
                contains_emoji_output, epsg_code)
        if all_non_itemized_shapes:
            cls._write_all(
                all_non_itemized_shapes, False,
                contains_emoji_output, epsg_code)

    @staticmethod
    def _get_shape_schema(itemized):
        """Define polygon feature geometry"""
        if itemized:
            schema = {
                'geometry': 'Polygon',
                'properties': {'Join_Count': 'int',
                               'Views': 'int',
                               'COUNT_User': 'int',
                               'ImpTag': 'str',
                               'TagCountG': 'int',
                               'HImpTag': 'int',
                               'Weights': 'float',
                               'WeightsV2': 'float',
                               'WeightsV3': 'float',
                               # 'shapetype': 'str',
                               'emoji': 'int'},
            }
        else:
            # Define a polygon feature geometry with one attribute
            schema = {
                'geometry': 'Point',
                'properties': {'Join_Count': 'int',
                               'Weights': 'float'},
            }
        return schema

    @staticmethod
    def _contains_emoji_output(shapes_and_meta_list):
        """Check if emoji type is in output list"""
        contains_emoji_output = False
        for __, output_type in shapes_and_meta_list:
            if output_type == EMOJI:
                contains_emoji_output = True
        return contains_emoji_output

    @classmethod
    def _getcompile_nonitemized_shapes(
            cls, shapes,
            weights: Dict[int, Tuple[float, float]],
    ):
        """Compilation of final records to be

        written to shapefile. Includes normalization
        of values"""
        shapelist = list()
        for alphashape_and_meta in shapes:
            local_value = alphashape_and_meta[1]
            local_value_normalized = cls._get_normalize_value(
                local_value, weights.get(1))
            # each part of the tuple is
            # one column in output shapefile
            shapelist.append(
                (alphashape_and_meta[0],
                 alphashape_and_meta[1],
                 local_value_normalized))
        return shapelist

    @classmethod
    def _write_all(cls, shapes, itemized,
                   contains_emoji_output, epsg_code):
        schema = cls._get_shape_schema(itemized)
        # update for emoji only run
        if itemized:
            shapefile_name = "allTagCluster"
            # sort shapelist by firstg column,
            # in descending order
            # we want most important tags places first
            shapes.sort(key=itemgetter(7), reverse=True)
        else:
            shapefile_name = "allLocationCluster"
            # sort ascending, we want smalles clusters places
            # first as small points, overlayed by larger ones
            shapes.sort(key=itemgetter(2))
        with fiona.open(
                f'02_Output/{shapefile_name}.shp', mode='w',
                encoding='UTF-8', driver='ESRI Shapefile',
                schema=schema, crs=from_epsg(epsg_code)) as shapefile:
            cls._attach_emojitable_handler(
                shapefile,
                shapes,
                contains_emoji_output,
                itemized)

    @classmethod
    def _attach_emojitable_handler(cls, shapefile,
                                   shapes,
                                   contains_emoji_output,
                                   itemized):
        """If Emoji Output present, open csv for writing
        Note: refactor as optional property!
        """
        if contains_emoji_output:
            # If newline is '', no translation takes place on write
            # that means: \n (LF) is written, not CRLF
            with open("02_Output/emojiTable.csv",
                      "w", newline='', encoding='utf-8') as emoji_table:
                emoji_table.write("FID,Emoji\n")
                if itemized:
                    cls._write_all_shapes(
                        shapefile, shapes,
                        emoji_table, itemized)

        else:
            cls._write_all_shapes(
                shapefile, shapes, None, itemized)

    @classmethod
    def _write_all_shapes(cls, shapefile, shapes,
                          emoji_table: TextIO,
                          itemized: bool):
        fid = 0
        for shape in shapes:
            if itemized:
                # check if colum 10 is set to 1
                # == emoji record
                if shape[10] == 1:
                    is_emoji_record = True
                else:
                    is_emoji_record = False
                cls._write_itemized_shape(
                    shapefile, shape, is_emoji_record)
                if emoji_table:
                    cls._write_emoji_record(
                        fid,
                        shape,
                        emoji_table,
                        is_emoji_record)
                    fid += 1
            else:
                cls._write_nonitemized_shape(
                    shapefile, shape)

    @staticmethod
    def _write_nonitemized_shape(shapefile, shape):
        shapefile.write({
            'geometry': geometry.mapping(shape[0]),
            'properties': {'Join_Count': shape[1],
                           'Weights': shape[2]},
        })

    @staticmethod
    def _write_itemized_shape(shapefile, shape, is_emoji_record):
        """Append final record to shape"""
        # do not write emoji to shapefile directly
        # bug in Arcgis, needs to be imported
        # using join
        if is_emoji_record:
            imptag = ""
        else:
            imptag = shape[4]
        shapefile.write({
            'geometry': geometry.mapping(shape[0]),
            'properties': {'Join_Count': shape[1],
                           'Views': shape[2],
                           'COUNT_User': shape[3],
                           'ImpTag': imptag,
                           'TagCountG': shape[5],
                           'HImpTag': shape[6],
                           'Weights': shape[7],
                           'WeightsV2': shape[8],
                           'WeightsV3': shape[9],
                           # 'shapetype': alphaShapeAndMeta[9],
                           'emoji': shape[10]},
        })

    @classmethod
    def _getcompile_itemized_shapes(
            cls, shapes, cls_type,
            weights: Dict[int, Tuple[float, float]]):
        """Main wrapper for writing
        all results to output
        """
        # Normalize Weights to 0-1000 Range
        idx = 0
        shapelist = list()
        for alphashape_and_meta in shapes:
            h_imp = cls._get_himp(idx, shapes)
            idx += 1
            item_shape = cls._getcompile_item_shape(
                alphashape_and_meta,
                cls_type, weights, h_imp)
            shapelist.append((item_shape))
        return shapelist

    @staticmethod
    def _get_himp(idx, shapes):
        """check if current cluster is most
        used for item
        Compares item str to previous item,
        if different, then himp=1
        Note: Items are ordered,
        therefore a change means
        new item begins
        """
        if ((idx == 0
             or shapes[idx][4] != shapes[idx-1][4])
                and not shapes[idx][2] == 1):
            # if item is different to
            # previous item and
            # user count is not 1
            h_imp = 1
        else:
            h_imp = 0
        return h_imp

    @staticmethod
    def _write_emoji_record(fid, shape, emoji_table,
                            is_emoji):
        """Write Emoji table separetely to join to shapefile"""
        if is_emoji:
            imp_tag_text = f'{shape[4]}'
        else:
            # also write tags as empty
            # records to table, necessary
            # for accurate join/ fid count
            imp_tag_text = ""
        emoji_table.write(
            f'{fid},{imp_tag_text}\n')

    @classmethod
    def _getcompile_item_shape(
            cls,
            alphashape_and_meta, cls_type,
            weights: Dict[int, Tuple[float, float]],
            h_imp):

        # emoName = unicode_name(alphaShapeAndMeta[4])
        # Calculate Normalized Weights Values based on precalc Step
        value_weight1 = alphashape_and_meta[6]
        weight1_normalized = cls._get_normalize_value(
            value_weight1, weights.get(1))
        value_weight2 = alphashape_and_meta[7]
        weight2_normalized = cls._get_normalize_value(
            value_weight2, weights.get(2))
        value_weight3 = alphashape_and_meta[8]
        weight3_normalized = cls._get_normalize_value(
            value_weight3, weights.get(3))
        # project data
        # geom_proj = transform(project, alphaShapeAndMeta[0])
        # c.write({
        #    'geometry': geometry.mapping(geom_proj),
        if cls_type == EMOJI:
            emoji = 1
            # due to bug in ArcGIS
            # leave blank
            # emoji must be imported separately
            # imp_tag_text = ""
        else:
            emoji = 0
            # imp_tag_text = f'{alphashape_and_meta[4]}'
        item_shape = (
            alphashape_and_meta[0],
            alphashape_and_meta[1],
            alphashape_and_meta[2],
            alphashape_and_meta[3],
            alphashape_and_meta[4],
            alphashape_and_meta[5],
            h_imp,
            weight1_normalized,
            weight2_normalized,
            weight3_normalized,
            emoji
        )
        return item_shape

    @classmethod
    def _get_weights(cls, shapes, columns: List[int]):
        """Normalization of Values (1-1000 Range),
        precalc Step (global weights),
        see
        https://stats.stackexchange.com/questions/70801/how-to-normalize-data-to-0-1-range
        """
        idx = 1
        weights_dict: Dict[int, Tuple[float, float]] = dict()
        for column in columns:
            # int: weights algorithm
            # Tuple: min and max modifiers
            values_min, values_max = cls._get_column_min_max(
                shapes, column)
            weights_mod_a = (1000-1)/(
                values_max-values_min)
            weights_mod_b = 1000 - weights_mod_a * values_max
            weights_dict[idx] = (weights_mod_a, weights_mod_b)
            idx += 1
        cls._write_legend_info(weights_dict)
        return weights_dict

    @staticmethod
    def _write_legend_info(weights_dict):
        """Helper Function for updating ArcGIS legend
        - not implemented
        """
        if not weights_dict:
            return
        return

    @staticmethod
    def _get_column_min_max(
            shapes,
            column: int) -> Tuple[float, float]:
        """Get min and max values of specific column
        for normalization"""
        # get the n'th column out for calculating the max/min
        weights_range = [x[column] for x in shapes]
        weights_min = min(weights_range)
        weights_max = max(weights_range)
        return weights_min, weights_max

    @staticmethod
    def _normalize_value(
            weights,
            local_value):
        """Normalize value based on global weights"""
        mul_mod = weights[0]
        sum_mod = weights[1]
        normalized_value = mul_mod * local_value + sum_mod
        return normalized_value

    @classmethod
    def _get_normalize_value(cls, local_value,
                             weights_tuple: Tuple[float, float]):
        """Wrapper for Normalization: keep 1,
        otherwise, normalize"""
        if local_value == 1:
            value_normalized = local_value
        else:
            value_normalized = cls._normalize_value(
                weights_tuple, local_value)
        return value_normalized

    @staticmethod
    def get_weight(weighting_id: int,
                   post_count: int,
                   unique_user_count: int):
        """Get Weight for input metrics
        user count and post count based on
        three types of weighting formulas (id):
        1: weightsv1 -> Standard weighting formula
           (x**y means x raised to the power y);
           +1 to UserCount: prevent 1-2
           Range from being misaligned
        2: weightsv2 -> less importance
           on User_Count compared
           to photo count [Join_Count];
           +1 to UserCount: prevent 1-2
           Range from being misaligned
        3: weightsv3 -> Ignores User_Count,
           this will emphasize individual
           and very active users
        """
        if weighting_id == 1:
            weighted_value = post_count * (
                sqrt(1/(post_count / (
                    unique_user_count+1))**3))
        elif weighting_id == 2:
            weighted_value = post_count * (
                sqrt(1/(post_count / (
                    unique_user_count+1))**2))
        elif weighting_id == 3:
            weighted_value = sqrt(
                (post_count+(2*sqrt(post_count)))*2)
        return weighted_value
