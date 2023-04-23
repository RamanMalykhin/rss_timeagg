import feedparser
import datetime
import subprocess
import datetime
import rfeed
import time
import os
import logging
import argparse
import json

try:
	parser = argparse.ArgumentParser()
	parser.add_argument("-c","--config", dest='config')
	
	args = parser.parse_args()

	configname = args.config
		
	with open(configname+'.json','r') as config_f:
		config = json.load(config_f)

	logging.basicConfig(format='%(asctime)s %(message)s', level = logging.DEBUG, filename = config['job_name'] +'.log')


	logging.info('beginning run')
	
	input_feed = feedparser.parse(config['input_feed_link'])
	
	feed_author = input_feed['feed']['author']
	feed_entries = input_feed['entries']
	feed_entries.reverse()	

	dateagg_dict = {}
	
	for entry in feed_entries:
		publish_date = entry['published_parsed']
		agg_date = str(datetime.date(publish_date.tm_year, publish_date.tm_mon, publish_date.tm_mday))
		
		entry_content = entry['summary_detail']['value']
		
		dateagg_dict.setdefault(agg_date, []).append(entry_content)
			
	rfeed_items = []
	outputted_files = []
	for agg_date, entries in dateagg_dict.items():
		
		aggregated_entries_html = "<html>" + \
				" <head> <meta charset = \"UTF-8\">" + \
				"<title>" + agg_date+ "</title>" + \
				"</head> <body>" + \
				"<hr>".join(entries) + \
				"</body> </html>"
		
		filename = agg_date+'.html'
		
		with open(filename, 'w') as file:
			file.write(aggregated_entries_html)
		
		subprocess.Popen(["s3cmd", "put", "--acl-public", filename, config['s3cmd_bucket_url']])
		
		link = config['public_bucket-url'] + filename
		
		rfeed_items.append(rfeed.Item(
			title = agg_date,
			link = link,
			description = aggregated_entries_html[0:200]+'...',
			author = feed_author,
			guid = rfeed.Guid(link)
		))
		
		outputted_files.append(filename)
		
	f = rfeed.Feed(
		title = config['job_name'] + "_rss_timeagg",
		link = config['input_feed_link'],
		description = "",
		language = "",
		lastBuildDate = datetime.datetime.now(),
		items = rfeed_items)
	
	filename = config['job_name']+'_feed.xml' 
	
	with open(filename, 'w') as file:
		file.write(f.rss())
	
	subprocess.Popen(["s3cmd", "put", "--acl-public", filename, config['s3cmd_bucket_url']])
	
	outputted_files.append(filename)
	
	time.sleep(15)
	
	for filename in outputted_files:
		os.remove(filename)
		
	logging.info('complete')

except Exception as e:
	logging.exception(e)
	print(e)