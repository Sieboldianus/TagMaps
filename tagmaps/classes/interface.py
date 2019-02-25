# -*- coding: utf-8 -*-

"""
Module for tag maps tkinker interface

for (optional) user input
"""

from __future__ import absolute_import

import sys
import traceback
import tkinter as tk
import tkinter.messagebox
from tkinter import TclError
from tkinter.messagebox import showerror
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from tagmaps.classes.cluster import ClusterGen
from tagmaps.classes.plotting import TPLT
from tagmaps.classes.shared_structure import CleanedPost, LOCATIONS
from tagmaps.classes.utils import Utils

# enable interactive mode for pyplot
plt.ion()
# label_size = 10
# plt.rcParams['xtick.labelsize'] = label_size
# plt.rcParams['ytick.labelsize'] = label_size
# Optional: set global plotting bounds
# plt.gca().set_xlim([limXMin, limXMax])
# plt.gca().set_ylim([limYMin, limYMax])
# sns.set_color_codes()
plt.style.use('ggplot')


class UserInterface():
    """User interface class for interacting input"""

    def __init__(self,
                 clusterer_list: List[ClusterGen] = None,
                 location_names_dict: Dict[str, str] = None
                 ):
        """Prepare user interface and start Tkinter mainloop()
        """
        self._clst_list = list()
        # append clusters to list
        if not clusterer_list:
            raise ValueError('No clusterer selected.')
        for clusterer in clusterer_list:
            self._clst_list.append(clusterer)
        # select initial cluster
        self._clst = self._clst_list[0]
        self.location_names_dict = location_names_dict
        self.abort = False
        self.current_display_item = None
        # Initialize TKinter Interface
        self.app = App()
        # allow error reporting from console backend
        tk.Tk.report_callback_exception = self._report_callback_exception
        # definition of global vars for interface and graph design
        # Cluster preparation
        self.gen_preview_map = tk.IntVar(value=0)
        self.create_min_spanning_tree = False
        self.create_condensed_tree = False
        self.tk_scalebar = None
        # definition of global figure for reusing windows
        self.fig1 = None
        self.fig2 = None
        self.fig3 = None
        self.fig4 = None
        # user selected item
        self.lastselection = None
        # A frame is created for each window/part of the gui;
        # after it is used, it is destroyed with frame.destroy()
        header_frame = tk.Frame(self.app.floater)
        canvas = tk.Canvas(
            header_frame, width=150, height=220,
            highlightthickness=0, background="gray7")
        header_label = tk.Label(
            canvas, text="Optional: Exclude tags, "
            "emoji or locations.",
            background="gray7", fg="gray80",
            font="Arial 10 bold")
        header_label.pack(padx=10, pady=10)

        self._clst_index = tk.IntVar()
        self._clst_index.set(0)
        # Radiobuttons for selecting list
        idx = 0
        for clst in self._clst_list:
            radio_b = tk.Radiobutton(
                canvas, text=f'{clst.cls_type}',
                variable=self._clst_index,
                value=idx,
                indicatoron=0,
                command=self._change_clusterer,
                background="gray20",
                fg="gray80",
                borderwidth=0,
                font="Arial 10 bold",
                width=15)
            radio_b.pack(side='left')
            idx += 1
        canvas.pack(fill='both', padx=0, pady=0,)
        header_frame.pack(fill='both', padx=0, pady=0)
        listbox_frame = tk.Frame(self.app.floater)
        canvas = tk.Canvas(
            listbox_frame, width=150, height=220,
            highlightthickness=0, background="gray7")
        guide_label = tk.Label(
            canvas, text=f'Select all items you wish to exclude '
            f'from analysis \n '
            f'and click on remove. Proceed if ready.',
            background="gray7", fg="gray80")
        guide_label.pack(padx=10, pady=10)
        listbox_font = None
        listbox = tk.Listbox(
            canvas,
            selectmode=tk.EXTENDED, bd=0, background="gray29",
            fg="gray91", width=30, font=listbox_font)
        listbox.bind('<<ListboxSelect>>', self._onselect)
        scroll = tk.Scrollbar(canvas, orient=tk.VERTICAL,
                              background="gray20", borderwidth=0)
        scroll.configure(command=listbox.yview)
        scroll.pack(side="right", fill="y")
        listbox.pack()
        listbox.config(yscrollcommand=scroll.set)
        self.listbox = listbox
        self._populate_listbox()
        canvas.pack(fill='both', padx=0, pady=0)
        listbox_frame.pack(fill='both', padx=0, pady=0)
        buttons_frame = tk.Frame(self.app.floater)
        canvas = tk.Canvas(buttons_frame, width=150, height=200,
                           highlightthickness=0, background="gray7")
        UserInterface._create_button(
            canvas, "Remove Selected", lambda: self._delete_fromtoplist(
                self.listbox),
            left=False)
        check_b = tk.Checkbutton(
            canvas, text="Map Tags",
            variable=self.gen_preview_map,
            background="gray7", fg="gray80",
            borderwidth=0, font="Arial 10 bold")
        check_b.pack(padx=10, pady=10)
        self.tk_scalebar = tk.Scale(
            canvas,
            from_=(self._clst.cluster_distance/100),
            to=(self._clst.cluster_distance*2),
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
        self.tk_scalebar.set(self._clst.cluster_distance)
        self.tk_scalebar.pack()
        UserInterface._create_button(
            canvas, "Cluster Preview",
            self._cluster_current_display_item)
        UserInterface._create_button(
            canvas, "Scale Test",
            self._scaletest_current_display_item)
        UserInterface._create_button(
            canvas, "Proceed..", self._proceed_with_cluster)
        UserInterface._create_button(
            canvas, "Quit", self._quit_tkinter)
        canvas.pack(fill='both', padx=0, pady=0)
        buttons_frame.pack(fill='both', padx=0, pady=0)

    @staticmethod
    def _create_button(canvas, text: str, command, left: bool = True):
        """Create button with text and command

        and pack to canvas."""
        button = tk.Button(canvas, text=text,
                           command=command,
                           background="gray20",
                           fg="gray80",
                           borderwidth=0,
                           font="Arial 10 bold")
        if left:
            button.pack(padx=10, pady=10, side="left")
        else:
            button.pack(padx=10, pady=10)

    def _populate_listbox(self):
        """Populate tkinter listbox with records

        - only for first 1000 entries: top_list[:1000]
        """
        listbox = self.listbox
        top_list: List[Tuple[str, int]] = self._clst.top_list
        loc_name_dict: Dict[str, str] = self.location_names_dict
        # clear first
        listbox.delete(0, tk.END)
        # tkinter.messagebox.showinfo(f"length of list:", f"{len(top_list)}")
        # maximum of 1000 entries shown
        for item in top_list[:1000]:
            if self._clst.cls_type == LOCATIONS:
                item_name = Utils.get_locname(item.name, loc_name_dict)
            else:
                item_name = item.name
            try:
                # try inserting emoji first,
                # some emoji can be printed
                listbox.insert(tk.END, f'{item_name} ({item.ucount} user)')
            except TclError:
                # replace emoji by unicode name on error
                emoji = Utils.get_emojiname(item_name)
                listbox.insert(tk.END, f'{emoji} ({item.ucount} user)')

    def start(self):
        """Start up user interface after initialization

        this is the mainloop for the interface
        once it is destroyed, the regular process
        will continue
        """
        self.app.mainloop()
        # end of tkinter loop,
        # welcome back to console
        plt.close("all")

    def _cluster_preview(self, sel_item: str):
        """Show preview map(s) based on tag selection"""
        # Get cluster data first
        (_, _, points, sel_colors,
         mask_noisy, number_of_clusters) = self._clst.cluster_item(
             item=sel_item,
             preview_mode=True)
        ## Cluster Map Plot ##
        if not plt.fignum_exists(1):
            self.fig1 = plt.figure(1)
        else:
            self.fig1.clf()
        self.fig1.add_subplot(111)
        self.fig1 = TPLT.get_cluster_preview(
            points, sel_colors, sel_item, self._clst.bounds, mask_noisy,
            self._clst.cluster_distance, number_of_clusters,
            self._clst.autoselect_clusters, fig=self.fig1)
        self.fig1.canvas.draw_idle()
        ## Single Linkage Tree Plot ##
        if not plt.fignum_exists(2):
            self.fig2 = plt.figure(2)
        else:
            self.fig2.clf()
        axis = self.fig2.add_subplot(111)
        # p is the number of max count of leafs in the tree,
        # this should at least be the number of clusters*10,
        # not lower than 50 [but max 500 to not crash]
        self._clst.clusterer.single_linkage_tree_.plot(
            axis=axis,
            truncate_mode='lastp',
            p=max(50, min(number_of_clusters*10, 256)))
        item_name = sel_item
        TPLT.get_single_linkage_tree_preview(
            item_name, self.fig2, self._clst.cluster_distance,
            self._clst.cls_type)
        self.fig2.canvas.draw_idle()
        ## Condensed Tree Plot ##
        if self.create_condensed_tree:
            # Unfixed issue:
            # on consecutive updates
            # the colorbar is added multiple times
            # possible solution: retrieve only
            # condensed data from hdbscan
            # and create plot in tagmaps
            if not plt.fignum_exists(3):
                self.fig3 = plt.figure(3)
            else:
                self.fig3.clf()
            axis = self.fig3.add_subplot(111)
            self._clst.clusterer.condensed_tree_.plot(
                axis=axis,
                log_size=True
            )
            self.fig3.canvas.set_window_title('Condensed Tree')
            TPLT.set_plt_suptitle(
                self.fig3, sel_item, self._clst.cls_type)
            TPLT.set_plt_tick_params(axis)
            self.fig3.canvas.draw_idle()
        if self.create_min_spanning_tree:
            if not plt.fignum_exists(4):
                self.fig4 = plt.figure(4)
            else:
                self.fig4.clf()
            axis = self.fig4.add_subplot(111)
            self._clst.clusterer.minimum_spanning_tree_.plot(
                axis=axis,
                edge_cmap='viridis',
                edge_alpha=0.6,
                node_size=10,
                edge_linewidth=1)
            self.fig4.canvas.set_window_title(
                'Minimum Spanning Tree')
            # tkinter.messagebox.showinfo("messagr", str(type(ax)))
            TPLT.set_plt_suptitle(
                self.fig4, sel_item, self._clst.cls_type)
            axis.set_title(
                f'Minimum Spanning Tree @ {self._clst.cluster_distance}m',
                fontsize=12, loc='center')
            self.fig4.legend(fontsize=10)
            self.fig4.canvas.draw()
        TPLT.set_plt_tick_params(axis)
        self._update_scalebar()

    def _intf_selection_preview(self, sel_item: str):
        """Update preview map based on item selection"""
        # tkinter.messagebox.showinfo("Proceed", f'{sel_item}')
        points = self._clst.get_np_points(
            item=sel_item,
            silent=True)
        if points is None:
            tkinter.messagebox.showinfo(
                "No locations found.",
                "All locations for given item have been removed.")
            return
        if not plt.fignum_exists(1):
            self.fig1 = plt.figure(1)
        else:
            # clf() clears figure and subplots (axes)
            self.fig1.clf()
        self.fig1.add_subplot(111)
        self._intf_plot_points(sel_item, points)

    def _intf_plot_points(self, item_name: str, points):
        self.fig1 = TPLT.get_fig_points(
            self.fig1,
            points, self._clst.bounds)
        TPLT.set_plt_suptitle(
            self.fig1, item_name, self._clst.cls_type)

    def _report_callback_exception(self, __, val, ___):
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
        """Exit Tkinter GUI

        ..to continue with code execution after mainloop()

        Notes:
        - see [1]
        https://stackoverflow.com/questions/35040168/python-tkinter-error-cant-evoke-event-command
        - root.quit() causes mainloop to exit, see [2]
        https://stackoverflow.com/questions/2307464/what-is-the-difference-between-root-destroy-and-root-quit

        """
        self.abort = True
        self.app.update()
        self.app.destroy()
        self.app.quit()

    def _proceed_with_cluster(self):
        self.app.update()
        self.app.destroy()
        self.app.quit()

    def _change_cluster_dist(self, val):
        """Changes cluster distance based on user input

        Args:
            val: new cluster distance
        """
        self._clst.cluster_distance = float(val)

    def _change_clusterer(self):
        """Changes clusterer based on user selection

        Either TAGS, EMOJI or LOCATIONS
        """
        self.current_display_item = None
        self._clst = self._clst_list[
            self._clst_index.get()]
        self._populate_listbox()
        self._update_scalebar()

    def _update_scalebar(self):
        """Adjust scalebar limits from cluster distance"""
        self.tk_scalebar.configure(
            from_=(self._clst.cluster_distance/100),
            to=(self._clst.cluster_distance*2))
        self.tk_scalebar.set(self._clst.cluster_distance)

    def _onselect(self, evt):
        """On user select item from list

        Args:
            evt (event object): event object for selected item
        """
        widg = evt.widget
        self.lastselection = widg.index(tk.ACTIVE)
        sel_index = widg.curselection()[0]
        if (self.gen_preview_map.get() == 1 and
                len(widg.curselection()) == 1):
            # generate preview map
            # only if selection box is checked
            # and only if one item is checked
            sel_item = self._clst.top_list[sel_index][0]
            self._intf_selection_preview(
                sel_item)
            self.current_display_item = sel_item

    def _cluster_current_display_item(self):
        """Cluster button: use selected or first in list"""
        if self.current_display_item:
            # tkinter.messagebox.showinfo("Clusteritem: ",
            #                             f'{self.current_display_item}')
            self._cluster_preview(self.current_display_item)
        else:
            # use first in list
            self._cluster_preview(self._clst.top_list[0][0])

    def _scaletest_current_display_item(self):
        """Compute clustering across different scales and output results to txt"""
        if self.create_min_spanning_tree is False:
            tkinter.messagebox.showinfo(
                "Skip: ",
                f'Currently deactivated')
            return
        if self.current_display_item:
            sel_item = self.current_display_item
        else:
            sel_item = self._clst.top_list[0][0]
        scalecalclist = []
        dmax = int(self._clst.cluster_distance*10)
        dmin = int(self._clst.cluster_distance/10)
        dstep = int(((self._clst.cluster_distance*10) -
                     (self._clst.cluster_distance/10))/100)
        for i in range(dmin, dmax, dstep):
            self._change_cluster_dist(i)
            self.tk_scalebar.set(i)
            self.app.update()
            # self._clst.cluster_distance = i
            clusters, __ = (
                self._clst.cluster_item(sel_item, None, True)
            )
            mask_noisy = (clusters == -1)
            # with noisy (=0)
            number_of_clusters = len(np.unique(clusters[~mask_noisy]))
            if number_of_clusters == 1:
                break
            form_string = (f'{i},{number_of_clusters},'
                           f'{mask_noisy.sum()},{len(mask_noisy)},\n')
            scalecalclist.append(form_string)
        with open(f'02_Output/scaletest_{sel_item.name}.txt',
                  "w", encoding='utf-8') as logfile_a:
            for scalecalc in scalecalclist:
                logfile_a.write(scalecalc)
        plt.figure(1).clf()
        # plt references the last figure accessed
        self.fig1 = plt.figure()
        TPLT.set_plt_suptitle(self.fig1, sel_item.name, self._clst.cls_type)
        self.fig1.canvas.set_window_title('Cluster Preview')
        dist_text = ''
        if self._clst.autoselect_clusters is False:
            dist_text = f'@ {self._clst.cluster_distance}m'
        plt.title(f'Cluster Preview {dist_text}', fontsize=12, loc='center')
        noisy_txt = f'{mask_noisy.sum()}/{len(mask_noisy)}'
        plt.text(self._clst.bounds.lim_lng_max, self._clst.bounds.lim_lat_max,
                 f'{number_of_clusters} Cluster (Noise: {noisy_txt})',
                 fontsize=10, horizontalalignment='right',
                 verticalalignment='top', fontweight='bold')

    def _delete_fromtoplist(self, listbox):
        """Remove entry from top_list

        - if location removed, clean post list too
        """
        # Delete from Listbox
        selection = listbox.curselection()
        id_list_selected = list()
        for index in selection[::-1]:
            listbox.delete(index)
            id_list_selected.append(self._clst.top_list[index][0])
            del self._clst.top_list[index]
        # remove all cleaned posts from processing list if
        # location is removed
        if self._clst.cls_type == LOCATIONS:
            self._delete_post_locations(id_list_selected)

    def _delete_post_locations(self,
                               post_locids: List[str]) -> List[CleanedPost]:
        """Remove all posts with post_locid from list

        Returns a list of values for fast lookup
                the dict itself is modified in place
                across clusters
                because dicts are mutable
        To-do:
            - update toplists (remove tags/emoji from
            posts that are removed)
        """
        # tkinter.messagebox.showinfo("Len before: ", len(cleaned_post_dict))
        # first get post guids to be removed
        # this is quite expensive,
        # perhaps there's a better way
        # tkinter.messagebox.showinfo("post_locids: ", f'{post_locids}')
        postguids_to_remove = [post_record.guid for post_record
                               in self._clst.cleaned_post_dict.values()
                               if post_record.loc_id in post_locids]
        if UserInterface._query_user(
                f'This will also remove '
                f'{len(postguids_to_remove)} posts from further processing.\n'
                f'Continue?', f'Continue?') is True:
            # the following code will remove
            # dict records and list entries from current clusterer
            for post_guid in postguids_to_remove:
                del self._clst.cleaned_post_dict[post_guid]
            # To modify the list in-place, assign to its slice:
            self._clst.cleaned_post_list[:] = list(
                self._clst.cleaned_post_dict.values())

    @staticmethod
    def _query_user(question_text: str,
                    title_text: str) -> bool:
        """Ask a question with Yes No options"""
        result = tkinter.messagebox.askquestion(
            title_text, question_text, icon='question')
        if result == 'yes':
            return True
        else:
            return False


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
        w_win = self.winfo_reqwidth()
        h_win = self.winfo_reqheight()
        ws_win = self.winfo_screenwidth()
        hs_win = self.winfo_screenheight()
        x_win = (ws_win/2) - (w_win/2)
        y_win = (hs_win/2) - (h_win/2)
        self.geometry('+%d+%d' % (x_win, y_win))
        # coordinates of floating window
        self.x_move = None
        self.y_move = None

    def _start_move(self, event):
        self.x_move = event.x
        self.y_move = event.y

    def _stop_move(self, __):
        self.x_move = None
        self.y_move = None

    def _on_motion(self, event):
        deltax = event.x - self.x_move
        deltay = event.y - self.y_move
        x_win = self.winfo_x() + deltax
        y_win = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x_win, y_win))
