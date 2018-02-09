#Source: fromFlickr_CSV, fromLBSN
#-j tokenizeJapanese
#-p cluster Photos
#-c localSaturationCheck (will exclude any tags that are used over the whole area)
#-s Source
python "D:\03_EvaVGI\05_Code\Py\standalone_tag_cluster_hdbscan\generateTagClusters.py" -s 'fromFlickr_CSV' -c 'True' -p 'False' -j 'False'
$SHELL