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
#-i shapefileIntersect (will clip with referenced shapefile, requires WGS1984 Projection
#-f shapefilePath
#-stat statisticsOnly
#-lmuc limitBottomUserCount, default = 5
%~dp0__main__.exe -p "False" -o "False" -t "True"
exit