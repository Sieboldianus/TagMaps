# -*- coding: utf-8 -*-

"""Module for matplotlib, seaborn, pyplot methods.
"""

from __future__ import absolute_import

from typing import Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from descartes import PolygonPatch

from tagmaps.classes.shared_structure import (EMOJI, LOCATIONS, TAGS,
                                              AnalysisBounds)
from tagmaps.classes.utils import Utils


class TPLT():
    """Tag Maps plotting Class

    To remember (because mpl/pyplot can be confusing):
        - The figure is the window that the plot is in.
          It's the top-level container. Each figure has a canvas
          where things are painted on.
        - Each figure usually has one or more axes.
          These are the plots/subplots. Here, only one axes is used.
        - Colorbars and other stuff are also inside the figure.
          Adding a colorbar creates a new axe (unless specified otherwise)
        - two modes exist, OO (object oriented) and
          pyplot("state-machine interface"),
          use OO-Mode if possible because it is more flexible and works
          better with Jupyter Mode
    for more information, see:
    https://stackoverflow.com/questions/19816820/how-to-retrieve-colorbar-instance-from-figure-in-matplotlib
    """
    PLOT_KWDS = {'alpha': 0.5, 's': 10, 'linewidths': 0}

    @staticmethod
    def _get_xy_dists(
            bounds: AnalysisBounds) -> Tuple[float, float]:
        """Get X/Y Distances from Analysis Bounds"""
        dist_y_lat = (
            bounds.lim_lat_max - bounds.lim_lat_min)
        dist_x_lng = (
            bounds.lim_lng_max - bounds.lim_lng_min)
        return dist_y_lat, dist_x_lng

    @staticmethod
    def plt_setxy_lim(axis, bounds: AnalysisBounds):
        """Set global plotting bounds basedon Analysis Bounds"""
        axis.set_xlim(
            [bounds.lim_lng_min, bounds.lim_lng_max])
        axis.set_ylim(
            [bounds.lim_lat_min, bounds.lim_lat_max])

    @staticmethod
    def get_fig_points(fig, points, bounds, point_size=None):
        """Get figure for numpy.ndarray of points"""
        if not fig:
            # create a new figure window
            fig = plt.figure(1)
            fig.add_subplot(111)
        axis = fig.get_axes()[0]
        # only one subplot (nrows, ncols, axnum)
        if point_size is not None:
            axis.scatter(points.T[0], points.T[1],
                         color='red', alpha=0.5, s=point_size, linewidths=0)
        else:
            axis.scatter(points.T[0], points.T[1],
                         color='red', **TPLT.PLOT_KWDS)
        fig.canvas.set_window_title('Preview Map')
        TPLT.plt_setxy_lim(axis, bounds)
        axis.tick_params(labelsize=10)
        return fig

    @staticmethod
    def get_sel_preview(points, item, bounds, cls_type):
        """Returns plt map for item selection preview"""
        # img_ratio = TPLT._get_img_ratio(bounds)
        fig = None
        fig = TPLT.get_fig_points(fig, points, bounds)
        TPLT.set_plt_suptitle(fig, item, cls_type)
        return fig

    @staticmethod
    def get_centroid_preview(points, item, bounds, cls_type, point_size):
        """Returns plt map for item selection preview"""
        # img_ratio = TPLT._get_img_ratio(bounds)
        fig = None
        fig = TPLT.get_fig_points(fig, points, bounds, point_size)
        TPLT.set_plt_suptitle(fig, item, cls_type)
        return fig

    @staticmethod
    def get_cluster_preview(
            points, sel_colors, item_text, bounds, mask_noisy,
            cluster_distance, number_of_clusters, auto_select_clusters=None,
            shapes=None, fig=None, cls_type=None):
        """Get cluster preview figure

        Args:
            points (numpy.ndarray): Point coordinates
            sel_colors ([type]): Cluster colors
            item_text ([type]): Text for suptitle
            bounds ([type]): Bounds of plotting area
            mask_noisy ([type]): Statistics for output of noisy clusters text
            cluster_distance ([type]): Cluster distance
            number_of_clusters (int): Total number of clusters
            auto_select_clusters ([type], optional): Defaults to None.
                If clusters have been auto-selected (no cluster distance)
            shapes ([type], optional): Defaults to None.
                Optional shapes for cluster outline/polygons.
            fig ([type], optional): Defaults to None.
                Optional figure for printing results.
            cls_type ([type], optional): Defaults to None.
                Cluster type, used to format text(s)

        Returns:
           figure [plt.fig]: Mpl Figure object
        """

        if auto_select_clusters is None:
            auto_select_clusters = False
        # img_ratio = TPLT._get_img_ratio(bounds)
        if not fig:
            fig = plt.figure(1)
            fig.add_subplot(111)
        axis = fig.get_axes()[0]
        # create main cluster points map
        axis.scatter(points.T[0], points.T[1],
                     c=sel_colors, **TPLT.PLOT_KWDS)
        fig.canvas.set_window_title('Cluster Preview')
        TPLT.set_plt_suptitle(fig, item_text, cls_type)
        dist_text = ''
        if shapes:
            for shape in shapes:
                patch = TPLT._get_poly_patch(shape)
                axis.add_patch(patch)
        if auto_select_clusters is False:
            dist_text = '@ ' + str(int(cluster_distance)) + 'm'
        axis.set_title(f'Cluster Preview {dist_text}',
                       fontsize=12, loc='center')
        noisy_txt = '{} / {}'.format(mask_noisy.sum(), len(mask_noisy))
        axis.text(bounds.lim_lng_max,
                  bounds.lim_lat_max,
                  f'{number_of_clusters} Clusters (Noise: {noisy_txt})',
                  fontsize=10, horizontalalignment='right',
                  verticalalignment='top', fontweight='bold')
        # set plotting bounds
        TPLT.plt_setxy_lim(axis, bounds)
        TPLT.set_plt_tick_params(axis)
        # define new figure so this one is not
        # overwritten in interactive notebook mode
        # plt.figure()
        return fig

    @staticmethod
    def get_single_linkage_tree_preview(
            item_text, fig, cluster_distance, cls_type):
        """Gets figure for single linkage tree from HDBSCAN results"""
        TPLT.set_plt_suptitle(fig, item_text, cls_type)
        fig.canvas.set_window_title('Single Linkage Tree')
        axis = fig.get_axes()[0]
        axis.set_title('Single Linkage Tree', fontsize=12,
                       loc='center')
        # plot cutting distance
        y_value = Utils.get_radians_from_meters(
            cluster_distance)
        axis.relim()
        xmin = axis.get_xlim()[0]
        xmax = axis.get_xlim()[1]
        axis.plot(
            [xmin, xmax], [y_value, y_value], color='k',
            label=f'Cluster (Cut) Distance {int(cluster_distance)}m'
        )
        axis.legend(fontsize=10)
        # replace y_value labels with meters text (instead of radians dist)
        axis.yaxis.set_major_formatter(FuncFormatter(TPLT.y_formatter))
        TPLT.set_plt_tick_params(axis)
        return fig

    @staticmethod
    def y_formatter(y_value, __):
        """Format radians y-labels as meters for improved legibility"""
        return f'{Utils.get_meters_from_radians(y_value):3.0f}m'

    @staticmethod
    def set_plt_suptitle(fig, item: str, cls_type):
        """Sets suptitle for plot (plt) and Cluster Type"""
        TPLT._set_pltspec_suptitle(
            fig, item, cls_type)

    @staticmethod
    def _set_pltspec_suptitle(fig, item: str, cls_type=None):
        """Sets suptitle for plot (plt)"""
        title = TPLT._get_pltspec_suptitle(item, cls_type)
        if cls_type and cls_type == EMOJI:
            plt.rcParams['font.family'] = 'DejaVu Sans'
        else:
            plt.rcParams['font.family'] = 'sans-serif'
        TPLT._set_plt_suptitle_st(fig, title)

    @staticmethod
    def _set_plt_suptitle_st(fig, title: str):
        """Set title of plt"""
        fig.suptitle(title,
                     fontsize=18, fontweight='bold')

    @staticmethod
    def _get_pltspec_suptitle(item: str, cls_type=None) -> str:
        """Gets formatted suptitle for plot

        - depending on clusterer type
        """
        if cls_type is None:
            cls_type = TAGS
        title = ""
        if cls_type == LOCATIONS:
            title = item.upper()
        elif cls_type == EMOJI:
            emoji_name = Utils.get_emojiname(item)
            title = f'{item} ({emoji_name})'
        else:
            title = item.upper()
        return title

    @staticmethod
    def set_plt_tick_params(axis):
        """Sets common plt tick params"""
        axis.tick_params(labelsize=10)

    @staticmethod
    def _get_poly_patch(polygon):
        """Returns a matplotlib polygon-patch from shapely polygon"""
        patch = PolygonPatch(polygon, fc='#999999',
                             ec='#000000', fill=True,
                             zorder=-1, alpha=0.7)
        return patch

    # @staticmethod
    # def _get_img_ratio(bounds: AnalysisBounds
    #                    ) -> float:
    #     """Gets [img] ratio form bounds."""
    #     dists = TPLT._get_xy_dists(bounds)
    #     dist_y_lat = dists[0]
    #     dist_x_lng = dists[1]
    #     # distYLat = Utils.haversine(limXMin,limYMax,limXMin,limYMin)
    #     # distXLng = Utils.haversine(limXMax,limYMin,limXMin,limYMin)
    #     img_ratio = dist_x_lng/(dist_y_lat*2)
    #     return img_ratio
