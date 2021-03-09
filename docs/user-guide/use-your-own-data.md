# Use your own data

There are two types of input that can be processed by tagmaps with the provided files in `00_Config`:

* A) raw data
* B) preprocessed data

## A: Raw data

This is the most typical situation. If you have messy raw data, use this approach and simply provide a CSV with the following header:

```CSS
origin_id,post_guid,latitude,longitude,user_guid,post_create_date,post_publish_date,post_thumbnail_url,post_views_count,post_like_count,post_url,tags,emoji,post_title,post_body,post_geoaccuracy,post_comment_count,post_type,post_filter,place_guid,place_name
2,e0ec6886843ce41a587571b633aa9845,49.410686,8.713982,b9bbe67db95f8f81c5f91c338ed0ae24,2016-07-09 08:57:03,2016-10-17 16:21:10,,8,,,heidelberg;deutschland;alemania,"",Heidelberg,,latlng,,,,,
2,6d99d6b2577478fea2242c068b37b341,49.410686,8.713982,b9bbe67db95f8f81c5f91c338ed0ae24,2016-07-09 09:10:41,2016-10-17 16:21:12,,7,,,heidelberg;deutschland;alemania,"",Heidelberg,,latlng,,,,,
2,4eb6a10a8a4ee89cbd5f8c0163252ae0,49.411208,8.714927,6a770936ffc514f317a1572c940acd2e,2012-04-21 12:09:07,2012-05-14 16:27:29,,87,,,germany;heidelberg;2012;friendlyflickr,"",DSC_3734.JPG,,latlng,,,,,
```

If this header is detected, tagmaps will apply some basic filtering and cleanup procedures to filter the often noisy raw data found on social media. Here is an overview of minimum required fields (for most fields, data can be left empty if not available, but the header must be present):

* `origin_id` - an ID for each input source (if you have only one input source, use e.g. `0`). If multiple sources are provided, tagmaps will try to normalize each datasource separately (e.g. Flickr = 1, Twitter = 2)
* `post_guid` - a unique ID for each post, used to identify duplicates
* `latitude` - Latitude coordinate of post
* `longitude` - Longitude coordinate of post
* `user_guid` - a unique identifier for the user or avatar who created the post, used to normalize results (e.g. reduce impact of very active users)
* `post_publish_date` - currently not used in code but required in header
* `post_views_count` - required but can be empty; total views are summed for each cluster
* `emoji` - column with emoji separated by semicolon (`;`); if not present, can be automatically extracted from `post_body`
* `tags` - column with tags (or hashtags) separated by semicolon (`;`)
* `post_title` - Title of the post, used as additional input to select posts
* `post_body` - The content of the post, used as additional input to select posts

It is also possible to provide a custom source mapping in `00_Config` folder (e.g. `sourcemapping_myspecialdatatype.cfg`), but this is beyond the scope of this guide.

!!! Note
    You can use the standard header even if you don't have data for all columns. Simply use empty fields where data is not available:

```python
origin_id,post_guid,latitude,longitude,user_guid,post_create_date,post_publish_date,post_thumbnail_url,post_views_count,post_like_count,post_url,tags,emoji,post_title,post_body,post_geoaccuracy,post_comment_count,post_type,post_filter,place_guid,place_name,place_post_count,city_guid,country_guid
1,1636388273616523980,38.09341,-78.94898,5921622184,,,,0,0,,tag1;tag2;tag3,,,,,0,,,,,,,

```

## B: Preprocessed data

If you have data that was already processed (e.g. cleaned) by yourself and you want to directly produce a clustered output, use this approach. Tagmaps will not try to filter such input. Preprocessed data is also available as an intermediate output from **A**. You may therefore use this to continue Tagmaps processing from already cleaned data.

An example for preprocessed data is the `flickr_dresden_cc-by-licenses.csv` in `01_Input`. It is a CSV with the following header:

```CSS
origin_id,lat,lng,guid,user_guid,post_create_date,post_publish_date,post_body,hashtags,emoji,post_views_count,post_like_count,loc_id,loc_name
"2",51.053833,13.733333,"8ba6c17f46cabbd7a2d63e767601272d","f2487030bdaa29aa85138cac1f354826","2010-05-07","2010-05-23","","water;dresden;germany","",58,0,"51.053833:13.733333",""
"2",51.041,13.731,"31eec170b862e463a1e3297057b6277e","f2487030bdaa29aa85138cac1f354826","2010-05-06","2010-05-15","","germany;dresden;transport","",78,0,"51.041:13.731",""
```