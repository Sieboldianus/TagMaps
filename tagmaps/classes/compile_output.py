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
        """
        bound_points_shapely = Utils._get_shapely_bounds(
            bounds)
        # data always in lat/lng WGS1984
        __, epsg_code = Utils._get_best_utmzone(
            bound_points_shapely)

        # Define polygon feature geometry
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
        cls._shape_writer(schema,
                          shapes_and_meta_list, epsg_code)

    @classmethod
    def _shape_writer(cls, schema,
                      shapes_and_meta_list, epsg_code):
        # Initialize a new Shapefile
        # WGS1984

        contains_emoji_output = cls._contains_emoji_output(
            shapes_and_meta_list)
        if (contains_emoji_output and len(shapes_and_meta_list) == 1):
            # if only emoji output
            shapefile_name = "allEmojiCluster"
        else:
            # if writing only tags
            # or tags and emoji
            shapefile_name = "allTagCluster"
        with fiona.open(
            f'02_Output/{shapefile_name}.shp', mode='w',
            encoding='UTF-8', driver='ESRI Shapefile',
                schema=schema, crs=from_epsg(epsg_code)) as shapefile:
            cls._attach_emojitable_handler(
                shapefile,
                shapes_and_meta_list,
                epsg_code, schema,
                contains_emoji_output)

    @classmethod
    def _attach_emojitable_handler(cls, shapefile,
                                   shapes_and_meta_list,
                                   epsg_code, schema,
                                   contains_emoji_output):
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
                                        emoji_table)
        else:
            cls._loop_shapemetalist(shapefile,
                                    shapes_and_meta_list,
                                    epsg_code, schema,
                                    None)

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
                            epsg_code, schema, emoji_table: TextIO):
        for shapes, cls_type in shapes_and_meta_list:
            # normalize types separately (e.g. emoji/tags)
            global_weights = cls._get_weights(shapes)
            cls._write_shapes(
                shapefile, shapes,
                cls_type, global_weights, emoji_table)

    @classmethod
    def _write_shapes(
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
    def write_centroids(cls,
                        bounds: AnalysisBounds,
                        cluster_centroids):

        bound_points_shapely = Utils._get_shapely_bounds(
            bounds)
        # data always in lat/lng WGS1984
        __, epsg_code = Utils._get_best_utmzone(
            bound_points_shapely)

        # Define a polygon feature geometry with one attribute
        schema = {
            'geometry': 'Point',
            'properties': {'Join_Count': 'int'},
        }

        # Write a new Shapefile
        # WGS1984
        with fiona.open('02_Output/allPhotoCluster.shp',
                        mode='w',
                        driver='ESRI Shapefile', schema=schema,
                        crs=from_epsg(epsg_code)) as c:
            # If there are multiple geometries, put the "for" loop here
            idx = 0
            for cluster_centroid in cluster_centroids:
                idx += 1
                c.write({
                    'geometry': geometry.mapping(cluster_centroid[0]),
                    'properties': {'Join_Count': cluster_centroid[1]},
                })

    @staticmethod
    def _get_weights(shapes):
        """Normalization of Values (1-1000 Range),
        precalc Step (global weights)
        """
        # get the n'th column out for calculating the max/min
        weightsv1_range = [x[6] for x in shapes]
        weightsv2_range = [x[7] for x in shapes]
        weightsv3_range = [x[8] for x in shapes]
        weightsv1_min = min(weightsv1_range)
        weightsv1_max = max(weightsv1_range)
        weightsv2_min = min(weightsv2_range)
        weightsv2_max = max(weightsv2_range)
        weightsv3_min = min(weightsv3_range)
        weightsv3_max = max(weightsv3_range)
        # precalc, see
        # https://stats.stackexchange.com/questions/70801/how-to-normalize-data-to-0-1-range

        # int: weights algorithm
        # Tuple: min and max modifiers
        weights: Dict[int, Tuple[float, float]] = dict()
        weightsv1_mod_a = (1000-1)/(
            weightsv1_max-weightsv1_min)
        weightsv1_mod_b = 1000 - weightsv1_mod_a * weightsv1_max
        weights[1] = (weightsv1_mod_a, weightsv1_mod_b)
        weightsv2_mod_a = (1000-1)/(
            weightsv2_max-weightsv2_min)
        weightsv2_mod_b = 1000 - weightsv2_mod_a * weightsv2_max
        weights[2] = (weightsv2_mod_a, weightsv2_mod_b)
        weightsv3_mod_a = (1000-1)/(
            weightsv3_max-weightsv3_min)
        weightsv3_mod_b = 1000 - weightsv3_mod_a * weightsv3_max
        weights[3] = (weightsv3_mod_a, weightsv3_mod_b)
        return weights

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
