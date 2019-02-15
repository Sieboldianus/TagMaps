# -*- coding: utf-8 -*-

"""Module for matplotlib, seaborn, pyplot methods.
"""
from typing import List, Set, Dict, Tuple, Optional, TextIO, Iterable
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from descartes import PolygonPatch
from tagmaps.classes.shared_structure import CleanedPost, AnalysisBounds
from tagmaps.classes.utils import Utils
from tagmaps.classes.shared_structure import (
    TAGS, LOCATIONS, EMOJI)


class TPLT():
    """Tag Maps plotting Class

    To remember (because mpl can be quite confusing):
        - The figure is the window that the plot is in.
          It's the top-level container.
        - Each figure usually has one or more axes.
          These are the plots/subplots.
        - Colorbars and other stuff are also inside the figure.
          Adding a colorbar creates a new axes (unless specified otherwise)
        - two modes exist, OO (object oriented) and 
          pyplot("state-machine interface"),
          use OO-Mode if possible because it is more flexible
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

    @staticmethod
    def plt_setxy_lim(ax, bounds: AnalysisBounds):
        """Set global plotting bounds basedon Analysis Bounds"""
        ax.set_xlim(
            [bounds.lim_lng_min, bounds.lim_lng_max])
        ax.set_ylim(
            [bounds.lim_lat_min, bounds.lim_lat_max])

    @staticmethod
    def _get_fig_points(fig, points, bounds):
        # a new figure window
        if not fig:
            fig = plt.figure(1)
            fig.add_subplot(111)
        ax = fig.get_axes()[0]
        # fig = plt.figure(num=1, figsize=(
        #    11, int(11*img_ratio)), dpi=80)
        # only one subplot (nrows, ncols, axnum)
        ax.scatter(points.T[0], points.T[1],
                   color='red', **TPLT.PLOT_KWDS)
        fig.canvas.set_window_title('Preview Map')
        TPLT.plt_setxy_lim(ax, bounds)
        ax.tick_params(labelsize=10)
        return fig

    @staticmethod
    def _get_sel_preview(points, item, bounds):
        """Returns plt map for item selection preview"""
        # img_ratio = TPLT._get_img_ratio(bounds)
        fig = None
        fig = TPLT._get_fig_points(fig, points, bounds)
        fig.suptitle(item, fontsize=18, fontweight='bold')
        return fig

    @staticmethod
    def _get_cluster_preview(points, sel_colors, item_text, bounds, mask_noisy,
                             cluster_distance, number_of_clusters, auto_select_clusters=None,
                             shapes=None, fig=None):
        if auto_select_clusters is None:
            auto_select_clusters = False
        # img_ratio = TPLT._get_img_ratio(bounds)
        if not fig:
            fig = plt.figure(1)
            fig.add_subplot(111)
        ax = fig.get_axes()[0]
        # create main cluster points map
        ax.scatter(points.T[0], points.T[1],
                   c=sel_colors, **TPLT.PLOT_KWDS)
        fig.canvas.set_window_title('Cluster Preview')
        TPLT._set_plt_suptitle_st(fig, item_text)
        dist_text = ''
        if shapes:
            for shape in shapes:
                patch = TPLT._get_poly_patch(ax, shape)
                ax.add_patch(patch)
        if auto_select_clusters is False:
            dist_text = '@ ' + str(int(cluster_distance)) + 'm'
        ax.set_title(f'Cluster Preview {dist_text}',
                     fontsize=12, loc='center')
        # xmax = fig1.get_xlim()[1]
        # ymax = fig1.get_ylim()[1]
        noisy_txt = '{} / {}'.format(mask_noisy.sum(), len(mask_noisy))
        ax.text(bounds.lim_lng_max,
                bounds.lim_lat_max,
                f'{number_of_clusters} Clusters (Noise: {noisy_txt})',
                fontsize=10, horizontalalignment='right',
                verticalalignment='top', fontweight='bold')
        # set plotting bounds
        TPLT.plt_setxy_lim(ax, bounds)
        TPLT.set_plt_tick_params(ax)
        # define new figure so this one is not
        # overwritten in interactive notebook mode
        # plt.figure()
        return fig

    @staticmethod
    def get_single_linkage_tree_preview(
            item_text, fig, cluster_distance, cls_type):

        TPLT._set_plt_suptitle(fig, item_text, cls_type)
        fig.canvas.set_window_title('Single Linkage Tree')
        ax = fig.get_axes()[0]
        ax.set_title('Single Linkage Tree', fontsize=12,
                     loc='center')
        # plot cutting distance
        y = Utils._get_radians_from_meters(
            cluster_distance)
        ax.relim()
        xmin = ax.get_xlim()[0]
        xmax = ax.get_xlim()[1]
        ax.plot(
            [xmin, xmax], [y, y], color='k',
            label=f'Cluster (Cut) Distance {int(cluster_distance)}m'
        )
        ax.legend(fontsize=10)
        # replace y labels with meters text (instead of radians dist)
        ax.yaxis.set_major_formatter(FuncFormatter(TPLT.y_formatter))
        TPLT.set_plt_tick_params(ax)
        return fig

    @staticmethod
    def y_formatter(x, pos):
        return f'{Utils._get_meters_from_radians(x):3.0f}m'

    @staticmethod
    def _set_plt_suptitle(fig, item: str, cls_type):
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
            emoji_name = Utils._get_emojiname(item)
            title = f'{item} ({emoji_name})'
        else:
            title = item.upper()
        return title

    @staticmethod
    def set_plt_tick_params(ax):
        """Sets common plt tick params"""
        ax.tick_params(labelsize=10)

    @staticmethod
    def _get_poly_patch(ax, polygon):
        """Returns a matplotlib polygon-patch from shapely polygon"""
        patch = PolygonPatch(polygon, fc='#999999',
                             ec='#000000', fill=True,
                             zorder=-1, alpha=0.7)
        return patch
