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
%~dp0generateTagClusters.exe -p "False" -o "True" -t "False"
exit