import pymongo
import csv
import json
import datetime
from dateutil.parser import parse
import requests
import logging
import re
import os
import weibomodule



def csvize_deleted_unique(csv_filename):

	csv_header = "post_id, user_id, user_name, user_follower_count_initial, user_follower_count, post_original_pic, post_created_at, post_repost_count_initial, post_repost_count, post_text, started_tracking_at, is_deleted, is_retired, error_message, error_code, last_checked_at"

	deleted_post_ids = weibomodule.get_deleted_postids()
	num_dead_posts = len(deleted_post_ids)

	#if we're not tracking any posts, get out of there
	if (num_dead_posts <= 0):
		return

	## OPEN A FILE
	with open(csv_filename, "w") as wf:
		wf.write(codecs.BOM_UTF)

		#write csv header
		wf.write(csv_header + "\n")
		print csv_header

		#iterate through posts
		for this_post_id in deleted_post_ids:

			this_post_new = weibomodule.get_most_recent_live_post(this_post_id)
			this_post_old = weibomodule.get_oldest_post(this_post_id)
			this_post_deleted = weibomodule.get_deletion_post(this_post_id)
			#the only items that change between the two is the "initial" items

			this_post = this_post_old
			this_post["user_follower_count_initial"] = this_post_old["user_follower_count"]
			this_post["user_follower_count"] = this_post_new["user_follower_count"]
			this_post["post_repost_count_initial"] = this_post_old["post_repost_count"]
			this_post["post_repost_count"] = this_post_new["post_repost_count"]
			this_post["started_tracking_at"] = this_post_old["started_tracking_at"]
			this_post["error_code"] = this_post_deleted["error_code"] 
			this_post["error_message"] = this_post_deleted["error_message"] 
			# we're setting the "deleted time" to be when it was found to be deleted
			# that means that, depending on the interval T, 
			# the actual deletion time is always between 0 and T later
			this_post["last_checked_at"] = this_post_new["checked_at"]


			csv_line = this_post["post_id"] + ", " +  this_post["user_id"] + ", " +  this_post["user_name"] + ", " +  this_post["user_follower_count_initial"] + ", " +  this_post["user_follower_count"] + ", " +  this_post["post_original_pic"] + ", " +  this_post["post_created_at"] + ", " +  this_post["post_repost_count_initial"] + ", " +  this_post["post_repost_count"] + ", " +  this_post["post_text"] + ", " +  this_post["started_tracking_at"] + ", " +  this_post["is_deleted"] + ", " +  this_post["is_retired"] + ", " +  this_post["error_message"] + ", " +  this_post["error_code"] + ", " +  this_post["last_checked_at"]

			wf.write(csv_line + "\n")
			print csv_line


def search_date(postid):

	print "=========" 
	print "==POSTID = " + str(postid) 


	thiscreated = -1

	for i in xrange(1,10, 1):
		increment = i
		searchid = int(postid) + increment

		r = requests.get('https://api.weibo.com/2/statuses/show.json', params={"access_token": weibo_accesstoken, "id": searchid })

		rdata = r.json()

#		print rdata
		try:
			if rdata["error"] == "User requests out of rate limit!":
			#try agin later
				return -10
		except:
			pass

		print rdata
		if "created_at" in rdata:
		#if rdata["created_at"] is not None:
			#print rdata["created_at"]
			print  "=====  searching for " + str(searchid )+ ": FOUND" 
#			logging.debug(rdata["created_at"])
			thiscreated = parse(rdata['created_at']).strftime('%s')
			return thiscreated

		print  "=====  searching for " + str(searchid )+ ": NO" 

	return thiscreated


	#weibo_postid_querystring


#################################
#################################
#################################
#################################


#our process
#grab all the deleted posts
#massage to CSV!
#csvize_sample()
deleted_weibo_filename = "deleted_weibo.csv"

csvize_deleted_unique(deleted_weibo_filename)
#deleted_in_sample()


