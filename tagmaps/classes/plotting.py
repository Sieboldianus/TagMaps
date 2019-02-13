# -*- coding: utf-8 -*-

"""Module for matplotlib, seaborn, pyplot methods.
"""
from typing import List, Set, Dict, Tuple, Optional, TextIO, Iterable
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from tagmaps.classes.shared_structure import CleanedPost, AnalysisBounds


class TPLT():
    """Tag Maps plotting Class
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
    def _get_img_ratio(bounds: AnalysisBounds
                       ) -> float:
        """Gets [img] ratio form bounds."""
        dists = TPLT._get_xy_dists(bounds)
        dist_y_lat = dists[0]
        dist_x_lng = dists[1]
        # distYLat = Utils.haversine(limXMin,limYMax,limXMin,limYMin)
        # distXLng = Utils.haversine(limXMax,limYMin,limXMin,limYMin)
        img_ratio = dist_x_lng/(dist_y_lat*2)
        return img_ratio

    @staticmethod
    def plt_setxy_lim(plt, bounds: AnalysisBounds):
        """Set global plotting bounds basedon Analysis Bounds"""
        plt.gca().set_xlim(
            [bounds.lim_lng_min, bounds.lim_lng_max])
        plt.gca().set_ylim(
            [bounds.lim_lat_min, bounds.lim_lat_max])

    @staticmethod
    def _get_fig_points(points, img_ratio, bounds):
        plt.scatter(points.T[0], points.T[1],
                    color='red', **TPLT.PLOT_KWDS)
        fig = plt.figure(num=1, figsize=(
            11, int(11*img_ratio)), dpi=80)
        fig.canvas.set_window_title('Preview Map')
        TPLT.plt_setxy_lim(plt, bounds)
        plt.tick_params(labelsize=10)
        return fig

    @staticmethod
    def _get_sel_preview(points, item, bounds):
        """Returns plt map for item selection preview"""
        img_ratio = TPLT._get_img_ratio(bounds)
        fig = TPLT._get_fig_points(points, img_ratio, bounds)
        plt.suptitle(item, fontsize=18, fontweight='bold')
        return fig

    @staticmethod
    def _get_cluster_preview(
            points, sel_colors, item_text, bounds, mask_noisy,
            cluster_distance, number_of_clusters, auto_select_clusters=None):
        if auto_select_clusters is None:
            auto_select_clusters = False
        # create main cluster points map
        plt.scatter(points.T[0], points.T[1],
                    c=sel_colors, **TPLT.PLOT_KWDS)
        img_ratio = TPLT._get_img_ratio(bounds)
        fig1 = plt.figure(num=1, figsize=(
            11, int(11*img_ratio)), dpi=80)
        fig1.canvas.set_window_title('Cluster Preview')
        TPLT._set_plt_suptitle_st(plt, item_text)
        dist_text = ''
        if auto_select_clusters is False:
            dist_text = '@ ' + str(cluster_distance) + 'm'
        plt.title(f'Cluster Preview {dist_text}',
                  fontsize=12, loc='center')
        # xmax = fig1.get_xlim()[1]
        # ymax = fig1.get_ylim()[1]
        noisy_txt = '{} / {}'.format(mask_noisy.sum(), len(mask_noisy))
        plt.text(bounds.lim_lng_max,
                 bounds.lim_lat_max,
                 f'{number_of_clusters} Clusters (Noise: {noisy_txt})',
                 fontsize=10, horizontalalignment='right',
                 verticalalignment='top', fontweight='bold')
        # set plotting bounds
        TPLT.plt_setxy_lim(plt, bounds)
        TPLT.set_plt_tick_params(plt)
        # define new figure so this one is not
        # overwritten in interactive notebook mode
        # plt.figure()
        return fig1

    @staticmethod
    def set_plt_tick_params(plt):
        """Sets common plt tick params"""
        plt.tick_params(labelsize=10)

    @staticmethod
    def _set_plt_suptitle_st(plt, title: str):
        """Set title of plt"""
        plt.suptitle(title,
                     fontsize=18, fontweight='bold')

    @staticmethod
    def plot_polygon(polygon):
        """Plot a polygon in matplotlib pyplot interface"""
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)
        margin = .3
        x_min, y_min, x_max, y_max = polygon.bounds
        ax.set_xlim([x_min-margin, x_max+margin])
        ax.set_ylim([y_min-margin, y_max+margin])
        patch = PolygonPatch(polygon, fc='#999999',
                             ec='#000000', fill=True,
                             zorder=-1)
        ax.add_patch(patch)
        return fig
