# -*- coding: utf-8 -*-

from tagmaps.classes.shared_structure import CleanedPost
from tagmaps.classes.utils import Utils, AnalysisBounds
import shapely.geometry as geometry
"""
Module for tag maps clustering functions
"""

from typing import List, Set, Dict, Tuple, Optional, TextIO
from multiprocessing.pool import ThreadPool
pool = ThreadPool(processes=1)


class ClusterGen():
    """Cluster module for tags, emoji and post locations
    """

    def __init__(self, bounds: AnalysisBounds,
                 cleaned_post_dict: Dict[CleanedPost],
                 top_tags_list: List[Tuple[str, int]]):
        self.tnum = 0
        self.bounds = bounds
        self.cleaned_post_list = list(cleaned_post_dict.values())
        self.top_tags_list = top_tags_list

    def cluster_tag(self, toptag=None, preview=None, silent=None):
        if preview is None:
            preview = False
        if silent is None:
            silent = False
        global currentDisplayTag
        global img_ratio, floater_x, floater_y
        global fig1, fig2, fig3, fig4
        selectedPhotoList_Guids, distinctLocalLocationCount = sel_photos(
            toptag[0], cleaned_post_list)
        percentageOfTotalLocations = distinctLocalLocationCount / \
            (total_distinct_locations/100)
        if silent:
            if toptag[0] in prepared_data.top_emoji_list:
                text = unicode_name(toptag[0])
            else:
                text = toptag[0]
            print(f'({self.tnum} of {prepared_data.tmax}) Found {len(selectedPhotoList_Guids)} photos (UPL) for tag \'{text}\' ({percentageOfTotalLocations:.0f}% of total distinct locations in area)', end=" ")

        # clustering
        if len(selectedPhotoList_Guids) < 2:
            return [], selectedPhotoList_Guids
        selectedPhotoList = [cleaned_post_dict[x]
                             for x in selectedPhotoList_Guids]
        # only used for tag clustering, otherwise (photo location clusters), global vars are used (df, points)
        df = pd.DataFrame(selectedPhotoList)
        # converts pandas data to numpy array (limit by list of column-names)
        points = df.as_matrix(['lng', 'lat'])
        # only return preview fig without clustering
        if preview == True:
            # only map data
            if genPreviewMap.get() == 1:
                if fig1:
                    plt.figure(1).clf()  # clear figure 1
                    #earth = Basemap()
                    # earth.bluemarble(alpha=0.42)
                    # earth.drawcoastlines(color='#555566', linewidth=1)
                    plt.suptitle(toptag[0].upper(),
                                 fontsize=18, fontweight='bold')
                    # reuse window of figure 1 for new figure
                    plt.scatter(points.T[0], points.T[1],
                                color='red', **plot_kwds)
                    fig1 = plt.figure(num=1, figsize=(
                        11, int(11*img_ratio)), dpi=80)
                    fig1.canvas.set_window_title('Preview Map')
                    #displayImgPath = pathname + '/Output/ClusterImg/00_displayImg.png'
                    # fig1.figure.savefig(displayImgPath)
                else:
                    plt.suptitle(toptag[0].upper(),
                                 fontsize=18, fontweight='bold')
                    plt.scatter(points.T[0], points.T[1],
                                color='red', **plot_kwds)
                    fig1 = plt.figure(num=1, figsize=(
                        11, int(11*img_ratio)), dpi=80)
                    #earth = Basemap()
                    # earth.bluemarble(alpha=0.42)
                    # earth.drawcoastlines(color='#555566', linewidth=1)
                    fig1.canvas.set_window_title('Preview Map')
                plt.gca().set_xlim(
                    [self.bounds.lim_lng_min, self.bounds.lim_lng_max])
                plt.gca().set_ylim(
                    [self.bounds.lim_lat_min, self.bounds.lim_lat_max])
                plt.tick_params(labelsize=10)
                currentDisplayTag = toptag
        else:
            # cluster data
            # conversion to radians for HDBSCAN (does not support decimal degrees)
            tagRadiansData = np.radians(points)
            # for each tag in overallNumOfUsersPerTag_global.most_common(1000) (descending), calculate HDBSCAN Clusters
            minClusterSize = max(
                2, int(((len(selectedPhotoList_Guids))/100)*5))  # 4% optimum
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=minClusterSize, gen_min_span_tree=createMinimumSpanningTree, allow_single_cluster=True, min_samples=1)
            #clusterer = hdbscan.HDBSCAN(min_cluster_size=minClusterSize,gen_min_span_tree=True,min_samples=1)
            #clusterer = hdbscan.HDBSCAN(min_cluster_size=10,metric='haversine',gen_min_span_tree=False,allow_single_cluster=True)
            #clusterer = hdbscan.robust_single_linkage_.RobustSingleLinkage(cut=0.000035)
            #srsl_plt = hdbscan.robust_single_linkage_.plot()
            # Start clusterer on different thread to prevent GUI from freezing
            # See: http://stupidpythonideas.blogspot.de/2013/10/why-your-gui-app-freezes.html
            # https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
            # if silent:
            #    #on silent command line operation, don't use multiprocessing
            #    clusterer = fit_cluster(clusterer,tagRadiansData)
            # else:
            with warnings.catch_warnings():
                # disable joblist multithread warning
                warnings.simplefilter('ignore', UserWarning)
                async_result = pool.apply_async(
                    Utils.fit_cluster, (clusterer, tagRadiansData))
                clusterer = async_result.get()
                # clusterer.fit(tagRadiansData)
                #updateNeeded = False
            if autoselectClusters:
                sel_labels = clusterer.labels_  # auto selected clusters
            else:
                sel_labels = clusterer.single_linkage_tree_.get_clusters(Utils.getRadiansFromMeters(
                    clusterTreeCuttingDist), min_cluster_size=2)  # 0.000035 without haversine: 223 m (or 95 m for 0.000015)
            # exit function in case final processing loop (no figure generating)
            if silent:
                return sel_labels, selectedPhotoList_Guids
            mask_noisy = (sel_labels == -1)
            number_of_clusters = len(
                np.unique(sel_labels[~mask_noisy]))  # len(sel_labels)
            #palette = sns.color_palette("hls", )
            # palette = sns.color_palette(None, len(sel_labels)) #sns.color_palette("hls", ) #sns.color_palette(None, 100)
            palette = sns.color_palette("husl", number_of_clusters+1)
            sel_colors = [palette[x] if x >= 0
                          else (0.5, 0.5, 0.5)
                          # for x in clusterer.labels_ ]
                          for x in sel_labels]  # clusterer.labels_ (best selection) or sel_labels (cut distance)
            #tkinter.messagebox.showinfo("Num of clusters: ", str(len(sel_colors)) + " " + str(sel_colors[1]))
            # output/update matplotlib figures
            if fig1:
                plt.figure(1).clf()
                # plt references the last figure accessed
                plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                ax = plt.scatter(
                    points.T[0], points.T[1], color=sel_colors, **plot_kwds)
                fig1 = plt.figure(num=1, figsize=(
                    11, int(11*img_ratio)), dpi=80)
                fig1.canvas.set_window_title('Cluster Preview')
                distText = ''
                if autoselectClusters == False:
                    distText = '@ ' + str(clusterTreeCuttingDist) + 'm'
                plt.title(f'Cluster Preview {distText}',
                          fontsize=12, loc='center')
                #plt.title('Cluster Preview')
                #xmax = ax.get_xlim()[1]
                #ymax = ax.get_ylim()[1]
                noisyTxt = '{}/{}'.format(mask_noisy.sum(), len(mask_noisy))
                plt.text(self.bounds.lim_lng_max, self.bounds.lim_lat_max, f'{number_of_clusters} Cluster (Noise: {noisyTxt})',
                         fontsize=10, horizontalalignment='right', verticalalignment='top', fontweight='bold')
            else:
                plt.scatter(points.T[0], points.T[1],
                            c=sel_colors, **plot_kwds)
                fig1 = plt.figure(num=1, figsize=(
                    11, int(11*img_ratio)), dpi=80)
                fig1.canvas.set_window_title('Cluster Preview')
                plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                distText = ''
                if autoselectClusters == False:
                    distText = '@ ' + str(clusterTreeCuttingDist) + 'm'
                plt.title(f'Cluster Preview {distText}',
                          fontsize=12, loc='center')
                #xmax = fig1.get_xlim()[1]
                #ymax = fig1.get_ylim()[1]
                noisyTxt = '{} / {}'.format(mask_noisy.sum(), len(mask_noisy))
                plt.text(self.bounds.lim_lng_max, self.bounds.lim_lat_max, f'{number_of_clusters} Clusters (Noise: {noisyTxt})',
                         fontsize=10, horizontalalignment='right', verticalalignment='top', fontweight='bold')
            plt.gca().set_xlim(
                [self.bounds.lim_lng_min, self.bounds.lim_lng_max])
            plt.gca().set_ylim(
                [self.bounds.lim_lat_min, self.bounds.lim_lat_max])
            plt.tick_params(labelsize=10)
            # if len(tagRadiansData) < 10000:
            if fig2:
                plt.figure(2).clf()
                plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                #plt.title('Condensed Tree', fontsize=12,loc='center')
                clusterer.condensed_tree_.plot(
                    select_clusters=False, selection_palette=sel_colors)  # ,label_clusters=False
                #tkinter.messagebox.showinfo("Num of clusters: ", str(len(sel_colors)) + " " + str(sel_colors[0]))
            else:
                plt.figure(2).canvas.set_window_title('Condensed Tree')
                fig2 = clusterer.condensed_tree_.plot(
                    select_clusters=False, selection_palette=sel_colors)  # ,label_clusters=False
                #tkinter.messagebox.showinfo("Num of clusters: ", str(len(sel_colors)) + " " + str(sel_colors[1]))
                #fig2 = clusterer.condensed_tree_.plot(select_clusters=False, selection_palette=sel_colors,label_clusters=True)
                #plt.title('Condensed Tree', fontsize=12,loc='center')
                plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
            plt.tick_params(labelsize=10)
            if fig3:
                plt.figure(3).clf()
                plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                plt.title('Single Linkage Tree', fontsize=12, loc='center')
                # clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=50)
                # p is the number of max count of leafs in the tree, this should at least be the number of clusters*10, not lower than 50 [but max 500 to not crash]
                ax = clusterer.single_linkage_tree_.plot(
                    truncate_mode='lastp', p=max(50, min(number_of_clusters*10, 256)))
                #tkinter.messagebox.showinfo("messagr", str(type(ax)))
                # plot cutting distance
                y = Utils.getRadiansFromMeters(clusterTreeCuttingDist)
                xmin = ax.get_xlim()[0]
                xmax = ax.get_xlim()[1]
                line, = ax.plot([xmin, xmax], [
                                y, y], color='k', label=f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                line.set_label(
                    f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                ax.legend(fontsize=10)
                vals = ax.get_yticks()
                ax.set_yticklabels(
                    ['{:3.1f}m'.format(Utils.getMetersFromRadians(x)) for x in vals])
            else:
                plt.figure(3).canvas.set_window_title('Single Linkage Tree')
                fig3 = clusterer.single_linkage_tree_.plot(
                    truncate_mode='lastp', p=max(50, min(number_of_clusters*10, 256)))
                plt.suptitle(toptag[0].upper(), fontsize=18, fontweight='bold')
                plt.title('Single Linkage Tree', fontsize=12, loc='center')
                #tkinter.messagebox.showinfo("messagr", str(type(fig3)))
                # plot cutting distance
                y = Utils.getRadiansFromMeters(clusterTreeCuttingDist)
                xmin = fig3.get_xlim()[0]
                xmax = fig3.get_xlim()[1]
                line, = fig3.plot([xmin, xmax], [
                                  y, y], color='k', label=f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                line.set_label(
                    f'Cluster (Cut) Distance {clusterTreeCuttingDist}m')
                fig3.legend(fontsize=10)
                vals = fig3.get_yticks()
                fig3.set_yticklabels(
                    [f'{Utils.getMetersFromRadians(x):3.1f}m' for x in vals])
            plt.tick_params(labelsize=10)
            if createMinimumSpanningTree:
                if fig4:
                    plt.figure(4).clf()
                    plt.suptitle(toptag[0].upper(),
                                 fontsize=18, fontweight='bold')
                    #plt.title('Single Linkage Tree', fontsize=12,loc='center')
                    # clusterer.single_linkage_tree_.plot(truncate_mode='lastp',p=50)
                    ax = clusterer.minimum_spanning_tree_.plot(edge_cmap='viridis',
                                                               edge_alpha=0.6,
                                                               node_size=10,
                                                               edge_linewidth=1)  # tkinter.messagebox.showinfo("messagr", str(type(ax)))
                    fig4.canvas.set_window_title('Minimum Spanning Tree')
                    plt.title(
                        f'Minimum Spanning Tree @ {clusterTreeCuttingDist}m', fontsize=12, loc='center')
                    ax.legend(fontsize=10)
                    # ax=plt.gca()        #plt.gca() for current axis, otherwise set appropriately.
                    # im=ax.images        #this is a list of all images that have been plotted
                    # cb=im[0].colorbar  ##in this case I assume to be interested to the last one plotted, otherwise use the appropriate index
                    # cb.ax.tick_params(labelsize=10)
                    #vals = cb.ax.get_yticks()
                    #cb.ax.set_yticklabels(['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals])
                else:
                    plt.figure(4).canvas.set_window_title(
                        'Minimum Spanning Tree')
                    fig4 = clusterer.minimum_spanning_tree_.plot(edge_cmap='viridis',
                                                                 edge_alpha=0.6,
                                                                 node_size=10,
                                                                 edge_linewidth=1)  # tkinter.messagebox.showinfo("messagr", str(type(ax)))
                    plt.suptitle(toptag[0].upper(),
                                 fontsize=18, fontweight='bold')
                    plt.title(
                        f'Minimum Spanning Tree @ {clusterTreeCuttingDist}m', fontsize=12, loc='center')
                    fig4.legend(fontsize=10)
                    # ax=plt.gca()        #plt.gca() for current axis, otherwise set appropriately.
                    # im=ax.images        #this is a list of all images that have been plotted
                    # cb=im[0].colorbar  ##in this case I assume to be interested to the last one plotted, otherwise use the appropriate index
                    # cb.ax.tick_params(labelsize=10)
                    #vals = cb.ax.get_yticks()
                    #cb.ax.set_yticklabels(['{:3.1f}m'.format(getMetersFromRadians(x)) for x in vals])
            plt.tick_params(labelsize=10)
            # adjust scalebar limits
            global tkScalebar
            tkScalebar.configure(
                from_=(clusterTreeCuttingDist/100), to=(clusterTreeCuttingDist*2))
