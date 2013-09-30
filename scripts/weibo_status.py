import time
import sys
import weibo_module
from json import loads
from urllib import urlretrieve
from os.path import splitext, isdir
from dateutil import parser


##########################################
## CHECK FOR LIVE POSTS
##########################################
def check_for_live_posts():

	dbcursor = weibo_module.db_cursor()
	tracking_post_ids = weibo_module.get_tracking_postids()
	num_currently_tracking = len(tracking_post_ids)

	if (num_currently_tracking == 0):
		print "No posts are being tracked right now." 
	print "Currently tracking " + str(num_currently_tracking) + " posts"

	return num_currently_tracking


##########################################
## HAS ENOUGH TIME PASSED?
##########################################
def display_tracking_interval():

	# get current time
#	nowdatetime = weibo_module.get_current_chinatime()
	timelapsed = -1

	# when was the last time we checked
	most_recent_check = weibo_module.get_most_recent_check()

	if most_recent_check == -1:
		print "Never been tracked!"

	else:	
		# okay, so has it been long enough?
		timelapsed = nowdatetime - most_recent_check

		print "It's been " + weibo_module.minsec(timelapsed.seconds) + " min since our most recent check, which was on" , most_recent_check	

	print "We're checking posts every " + weibo_module.minsec(weibo_module.tracking_period_seconds) + " minutes." 



##########################################
## GET LIST OF LIVE POSTS
##########################################
def list_live_posts():

	tracking_post_ids = weibo_module.get_tracking_postids()

	print "########## POSTS TRACKING ##########"
	print "# of posts we're tracking: " , len(tracking_post_ids)

	if (len(tracking_post_ids) > 0):

		for this_post_id in tracking_post_ids:
			print "Checking post #" + this_post_id + ":",

			this_post_new = weibo_module.get_most_recent_live_post(this_post_id)
			this_post_old = weibo_module.get_oldest_post(this_post_id)

			print "alive: new/old repost count (" , this_post_new["post_repost_count"] , " / " , this_post_old["post_repost_count"] , ") "

#			print "* this_post_new = " , this_post_new

			elapsedtime  = nowdatetime - weibo_module.set_timezone_to_china(this_post_new["started_tracking_at"]) 
			print "elapsed time = " ,  elapsedtime
	#k		print elapsedtime.seconds


			#print this_post_old["checked_at"]
			#print this_post_old["started_tracking_at"]
	#		print weibo_module.minsec(this_post_new["checked_at"] - this_post_new["started_tracking_at"]) + " since tracking start"
			#print this_post_check["checked_at"] , " " , this_post_old["started_tracking_at"]


##########################################
## GET LIST OF DEAD POSTS
##########################################
def list_deleted_posts():

	deleted_post_ids = weibo_module.get_deleted_postids()

	print ""
	print "########## DEAD POSTS ##########"
	num_dead_posts = len(deleted_post_ids)
	print "# of dead posts we've tracked: " + str(num_dead_posts)
	if (num_dead_posts > 0):
		dead_post_ids = []

		for this_post_id in deleted_post_ids:
			print "Checking post # " + this_post_id , "::::: ",

			# get the post info from postids_live collection,
			# since if the post was deleted we wouldn't have any of that info anymore

			this_post_deleted = weibo_module.merge_deleted_from_new_old(this_post_id)
			print "ERRORCODE = " , this_post_deleted["error_code"]

			print "alive: new/old repost count (" , this_post_deleted["post_repost_count"] , " / " , this_post_deleted["post_repost_count_initial"] , ") "
		#	print " >> post alive: new/old repost count (" + str(statusresponse["reposts_count"]) + " / " + str(this_post["post_repost_count"]) + ") "

##########################################
## GET LIST OF RETIRED POSTS
##########################################
def list_retired_posts():

	retired_post_ids = weibo_module.get_retired_postids()

	print ""
	print "########## RETIRED POSTS ##########"
	num_retired_posts = len(retired_post_ids)
	print "# of retired posts we've tracked: " + str(num_retired_posts)
	if (num_retired_posts > 0):
		retired_post_ids = []

		for this_post_id in retired_post_ids:
			print "Checking post # " + this_post_id , 

			# get the post info from postids_live collection,
			# since if the post was retired we wouldn't have any of that info anymore

			this_post_new = weibo_module.get_most_recent_live_post(this_post_id)
			this_post_old = weibo_module.get_oldest_post(this_post_id)



			print "alive: new/old repost count (" , this_post_new["post_repost_count"] , " / " , this_post_old["post_repost_count"] , ") "
		#	print " >> post alive: new/old repost count (" + str(statusresponse["reposts_count"]) + " / " + str(this_post["post_repost_count"]) + ") "



################
################
################
################


print "##################################"
print "########## WEIBO STATUS ##########"
print "##################################"

print weibo_module.post_alert()
nowdatetime = weibo_module.get_current_chinatime()
numlive = check_for_live_posts()
if numlive > 0:
	list_live_posts()
#list_retired_posts()
#list_deleted_posts()


