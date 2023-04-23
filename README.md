# rss_timeagg
Script for aggregating posts from an RSS feed across time into a HTML page, and outputting a feed of such aggregate pages. Perfect for feeds that are too active and give you 10 posts a day where you'd rather get 1 long one. (I made it when I realized there was no convenient way to subscribe to Telegram channels that break up a single long post into multiple instead of using telegra.ph like they probably should.)

The resulting feed and its aggregate HTMLs are outputted to an S3 bucket (or any other object storage system that is S3-compatible.) **It relies on there being `s3cmd` configured on your system.**

Current limitations:
* can only aggregate per day, but I plan to extend that to at least weeks, hours and minutes
* ~~does not explicitly respect the order of posts within the day.~~ fixed as of [`ebeb39e5a741d6265f5229d54cd49931246ec431`](https://github.com/RamanMalykhin/rss_timeagg/commit/ebeb39e5a741d6265f5229d54cd49931246ec431)

both will be fixed... when they will be fixed, but I expect that to happen sooner rather than later.

## Usage

For every feed that you want `rss_timeagg` to work on, it expects a json config in the same directory as itself. Format:
```
{
    "job_name": "nasabreakingnews",
    "input_feed_link": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "s3cmd_bucket_url": "s3://mybucket",
    "public_bucket_url":"http://myobjectstorage.com/"
}
```
where:
* `job_name` is the name of this aggregation job. This appears in the title of the outputted feed as well as the name of the .xml, so best to not use special characters
* `input_feed_link` is the feed you want to be aggregating
* `s3cmd_bucket_url` is the url of your bucket that s3cmd uses (`s3://` and the name of your bucket)
* `public_bucket_url` is the endpoint where you are serving your feed and files to the rest of the internet from your bucket

after this has been created, simply run `rss_timeagg.py` from the console (or - more practical since you probably want your aggregate feed to keep updating - automation tool of your choice like crontab), passing with the argument `--config` the name of the config.
```
python rss_timeagg.py --config nasa_breaking_config.json
```
The resulting aggregated feed will be accessible at `public_bucket_url`/`job_name`_feed.xml, so in our example http://myobjectstorage.com/nasabreakingnews_feed.xml. You can pass that URL to whatever RSS feed you use.

## Acknowledgements
I would probably have never gotten this off the ground, if not for the existence of https://github.com/kurtmckee/feedparser and https://github.com/svpino/rfeed. Big thanks to the maintainers of both for bringing the barrier to entry into RSS-related Python stuff low enough even for script monkeys like myself. :)
