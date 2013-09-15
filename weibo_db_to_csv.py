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


csv_header='post_id,user_id,user_name,user_follower_count_initial,user_follower_count,post_original_pic,post_created_at,post_repost_count_initial,post_repost_count,post_text,started_tracking_at,is_deleted,is_retired,error_message,error_code,last_checked_at,time_elapsed,post_lifespan'


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
		wf.write(csv_header + "\n")
		print csv_header

		#iterate through posts
		for this_post_id in deleted_post_ids:

			this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

			csvline = weibo_module.make_csvline_from_post(this_post)

		
			csvline = map((lambda x: unicode(x)), csvline)
			csvline = u','.join(csvline)

			print csvline
			wf.write(csvline + "\n")



###
#let's print a log of all deleted posts, with the repost count/checked time following as pairs. so:
# post_id, user id, etc....... and then , unixepoch, repost count, unixepoch, repost count.... 

#if exclude_error_code = false, use error_code as filter
def csvize_deleted_repost_timeline(csv_filename, error_code=-1, exclude_error_code=False):

	nowdatetime = weibo_module.get_current_chinatime()

	deleted_post_ids = weibo_module.get_deleted_postids(error_code, exclude_error_code)
	num_dead_posts = len(deleted_post_ids)

	#if we're not tracking any posts, get out of there
	if (num_dead_posts <= 0):
		return

	## OPEN A FILE
	with codecs.open(csv_filename, "w", "utf-16") as wf:

		#write csv header
		wf.write(csv_header + "\n")
		print csv_header

		#iterate through posts
		for this_post_id in deleted_post_ids:

			print "===========", this_post_id
			# okay first we get the initial post
			this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

#			print "THISPOST" , this_post
			# and then we scan the rest 
			this_post_all_logs =  weibo_module.get_all_posts(this_post_id)

			for this_log in this_post_all_logs:
#				print "##############################tpal"
#				print "THISLOG" , this_log
#				print "CHECKEDAT "  , this_log["checked_at"]
				if 'post_repost_count' in this_log:
					print this_log["post_repost_count"], " :: " , this_log["checked_at"]
#				print "##############################tpalE"
							

			csvline = weibo_module.make_csvline_from_post(this_post)
		
			csvline = map((lambda x: unicode(x)), csvline)
			csvline = u','.join(csvline)

#			print csvline
			wf.write(csvline + "\n")

#################################
#################################
#################################
#################################


#our process
#grab all the deleted posts
#massage to CSV!
#csvize_sample()
deleted_weibo_filename = weibo_settings.csv_filename
#csvize_deleted_unique(deleted_weibo_filename, 20101  )

csvize_deleted_repost_timeline(deleted_weibo_filename, 20101 )

#deleted_in_sample()


