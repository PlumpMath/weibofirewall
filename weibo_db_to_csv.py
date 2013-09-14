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
import weibo_module


def csvize_deleted_unique(csv_filename, error_code=-1):

	csv_header='post_id,user_id,user_name,user_follower_count_initial,user_follower_count,post_original_pic,post_created_at,post_repost_count_initial,post_repost_count,post_text,started_tracking_at,is_deleted,is_retired,error_message,error_code,last_checked_at,time_elapsed,post_lifespan'

	nowdatetime = weibo_module.get_current_chinatime()

	deleted_post_ids = weibo_module.get_deleted_postids(error_code)
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

			this_post_new = weibo_module.get_most_recent_live_post(this_post_id)
			this_post_old = weibo_module.get_oldest_post(this_post_id)
			this_post_deleted = weibo_module.get_deletion_post(this_post_id)
			#the only items that change between the two is the "initial" items

			thispost_created_at = weibo_module.set_timezone_to_china(this_post_old['post_created_at'])
			thispost_lifespan = nowdatetime - thispost_created_at
			thispost_lifespan = weibo_module.total_seconds(thispost_lifespan)

			this_post = this_post_old
			this_post["user_follower_count_initial"] = str(this_post_old["user_follower_count"])
			this_post["user_follower_count"] = str(this_post_new["user_follower_count"])
			this_post["post_repost_count_initial"] = str(this_post_old["post_repost_count"])
			this_post["post_repost_count"] = str(this_post_new["post_repost_count"])
			this_post["started_tracking_at"] = this_post_old["started_tracking_at"].strftime('%Y-%m-%d %H:%M:%S')
			this_post["error_code"] = this_post_deleted["error_code"] 
			this_post["error_message"] = this_post_deleted["error_message"] 
			this_post["is_deleted"] = this_post_deleted["is_deleted"] 
			# we're setting the "deleted time" to be when it was found to be deleted
			# that means that, depending on the interval T, 
			# the actual deletion time is always between 0 and T later
			this_post["last_checked_at"] = this_post_new["checked_at"].strftime('%Y-%m-%d %H:%M:%S')
			this_post["post_created_at"] = this_post_new["post_created_at"].strftime('%Y-%m-%d %H:%M:%S')
			this_post["post_lifespan"] = thispost_lifespan

			csvline = this_post["post_id"] , this_post["user_id"] , this_post["user_name"] , this_post["user_follower_count_initial"] , this_post["user_follower_count"] , this_post["post_original_pic"] , this_post["post_created_at"] , this_post["post_repost_count_initial"] , this_post["post_repost_count"] , this_post["post_text"] , this_post["started_tracking_at"] , this_post["is_deleted"] , this_post["is_retired"] , this_post["error_message"] , this_post["error_code"] , this_post["last_checked_at"] , this_post["post_lifespan"]

		
			csvline = map((lambda x: unicode(x)), csvline)
			csvline = u','.join(csvline)

			print csvline
			wf.write(csvline + "\n")

#################################
#################################
#################################
#################################


#our process
#grab all the deleted posts
#massage to CSV!
#csvize_sample()
deleted_weibo_filename = "deleted_weibo.csv"
csvize_deleted_unique(deleted_weibo_filename, 20101 )
#deleted_in_sample()


