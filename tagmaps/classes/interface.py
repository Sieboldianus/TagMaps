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
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from typing import List, Set, Dict, Tuple, Optional, TextIO
import seaborn as sns
import sklearn.datasets as data
import pandas as pd
import hdbscan
import traceback
import shapely.geometry as geometry
from tagmaps.classes.utils import Utils, AnalysisBounds
from tagmaps.classes.shared_structure import CleanedPost
from tagmaps.classes.cluster import ClusterGen


class UserInterface():
    def __init__(self, bounds: AnalysisBounds,
                 cleaned_post_dict: Dict[CleanedPost],
                 top_tags_list: List[Tuple[str, int]]):
        """Prepare user interface and start Tkinter mainloop()
        """
        self.abort = False
        self.bounds = bounds
        self.floater_x = 0
        self.floater_y = 0
        self.plot_kwds = {'alpha': 0.5, 's': 10, 'linewidths': 0}
        self.cleaned_post_list = list(cleaned_post_dict.values())
        self.top_tags_list = top_tags_list
        self.lastselection_list = list()
        self.tnum = 0
        self._update_bounds()
        self.bound_points_shapely = (
            geometry.MultiPoint([
                (self.bounds.lim_lng_min, self.bounds.lim_lat_min),
                (self.bounds.lim_lng_max, self.bounds.lim_lat_max)
            ])
        )
        self.distYLat = self.bounds.lim_lat_max - self.bounds.lim_lat_min
        self.distXLng = self.bounds.lim_lng_max - self.bounds.lim_lng_min
        # distYLat = Utils.haversine(limXMin,limYMax,limXMin,limYMin)
        # distXLng = Utils.haversine(limXMax,limYMin,limXMin,limYMin)
        # imgRatio = distXLng/(distYLat*2)
        self.img_ratio = self.distXLng/(self.distYLat*2)
        self.distY = Utils.haversine(self.bounds.lim_lng_min,
                                     self.bounds.lim_lat_min,
                                     self.bounds.lim_lng_min,
                                     self.bounds.lim_lat_max)
        self.distX = Utils.haversine(self.bounds.lim_lng_min,
                                     self.bounds.lim_lat_min,
                                     self.bounds.lim_lng_max,
                                     self.bounds.lim_lat_min)
        # 7% of research area width/height (max) =
        # default value #223.245922725 #= 0.000035 radians dist
        self.cluster_distance = (min(self.distX, self.distY)/100)*7
        self.current_display_tag = None
        # Initialize TKinter Interface
        self.app = App()
        # allow error reporting from console backend
        tk.Tk.report_callback_exception = self.report_callback_exception

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
        listbox.bind('<<ListboxSelect>>', self.onselect)
        scroll = tk.Scrollbar(canvas, orient=tk.VERTICAL,
                              background="gray20", borderwidth=0)
        scroll.configure(command=listbox.yview)
        scroll.pack(side="right", fill="y")
        listbox.pack()
        listbox.config(yscrollcommand=scroll.set)
        # only for first 500 entries: use topTagsList[:500]
        for item in self.top_tags_list:
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
                      command=lambda: self.delete_tag(listbox),
                      background="gray20", fg="gray80", borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10)
        c = tk.Checkbutton(canvas, text="Map Tags",
                           variable=self.gen_preview_map,
                           background="gray7", fg="gray80",
                           borderwidth=0, font="Arial 10 bold")
        c.pack(padx=10, pady=10)
        tk_scalebar = tk.Scale(canvas,
                               from_=(self.cluster_distance/100),
                               to=(self.cluster_distance*2),
                               orient=tk.HORIZONTAL,
                               resolution=0.1,
                               command=self.change_cluster_dist,
                               length=300,
                               label="Cluster Cut Distance (in Meters)",
                               background="gray20",
                               borderwidth=0,
                               fg="gray80",
                               font="Arial 10 bold")
        # set position of slider to center
        # (clusterTreeCuttingDist*10) - (clusterTreeCuttingDist/10)/2)
        tk_scalebar.set(self.cluster_distance)
        tk_scalebar.pack()
        b = tk.Button(canvas, text="Cluster Preview",
                      command=self.cluster_current_display_tag,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        b = tk.Button(canvas, text="Scale Test",
                      command=self.scaletest_current_display_tag,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        b = tk.Button(canvas, text="Proceed..",
                      command=self.proceed_with_cluster,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        b = tk.Button(canvas, text="Quit",
                      command=self.quit_tkinter,
                      background="gray20",
                      fg="gray80",
                      borderwidth=0,
                      font="Arial 10 bold")
        b.pack(padx=10, pady=10, side="left")
        canvas.pack(fill='both', padx=0, pady=0)
        buttonsFrame.pack(fill='both', padx=0, pady=0)

        # this is the mainloop for the interface
        # once it is destroyed, the regular process will continue
        self.app.mainloop()
        # end of tkinter loop, welcome back to command line interface
        plt.close("all")

    def _update_bounds(self):
        """Update analysis rectangle boundary based on

        cleaned posts list."""
        df = pd.DataFrame(self.cleaned_post_list)
        points = df.as_matrix(['lng', 'lat'])
        (self.bounds.lim_lat_min,
         self.bounds.lim_lat_max,
         self.bounds.lim_lng_min,
         self.bounds.lim_lng_max) = Utils.get_rectangle_bounds(points)

    def report_callback_exception(self, exc, val, tb):
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

    def quit_tkinter(self):
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

    def proceed_with_cluster(self):
        self.proceed_clusting = True
    # def vis_tag(tag):
        # tkinter.messagebox.showinfo("Proceed", "Proceed")
        # if plt.figure(1):
        #    plt.figure(1).clf()
        self.app.update()
        self.app.destroy()
        self.app.quit()

    @staticmethod
    def sel_photos(tag, cleaned_postlocs: List[CleanedPost]
                   ) -> Tuple[List[str], int]:
        """select photos from list based on a specific tag

        Args:
            tag: tag for selecting posts
            cleaned_postlocs (List[CleanedPost]): list of all posts

        Returns:
            Tuple[List[str], int]: list of post_guids and
                                   number of distinct locations
        """
        distinct_local_loc_ount = set()
        selected_post_guids = list()
        for cleaned_photo_location in cleaned_postlocs:
            if (tag in (cleaned_photo_location.hashtags) or
                    (tag in cleaned_photo_location.post_body)):
                selected_post_guids.append(cleaned_photo_location.guid)
                distinct_local_loc_ount.add(cleaned_photo_location.loc_id)
        return selected_post_guids, len(distinct_local_loc_ount)

    def change_cluster_dist(self, val):
        """Changes cluster distance based on user input

        Args:
            val: new cluster distance
        """
        # tkinter.messagebox.showinfo("messagr", val)
        # global canvas
        # global tkScalebar
        self.cluster_distance = float(val)  # tkScalebar.get()

    def onselect(self, evt):
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
        index = int(list(changed_selection)[0])
        # value = w.get(index)
        # tkinter.messagebox.showinfo("You selected ", value)
        self.tnum = 1
        # generate only preview map
        ClusterGen.cluster_tag(self.top_tags_list[index], True)
        # plt.close('all')

    def cluster_current_display_tag(self):
        if self.current_display_tag:
            # tkinter.messagebox.showinfo("Clustertag: ",
            #                             str(currentDisplayTag))
            ClusterGen.cluster_tag(self.current_display_tag)
        else:
            ClusterGen.cluster_tag(self.top_tags_list[0])

    def scaletest_current_display_tag(self):
        if self.current_display_tag:
            clustertag = self.current_display_tag
        else:
            clustertag = self.top_tags_list[0]
        scalecalclist = []
        dmax = int(self.cluster_distance*10)
        dmin = int(self.cluster_distance/10)
        dstep = int(((self.cluster_distance*10) -
                     (self.cluster_distance/10))/100)
        for i in range(dmin, dmax, dstep):
            self.change_cluster_dist(i)
            self.tk_scalebar.set(i)
            self.app.update()
            # self.cluster_distance = i
            clusters, self.selected_postlist_guids = (
                ClusterGen.cluster_tag(clustertag, None, True)
            )
            mask_noisy = (clusters == -1)
            # with noisy (=0)
            number_of_clusters = len(np.unique(clusters[~mask_noisy]))
            if number_of_clusters == 1:
                break
            form_string = f'{i},{number_of_clusters},'
            f'{mask_noisy.sum()},{len(mask_noisy)},\n'
            scalecalclist.append(form_string)
        with open(f'02_Output/scaletest_{clustertag[0]}.txt',
                  "w", encoding='utf-8') as logfile_a:
            for scalecalc in scalecalclist:
                logfile_a.write(scalecalc)
        plt.figure(1).clf()
        # plt references the last figure accessed
        plt.suptitle(clustertag[0].upper(
        ), fontsize=18, fontweight='bold')
        self.fig1 = plt.figure(num=1, figsize=(
            11, int(11*self.img_ratio)), dpi=80)
        self.fig1.canvas.set_window_title('Cluster Preview')
        dist_text = ''
        if self.autoselect_clusters is False:
            dist_text = f'@ {self.cluster_distance}m'
        plt.title(f'Cluster Preview {dist_text}', fontsize=12, loc='center')
        noisy_txt = f'{mask_noisy.sum()}/{len(mask_noisy)}'
        plt.text(self.bounds.lim_lng_max, self.bounds.lim_lat_max,
                 f'{number_of_clusters} Cluster (Noise: {noisy_txt})',
                 fontsize=10, horizontalalignment='right',
                 verticalalignment='top', fontweight='bold')

    def delete_tag(self, listbox):
        # global top_tags_list
        global lastselectionList
        lastselectionList = []
        # Delete from Listbox
        selection = listbox.curselection()
        for index in selection[::-1]:
            listbox.delete(index)
            del(self.top_tags_list[index])


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
        self.grip.bind("<ButtonPress-1>", self.StartMove)
        self.grip.bind("<ButtonRelease-1>", self.StopMove)
        self.grip.bind("<B1-Motion>", self.OnMotion)
        # center Floating Window
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('+%d+%d' % (x, y))

    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))
