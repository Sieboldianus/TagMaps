#Optional Parameter:
#-s source, default= "fromLBSN"
#-r removeLongTail, default= "True"
#-e EPSGCode, default= Auto Detect!
#-t clusterTags, default= "True"
#-p cluster Photos, default= "True"
#-o cluster Emoji, default= "True"
#-m topicModeling, default= "False"
#-j tokenizeJapanese, default= "False"
#-w writeCleanedData, default= "True"
#-c localSaturationCheck (will exclude any tags that are used over the whole area), default= "False"
python "D:\03_EvaVGI\05_Code\Py\standalone_tag_cluster_hdbscan\tagmaps\generateTagClusters.py" -s 'fromLBSN' -p False -o True -t True -r True -i True --ignorePlaceCorrections True --ignoreStoplists True --statisticsOnly True -f 'D:/03_EvaVGI/01_Daten/2018-02-20_NationalPark_Berchtesgarden_Nicola/nationalpark_berchtesgarden_osm.shp' 
$SHELL