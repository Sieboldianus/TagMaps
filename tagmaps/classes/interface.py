# -*- coding: utf-8 -*-

"""
Module for tag maps tkinker interface

for (optional) user input
"""

import sys
import tkinter as tk
from tkinter.messagebox import showerror
import tkinter.messagebox
from unicodedata import name as unicode_name
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Set, Dict, Tuple, Optional, TextIO
import sklearn.datasets as data
import traceback
import shapely.geometry as geometry
from tagmaps.classes.utils import Utils, AnalysisBounds
from tagmaps.classes.shared_structure import CleanedPost
from tagmaps.classes.cluster import ClusterGen

# enable interactive mode for pyplot (not necessary?!)
plt.ion()
# label_size = 10
# plt.rcParams['xtick.labelsize'] = label_size
# plt.rcParams['ytick.labelsize'] = label_size
# Optional: set global plotting bounds
# plt.gca().set_xlim([limXMin, limXMax])
# plt.gca().set_ylim([limYMin, limYMax])
# sns.set_color_codes()
# matplotlib.style.use('ggplot')
plt.style.use('ggplot')


class UserInterface():
    def __init__(self,
                 tag_cluster: ClusterGen,
                 emoji_cluster: ClusterGen = None
                 ):
        """Prepare user interface and start Tkinter mainloop()
        """
        self._clst = tag_cluster
        self._clst_e = emoji_cluster
        self.abort = False
        # self.floater_x = 0
        # self.floater_y = 0
        self.plot_kwds = {'alpha': 0.5, 's': 10, 'linewidths': 0}
        self.lastselection_list = list()
        self.distYLat = (
            self._clst.bounds.lim_lat_max - self._clst.bounds.lim_lat_min)
        self.distXLng = (
            self._clst.bounds.lim_lng_max - self._clst.bounds.lim_lng_min)
        # distYLat = Utils.haversine(limXMin,limYMax,limXMin,limYMin)
        # distXLng = Utils.haversine(limXMax,limYMin,limXMin,limYMin)
        # imgRatio = distXLng/(distYLat*2)
        self.img_ratio = self.distXLng/(self.distYLat*2)
        self.distY = Utils.haversine(self._clst.bounds.lim_lng_min,
                                     self._clst.bounds.lim_lat_min,
                                     self._clst.bounds.lim_lng_min,
                                     self._clst.bounds.lim_lat_max)
        self.distX = Utils.haversine(self._clst.bounds.lim_lng_min,
                                     self._clst.bounds.lim_lat_min,
                                     self._clst.bounds.lim_lng_max,
                                     self._clst.bounds.lim_lat_min)
        # 7% of research area width/height (max) =
        # default value #223.245922725 #= 0.000035 radians dist
        self.cluster_distance = (min(self.distX, self.distY)/100)*7
        self.auto_select_clusters = False
        self.current_display_tag = None
        # Initialize TKinter Interface
        self.app = App()
        # allow error reporting from console backend
        tk.Tk.report_callback_exception = self._report_callback_exception

        # definition of global vars for interface and graph design
        self.canvas_width = 1320
        self.canvas_height = 440
        # Cluster preparation
        self.graph_frame = None
        self.gen_preview_map = tk.IntVar(value=0)
        self.create_min_spanning_tree = False
        self.autoselect_clusters = False
        self.tk_scalebar = None
        # definition of global figure for reusing windows
        self.fig1 = None
        self.fig2 = None
        self.fig3 = None
        self.fig4 = None
        # A frame is created for each window/part of the gui;
        # after it is used, it is destroyed with frame.destroy()
        listbox_frame = tk.Frame(self.app.floater)
        canvas = tk.Canvas(listbox_frame, width=150, height=200,
                           highlightthickness=0, background="gray7")
        l = tk.Label(canvas, text="Optional: Exclude tags.",
                     background="gray7", fg="gray80", font="Arial 10 bold")
        l.pack(padx=10, pady=10)
        l = tk.Label(canvas,
                     text="Select all tags you wish to exclude "
                     "from analysis \n "
                     "and click on remove to proceed.",
                     background="gray7", fg="gray80")
        l.pack(padx=10, pady=10)
        # if cfg.data_source == "fromInstagram_PGlbsnEmoji":
        #    listbox_font = ("twitter Color Emoji", 12, "bold")
        #    #listbox_font = ("Symbola", 12, "bold")
        # else:
        listbox_font = None
        listbox = tk.Listbox(canvas,
                             selectmode=tk.MULTIPLE, bd=0, background="gray29",
                             fg="gray91", width=30, font=listbox_font)
        listbox.bind('<<ListboxSelect>>', self._onselect)
        scroll = tk.Scrollbar(canvas, orient=tk.VERTICAL,
                              background="gray20", borderwidth=0)
        scroll.configure(command=listbox.yview)
        scroll.pack(side="right", fill="y")
        listbox.pack()
        listbox.config(yscrollcommand=scroll.set)
        # only for first 500 entries: use topTagsList[:500]
        for item in self._clst.top_tags_list:
            try:
                listbox.insert(tk.END, f'{item[0]} ({item[1]} user)')
            except tk.TclError:
                # print(item[0].encode("utf-8"))
                # Utils.with_surrogates()
                emoji = "".join(unicode_name(c) for c in item[0])
                listbox.insert(tk.END, f'{emoji} ({item[1]} user)')
        canvas.pack(fill='both', padx=0, pady=0)
        listbox_frame.pack(fill='both', padx=0, pady=0)
        buttonsFrame = tk.Frame(self.app.floater)
        canvas = tk.Canvas(buttonsFrame, width=150, height=200,
                           highlightthickness=0, background="gray7")
        b = tk.Button(canvas, text="Remove Tag(s)",
                      command=lambda: self._delete_tag(listbox),
                      background="gray20", fg="gray80", borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10)
        c = tk.Checkbutton(canvas, text="Map Tags",
                           variable=self.gen_preview_map,
                           background="gray7", fg="gray80",
                           borderwidth=0, font="Arial 10 bold")
        c.pack(padx=10, pady=10)
        self.tk_scalebar = tk.Scale(canvas,
                                    from_=(self.cluster_distance/100),
                                    to=(self.cluster_distance*2),
                                    orient=tk.HORIZONTAL,
                                    resolution=0.1,
                                    command=self._change_cluster_dist,
                                    length=300,
                                    label="Cluster Cut Distance (in Meters)",
                                    background="gray20",
                                    borderwidth=0,
                                    fg="gray80",
                                    font="Arial 10 bold")
        # set position of slider to center
        # (clusterTreeCuttingDist*10) - (clusterTreeCuttingDist/10)/2)
        self.tk_scalebar.set(self.cluster_distance)
        self.tk_scalebar.pack()
        b = tk.Button(canvas, text="Cluster Preview",
                      command=self._cluster_current_display_tag,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        b = tk.Button(canvas, text="Scale Test",
                      command=self._scaletest_current_display_tag,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        b = tk.Button(canvas, text="Proceed..",
                      command=self._proceed_with_cluster,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        b = tk.Button(canvas, text="Quit",
                      command=self._quit_tkinter,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        canvas.pack(fill='both', padx=0, pady=0)
        buttonsFrame.pack(fill='both', padx=0, pady=0)

    def start(self):
        # this is the mainloop for the interface
        # once it is destroyed, the regular process will continue
        self.app.mainloop()
        # end of tkinter loop, welcome back to command line interface
        plt.close("all")

    def _cluster_preview(self, sel_tag: Tuple[str, int]):
        """Cluster preview map based on tag selection"""
        # tkinter.messagebox.showinfo("Num of clusters: ",
        # str(len(sel_colors)) + " " + str(sel_colors[1]))
        # output/update matplotlib figures
        points = self._clst._get_np_points(tag=sel_tag[0], silent=True)
        self._clst.cluster_points(
            points=points,
            cluster_distance=self.cluster_distance,
            preview_mode=True)
        mask_noisy = self._clst.mask_noisy
        number_of_clusters = self._clst.number_of_clusters
        sel_colors = self._clst.sel_colors
        if self.fig1:
            plt.figure(1).clf()
            # plt references the last figure accessed
            plt.suptitle(sel_tag[0].upper(),
                         fontsize=18, fontweight='bold')
            ax = plt.scatter(
                points.T[0], points.T[1], color=sel_colors,
                **self.plot_kwds)
            self.fig1 = plt.figure(num=1, figsize=(
                11, int(11*self.img_ratio)), dpi=80)
            self.fig1.canvas.set_window_title('Cluster Preview')
            distText = ''
            if self.auto_select_clusters is False:
                distText = '@ ' + str(self.cluster_distance) + 'm'
            plt.title(f'Cluster Preview {distText}',
                      fontsize=12, loc='center')
            # plt.title('Cluster Preview')
            # xmax = ax.get_xlim()[1]
            # ymax = ax.get_ylim()[1]
            noisy_txt = '{}/{}'.format(mask_noisy.sum(), len(mask_noisy))
            plt.text(self._clst.bounds.lim_lng_max,
                     self._clst.bounds.lim_lat_max,
                     f'{number_of_clusters} Cluster (Noise: {noisy_txt})',
                     fontsize=10, horizontalalignment='right',
                     verticalalignment='top', fontweight='bold')
        else:
            plt.scatter(points.T[0], points.T[1],
                        c=sel_colors, **self.plot_kwds)
            self.fig1 = plt.figure(num=1, figsize=(
                11, int(11*self.img_ratio)), dpi=80)
            self.fig1.canvas.set_window_title('Cluster Preview')
            plt.suptitle(sel_tag[0].upper(), fontsize=18, fontweight='bold')
            distText = ''
            if self.auto_select_clusters is False:
                distText = '@ ' + str(self.cluster_distance) + 'm'
            plt.title(f'Cluster Preview {distText}',
                      fontsize=12, loc='center')
            # xmax = fig1.get_xlim()[1]
            # ymax = fig1.get_ylim()[1]
            noisy_txt = '{} / {}'.format(mask_noisy.sum(), len(mask_noisy))
            plt.text(self._clst.bounds.lim_lng_max,
                     self._clst.bounds.lim_lat_max,
                     f'{number_of_clusters} Clusters (Noise: {noisy_txt})',
                     fontsize=10, horizontalalignment='right',
                     verticalalignment='top', fontweight='bold')
        plt.gca().set_xlim(
            [self._clst.bounds.lim_lng_min, self._clst.bounds.lim_lng_max])
        plt.gca().set_ylim(
            [self._clst.bounds.lim_lat_min, self._clst.bounds.lim_lat_max])
        plt.tick_params(labelsize=10)
        # if len(tagRadiansData) < 10000:
        if self.fig2:
            plt.figure(2).clf()
            plt.suptitle(sel_tag[0].upper(), fontsize=18, fontweight='bold')
            # plt.title('Condensed Tree', fontsize=12,loc='center')
            self._clst.clusterer.condensed_tree_.plot(
                select_clusters=False, selection_palette=sel_colors
            )
            # ,label_clusters=False
            # tkinter.messagebox.showinfo(
            #   "Num of clusters: ",
            #   str(len(sel_colors)) + " " + str(sel_colors[0])
            #   )
        else:
            plt.figure(2).canvas.set_window_title('Condensed Tree')
            self.fig2 = self._clst.clusterer.condensed_tree_.plot(
                select_clusters=False,
                selection_palette=sel_colors
            )
            # ,label_clusters=False
            # tkinter.messagebox.showinfo(
            #   "Num of clusters: ",
            #   str(len(self._clst.sel_colors)) + " "
            #   "str(sel_colors[1]))
            # fig2 = clusterer.condensed_tree_.plot(
            #   select_clusters=False,
            #   selection_palette=self._clst.sel_colors,
            #   label_clusters=True)
            # plt.title('Condensed Tree', fontsize=12,loc='center')
            plt.suptitle(sel_tag[0].upper(), fontsize=18,
                         fontweight='bold')
        plt.tick_params(labelsize=10)
        if self.fig3:
            plt.figure(3).clf()
            plt.suptitle(sel_tag[0].upper(), fontsize=18,
                         fontweight='bold')
            plt.title('Single Linkage Tree', fontsize=12,
                      loc='center')
            # clusterer.single_linkage_tree_.plot(
            #   truncate_mode='lastp',p=50)
            # p is the number of max count of leafs in the tree,
            # this should at least be the number of clusters*10,
            # not lower than 50 [but max 500 to not crash]
            ax = self._clst.clusterer.single_linkage_tree_.plot(
                truncate_mode='lastp',
                p=max(50, min(number_of_clusters*10, 256)))
            # tkinter.messagebox.showinfo("messagr", str(type(ax)))
            # plot cutting distance
            y = Utils.get_radians_from_meters(
                self.cluster_distance)
            xmin = ax.get_xlim()[0]
            xmax = ax.get_xlim()[1]
            line, = ax.plot(
                [xmin, xmax], [y, y], color='k',
                label=f'Cluster (Cut) Distance {self.cluster_distance}m'
            )
            line.set_label(
                f'Cluster (Cut) Distance {self.cluster_distance}m')
            ax.legend(fontsize=10)
            vals = ax.get_yticks()
            ax.set_yticklabels(
                ['{:3.1f}m'.format(
                    Utils.get_meters_from_radians(x)
                ) for x in vals])
        else:
            plt.figure(3).canvas.set_window_title(
                'Single Linkage Tree')
            self.fig3 = self._clst.clusterer.single_linkage_tree_.plot(
                truncate_mode='lastp',
                p=max(50, min(number_of_clusters*10, 256)))
            plt.suptitle(sel_tag[0].upper(), fontsize=18,
                         fontweight='bold')
            plt.title('Single Linkage Tree',
                      fontsize=12, loc='center')
            # tkinter.messagebox.showinfo("messagr", str(type(fig3)))
            # plot cutting distance
            y = Utils.get_radians_from_meters(self.cluster_distance)
            xmin = self.fig3.get_xlim()[0]
            xmax = self.fig3.get_xlim()[1]
            line, = self.fig3.plot(
                [xmin, xmax], [y, y],
                color='k',
                label=f'Cluster (Cut) Distance {self.cluster_distance}m')
            line.set_label(
                f'Cluster (Cut) Distance {self.cluster_distance}m')
            self.fig3.legend(fontsize=10)
            vals = self.fig3.get_yticks()
            self.fig3.set_yticklabels(
                [f'{Utils.get_meters_from_radians(x):3.1f}m' for x in vals])
        plt.tick_params(labelsize=10)
        if self.create_min_spanning_tree:
            if self.fig4:
                plt.figure(4).clf()
                plt.suptitle(sel_tag[0].upper(),
                             fontsize=18, fontweight='bold')
                # plt.title('Single Linkage Tree', fontsize=12,loc='center')
                # clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=50)
                ax = self._clst.clusterer.minimum_spanning_tree_.plot(
                    edge_cmap='viridis', edge_alpha=0.6,
                    node_size=10, edge_linewidth=1)
                # tkinter.messagebox.showinfo("messagr", str(type(ax)))
                self.fig4.canvas.set_window_title('Minimum Spanning Tree')
                plt.title(
                    f'Minimum Spanning Tree @ {self.cluster_distance}m',
                    fontsize=12, loc='center')
                ax.legend(fontsize=10)
                # ax=plt.gca()
                # #plt.gca() for current axis, otherwise set appropriately.
                # im=ax.images
                # #this is a list of all images that have been plotted
                # cb=im[0].colorbar
                # ##in this case I assume to be interested to the last one
                # plotted, otherwise use the appropriate index
                # cb.ax.tick_params(labelsize=10)
                # vals = cb.ax.get_yticks()
                # cb.ax.set_yticklabels(
                #   ['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals])
            else:
                plt.figure(4).canvas.set_window_title(
                    'Minimum Spanning Tree')
                self.fig4 = self._clst.clusterer.minimum_spanning_tree_.plot(
                    edge_cmap='viridis',
                    edge_alpha=0.6,
                    node_size=10,
                    edge_linewidth=1)
                # tkinter.messagebox.showinfo("messagr", str(type(ax)))
                plt.suptitle(sel_tag[0].upper(),
                             fontsize=18, fontweight='bold')
                plt.title(
                    f'Minimum Spanning Tree @ {self.cluster_distance}m',
                    fontsize=12, loc='center')
                self.fig4.legend(fontsize=10)
                # ax=plt.gca()        #plt.gca() for current axis,
                #   otherwise set appropriately.
                # im=ax.images        #this is a list of all
                #   images that have been plotted
                # cb=im[0].colorbar
                # ##in this case I assume to be interested
                #   to the last one plotted,
                #   otherwise use the appropriate index
                # cb.ax.tick_params(labelsize=10)
                # vals = cb.ax.get_yticks()
                # cb.ax.set_yticklabels(
                #   ['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals]
                # )
        plt.tick_params(labelsize=10)
        # adjust scalebar limits
        self.tk_scalebar.configure(
            from_=(self.cluster_distance/100),
            to=(self.cluster_distance*2))

    def _selection_preview(self, sel_tag: Tuple[str, int]):
        """Update preview map based on tag selection"""
        # tkinter.messagebox.showinfo("Proceed", f'{sel_tag}')
        points = self._clst._get_np_points(
            tag=sel_tag[0],
            silent=True)
        if self.fig1:
            plt.figure(1).clf()  # clear figure 1
            # earth = Basemap()
            # earth.bluemarble(alpha=0.42)
            # earth.drawcoastlines(color='#555566', linewidth=1)
            plt.suptitle(sel_tag[0].upper(),
                         fontsize=18, fontweight='bold')
            # reuse window of figure 1 for new figure
            plt.scatter(points.T[0], points.T[1],
                        color='red', **self.plot_kwds)
            self.fig1 = plt.figure(num=1, figsize=(
                11, int(11*self.img_ratio)), dpi=80)
            self.fig1.canvas.set_window_title('Preview Map')
            # displayImgPath = pathname +
            # '/Output/ClusterImg/00_displayImg.png'
            # fig1.figure.savefig(displayImgPath)
        else:
            plt.suptitle(sel_tag[0].upper(),
                         fontsize=18, fontweight='bold')
            plt.scatter(points.T[0], points.T[1],
                        color='red', **self.plot_kwds)
            self.fig1 = plt.figure(num=1, figsize=(
                11, int(11*self.img_ratio)), dpi=80)
            # earth = Basemap()
            # earth.bluemarble(alpha=0.42)
            # earth.drawcoastlines(color='#555566', linewidth=1)
            self.fig1.canvas.set_window_title('Preview Map')
        plt.gca().set_xlim(
            [self._clst.bounds.lim_lng_min, self._clst.bounds.lim_lng_max])
        plt.gca().set_ylim(
            [self._clst.bounds.lim_lat_min, self._clst.bounds.lim_lat_max])
        plt.tick_params(labelsize=10)
        self.current_display_tag = sel_tag

    def _report_callback_exception(self, exc, val, tb):
        """Override for error reporting during tkinter mode"""
        showerror("Error", message=str(val))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print("*** print_exception:")
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
        print("*** print_exc:")
        traceback.print_exc()
        print("*** format_exc, first and last line:")
        formatted_lines = traceback.format_exc().splitlines()
        print(formatted_lines[0])
        print(formatted_lines[-1])
        print("*** format_exception:")
        print(repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback)))
        print("*** extract_tb:")
        print(repr(traceback.extract_tb(exc_traceback)))
        print("*** format_tb:")
        print(repr(traceback.format_tb(exc_traceback)))
        print("*** tb_lineno:", exc_traceback.tb_lineno)

    def _quit_tkinter(self):
        """exits Tkinter gui

        ..to continue with code execution after mainloop()

        Notes:
        - see [1]
        https://stackoverflow.com/questions/35040168/python-tkinter-error-cant-evoke-event-command
        - root.quit() causes mainloop to exit, see [2]
        https://stackoverflow.com/questions/2307464/what-is-the-difference-between-root-destroy-and-root-quit

        """
        # global app
        # app.floater.destroy()
        # tkinter.messagebox.showinfo("Closing App", "Closing App")
        # plt.quit()
        self.abort = True
        self.app.update()
        self.app.destroy()
        self.app.quit()

    def _proceed_with_cluster(self):
        # def vis_tag(tag):
            # tkinter.messagebox.showinfo("Proceed", "Proceed")
            # if plt.figure(1):
            #    plt.figure(1).clf()
        self.app.update()
        self.app.destroy()
        self.app.quit()

    def _change_cluster_dist(self, val):
        """Changes cluster distance based on user input

        Args:
            val: new cluster distance
        """
        # tkinter.messagebox.showinfo("messagr", val)
        # global canvas
        # global tkScalebar
        self.cluster_distance = float(val)  # tkScalebar.get()

    def _onselect(self, evt):
        """On user select tag from list

        Args:
            evt (event object): event object for selected tag
        """
        w = evt.widget
        if self.lastselection_list:
            # if not empty
            changed_selection = (
                set(self.lastselection_list).symmetric_difference(
                    set(w.curselection()))
            )
            self.lastselection_list = w.curselection()
        else:
            self.lastselection_list = w.curselection()
            changed_selection = w.curselection()
        sel_index = int(list(changed_selection)[0])
        # value = w.get(index)
        # tkinter.messagebox.showinfo("You selected ", value)
        self._clst.tnum = 1
        if self.gen_preview_map.get() == 1:
            # generate only preview map
            # only if selection box is checked
            self._selection_preview(
                self._clst.top_tags_list[sel_index])
            # plt.close('all')

    def _cluster_current_display_tag(self):
        if self.current_display_tag:
            # tkinter.messagebox.showinfo("Clustertag: ",
            #                             f'{self.current_display_tag}')
            self._cluster_preview(self.current_display_tag)
        else:
            self._cluster_preview(self._clst.top_tags_list[0])

    def _scaletest_current_display_tag(self):
        if self.create_min_spanning_tree is False:
            tkinter.messagebox.showinfo(
                "Skip: ",
                f'Currently deactivated')
            return
        if self.current_display_tag:
            sel_tag = self.current_display_tag
        else:
            sel_tag = self._clst.top_tags_list[0]
        scalecalclist = []
        dmax = int(self.cluster_distance*10)
        dmin = int(self.cluster_distance/10)
        dstep = int(((self.cluster_distance*10) -
                     (self.cluster_distance/10))/100)
        for i in range(dmin, dmax, dstep):
            self._change_cluster_dist(i)
            self.tk_scalebar.set(i)
            self.app.update()
            # self.cluster_distance = i
            clusters, self.selected_postlist_guids = (
                self._clst.cluster_tag(sel_tag, None, True)
            )
            mask_noisy = (clusters == -1)
            # with noisy (=0)
            number_of_clusters = len(np.unique(clusters[~mask_noisy]))
            if number_of_clusters == 1:
                break
            form_string = f'{i},{number_of_clusters},'
            f'{mask_noisy.sum()},{len(mask_noisy)},\n'
            scalecalclist.append(form_string)
        with open(f'02_Output/scaletest_{sel_tag[0]}.txt',
                  "w", encoding='utf-8') as logfile_a:
            for scalecalc in scalecalclist:
                logfile_a.write(scalecalc)
        plt.figure(1).clf()
        # plt references the last figure accessed
        plt.suptitle(sel_tag[0].upper(
        ), fontsize=18, fontweight='bold')
        self.fig1 = plt.figure(num=1, figsize=(
            11, int(11*self.img_ratio)), dpi=80)
        self.fig1.canvas.set_window_title('Cluster Preview')
        dist_text = ''
        if self.autoselect_clusters is False:
            dist_text = f'@ {self.cluster_distance}m'
        plt.title(f'Cluster Preview {dist_text}', fontsize=12, loc='center')
        noisy_txt = f'{mask_noisy.sum()}/{len(mask_noisy)}'
        plt.text(self._clst.bounds.lim_lng_max, self._clst.bounds.lim_lat_max,
                 f'{number_of_clusters} Cluster (Noise: {noisy_txt})',
                 fontsize=10, horizontalalignment='right',
                 verticalalignment='top', fontweight='bold')

    def _delete_tag(self, listbox):
        # global top_tags_list
        global lastselectionList
        lastselectionList = []
        # Delete from Listbox
        selection = listbox.curselection()
        for index in selection[::-1]:
            listbox.delete(index)
            del(self._clst.top_tags_list[index])


class App(tk.Tk):
    """Tkinter interface wrapper

    Args:
        tk: reference to tkinter package

    """

    def __init__(self):
        tk.Tk.__init__(self)
        # this is needed to make the root disappear
        self.overrideredirect(True)
        self.geometry('%dx%d+%d+%d' % (0, 0, 0, 0))
        # create separate floating window
        self.floater = FloatingWindow(self)


class FloatingWindow(tk.Toplevel):
    """Toplevel tkinter floating window app

    Args:
        tk: Tkinter reference
    """

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)
        self.configure(background='gray7')
        # self.label = tk.Label(self, text="Click on the grip to move")
        self.grip = tk.Label(self, bitmap="gray25")
        self.grip.pack(side="left", fill="y")
        # self.label.pack(side="right", fill="both", expand=True)
        self.grip.bind("<ButtonPress-1>", self._start_move)
        self.grip.bind("<ButtonRelease-1>", self._stop_move)
        self.grip.bind("<B1-Motion>", self._on_motion)
        # center Floating Window
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('+%d+%d' % (x, y))

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _stop_move(self, event):
        self.x = None
        self.y = None

    def _on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))
