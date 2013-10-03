import codecs
import pymongo
import csv
import json
import datetime
from dateutil.parser import parse
import requests
import logging
import re
import os
import weibo_settings
import weibo_module
import sys




#if exclude_error_code = false, use error_code as filter
def csvize_deleted_unique(csv_filename, error_code=-1, exclude_error_code=False):

	nowdatetime = weibo_module.get_current_chinatime()

	deleted_post_ids = weibo_module.get_deleted_postids(error_code, exclude_error_code)
	num_dead_posts = len(deleted_post_ids)

	#if we're not tracking any posts, get out of there
	if (num_dead_posts <= 0):
		return

	## OPEN A FILE
	with codecs.open(csv_filename, "w", "utf-16") as wf:

		#write csv header
		csv_header = weibo_module.get_csv_header()
		wf.write(csv_header + "\n")
		#print csv_header

		#iterate through posts
		for this_post_id in deleted_post_ids:

			this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

			csvline = weibo_module.make_csvline_from_post(this_post)

		
			csvline = map((lambda x: unicode(x)), csvline)

			#not csv, this is our delimiter now
			csvline = weibo_settings.delim.join(csvline)

#			#print csvline
			wf.write(csvline + "\n")



###
#let's #print a log of all deleted posts, with the repost count/checked time following as pairs. so:
# post_id, user id, etc....... and then , unixepoch, repost count, unixepoch, repost count.... 

#if exclude_error_code = false, use error_code as filter
def csvize_repost_timeline(csv_filename, type="deleted", error_code=-1, exclude_error_code=False):

	nowdatetime = weibo_module.get_current_chinatime()

	if type == "deleted":
		query_post_ids = weibo_module.get_deleted_postids(error_code, exclude_error_code)
	else:
		query_post_ids = weibo_module.get_all_postids()

	num_query_posts = len(query_post_ids)

	#if we're not tracking any posts, get out of there
	if (num_query_posts <= 0):
		return

	## OPEN A FILE
	with codecs.open(csv_filename, "w", "utf-16") as wf:

		#write csv header
		csv_header = weibo_module.get_csv_header()
		wf.write(csv_header + "\n")

		#iterate through posts
		for this_post_id in query_post_ids:

			print "\n==WRITING POST #=========", this_post_id

			# okay first we get the initial post
			this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

			# and then we scan the rest 
			this_post_all_logs =  weibo_module.get_all_posts(this_post_id)

			# and then we amass a logline -- a csv file inside a csv file!
			this_log_line = []
			for this_log in this_post_all_logs:
				if 'post_repost_count' in this_log and this_log["post_repost_count"] <> None:
					this_log_line.append(str(this_log["post_repost_count"]))
					this_log_line.append(str(this_log["checked_at"]))
			this_log_line = weibo_settings.delim_log.join(this_log_line)

			#get csvline array
			csvline = weibo_module.make_csvline_from_post(this_post)

			#make each element in array unicode
			csvline = map((lambda x: unicode(x)), csvline)

			#join with delimiter
			csvline = weibo_settings.delim.join(csvline)

			#add logline
			csvline += weibo_settings.delim
			csvline += this_log_line

			#write  csvline
			wf.write(csvline + "\n")

#################################
#################################
#################################
#################################


#our process
#grab all the deleted posts
#massage to CSV!
all_log__eibo_filename = weibo_settings.all_log_csv_filename
#csvize_deleted_repost_timeline(weibo_settings.all_log_csv_filename, 10023, True)
csvize_repost_timeline(weibo_settings.all_log_csv_filename, "all")
csvize_repost_timeline(weibo_settings.deleted_log_csv_filename, "deleted", 10023, True)

#deleted_in_sample()


