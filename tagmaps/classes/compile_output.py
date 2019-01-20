# -*- coding: utf-8 -*-

"""
Module for compiling TagMaps results and writing output
"""

import fiona
from fiona.crs import from_epsg
import shapely.geometry as geometry
from typing import List, Set, Dict, Tuple, Optional, TextIO
from collections import namedtuple
from tagmaps.classes.utils import Utils
from tagmaps.classes.shared_structure import (AnalysisBounds,
                                              TAGS, LOCATIONS, EMOJI)


class Compile():

    @classmethod
    def write_shapes(cls,
                     bounds: AnalysisBounds,
                     shapes_and_meta_list):
        """Main wrapper for writing
        all results to output

        shapes_and_meta_list is either:
        - List[[Tuple[List[],cls_type, itemized: bool = True]]]
        or:
          List[[Tuple[List[],cls_type, itemized: bool = False]]]
          (overall clusters)
        """
        bound_points_shapely = Utils._get_shapely_bounds(
            bounds)
        # data always in lat/lng WGS1984
        __, epsg_code = Utils._get_best_utmzone(
            bound_points_shapely)
        cls._shape_writer_select(shapes_and_meta_list, epsg_code)

    @classmethod
    def _shape_writer_select(cls, shapes_and_meta_list,
                             epsg_code):
        """Wrapper to select different shape writer for itemized and
        not itemized cluster results"""
        itemized_shapes = list()
        non_itemized_shapes = list()
        for shapes_and_meta, cls_type, itemized in shapes_and_meta_list:
            if itemized:
                itemized_shapes.append(
                    (shapes_and_meta, cls_type))
            else:
                non_itemized_shapes.append(
                    (shapes_and_meta, cls_type))
        if itemized_shapes:
            cls._shape_writer(itemized_shapes,
                              epsg_code, True)
        if non_itemized_shapes:
            cls._shape_writer(non_itemized_shapes,
                              epsg_code, False)

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

    @classmethod
    def _shape_writer(cls, shapes_and_meta_list,
                      epsg_code, itemized):
        # Initialize a new Shapefile
        # WGS1984
        schema = cls._get_shape_schema(itemized)
        # better parametrization needed here:
        # select name based on cls_type, not itemized
        contains_emoji_output = cls._contains_emoji_output(
            shapes_and_meta_list)
        if itemized:
            if (contains_emoji_output and
                    len(shapes_and_meta_list) == 1):
                # if only emoji output
                shapefile_name = "allEmojiCluster"
            else:
                # if writing only tags
                # or tags and emoji
                shapefile_name = "allTagCluster"
        else:
            shapefile_name = "allLocationCluster"
        with fiona.open(
            f'02_Output/{shapefile_name}.shp', mode='w',
            encoding='UTF-8', driver='ESRI Shapefile',
                schema=schema, crs=from_epsg(epsg_code)) as shapefile:
            cls._attach_emojitable_handler(
                shapefile,
                shapes_and_meta_list,
                epsg_code, schema,
                contains_emoji_output,
                itemized)

    @classmethod
    def _attach_emojitable_handler(cls, shapefile,
                                   shapes_and_meta_list,
                                   epsg_code, schema,
                                   contains_emoji_output,
                                   itemized):
        """If Emoji Output present, open csv for writing
        Note: refactor as optional property!
        """
        if contains_emoji_output:
            with open("02_Output/emojiTable.csv",
                      "w", encoding='utf-8') as emoji_table:
                emoji_table.write("FID,Emoji\n")
                cls._loop_shapemetalist(shapefile,
                                        shapes_and_meta_list,
                                        epsg_code, schema,
                                        emoji_table,
                                        itemized)
        else:
            cls._loop_shapemetalist(shapefile,
                                    shapes_and_meta_list,
                                    epsg_code, schema,
                                    None, itemized)

    @staticmethod
    def _contains_emoji_output(shapes_and_meta_list):
        """Check if emoji type is in output list"""
        contains_emoji_output = False
        for __, output_type in shapes_and_meta_list:
            if output_type == EMOJI:
                contains_emoji_output = True
        return contains_emoji_output

    @classmethod
    def _loop_shapemetalist(cls, shapefile, shapes_and_meta_list,
                            epsg_code, schema, emoji_table: TextIO,
                            itemized):
        for shapes, cls_type in shapes_and_meta_list:
            if itemized:
                # normalize types separately (e.g. emoji/tags)
                global_weights = cls._get_weights(shapes, [6, 7, 8])
                cls._write_itemized_shapes(
                    shapefile, shapes,
                    cls_type, global_weights, emoji_table)
            else:
                # normalize types separately (e.g. emoji/tags)
                global_weights = cls._get_weights(shapes, [1])
                cls._write_nonitemized_shapes(
                    shapefile, shapes,
                    cls_type, global_weights, emoji_table)

    @classmethod
    def _write_nonitemized_shapes(
            cls, shapefile,
            shapes, cls_type,
            weights: Dict[int, Tuple[float, float]],
            emoji_table: TextIO
    ):
        for alphashape_and_meta in shapes:
            local_value = alphashape_and_meta[1]
            local_value_normalized = cls._get_normalize_value(
                local_value, weights.get(1))
            shapefile.write({
                'geometry': geometry.mapping(alphashape_and_meta[0]),
                'properties': {'Join_Count': alphashape_and_meta[1],
                               'Weights': local_value_normalized},
            })

    @classmethod
    def _write_itemized_shapes(
            cls, shapefile,
            shapes, cls_type,
            weights: Dict[int, Tuple[float, float]],
            emoji_table: TextIO):
        """Main wrapper for writing
        all results to output
        """
        # Normalize Weights to 0-1000 Range
        idx = 0
        for alphashape_and_meta in shapes:
            h_imp = cls._get_himp(idx, shapes)
            idx += 1
            cls._write_shape(
                shapefile, alphashape_and_meta,
                cls_type, weights, h_imp)
            if emoji_table:
                cls._write_emoji_table(idx,
                                       alphashape_and_meta,
                                       emoji_table,
                                       cls_type == EMOJI)

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
        if (idx == 0 or
                shapes[idx][4] != shapes[idx-1][4]):
            h_imp = 1
        else:
            h_imp = 0
        return h_imp

    @staticmethod
    def _write_emoji_table(idx, alphashape_and_meta, emoji_table,
                           is_emoji):
        """Write Emoji table separetely to join to shapefile"""
        imp_tag_text = f'{alphashape_and_meta[4]}'
        if is_emoji:
            imp_tag_text = f'{alphashape_and_meta[4]}'
        else:
            # also write tags as empty
            # records to table, necessary
            # for accurate join/ fid count
            imp_tag_text = ""
        emoji_table.write(
            f'{idx},{imp_tag_text}\n')

    @classmethod
    def _write_shape(
            cls, shapefile,
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
            imp_tag_text = ""
        else:
            emoji = 0
            imp_tag_text = f'{alphashape_and_meta[4]}'
        shapefile.write({
            'geometry': geometry.mapping(alphashape_and_meta[0]),
            'properties': {'Join_Count': alphashape_and_meta[1],
                           'Views': alphashape_and_meta[2],
                           'COUNT_User': alphashape_and_meta[3],
                           'ImpTag': imp_tag_text,
                           'TagCountG': alphashape_and_meta[5],
                           'HImpTag': h_imp,
                           'Weights': weight1_normalized,
                           'WeightsV2': weight2_normalized,
                           'WeightsV3': weight3_normalized,
                           # 'shapetype': alphaShapeAndMeta[9],
                           'emoji': emoji},
        })

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
        return weights_dict

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
