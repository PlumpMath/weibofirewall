import time
import sys
import weibomodule
from json import loads
from urllib import urlretrieve
from os.path import splitext, isdir
from dateutil import parser


##########################################
## OPEN DB
##########################################

print "##################################"
print "########## WEIBO STATUS ##########"
print "##################################"

dbcursor = weibomodule.db_cursor()
tracking_post_ids = weibomodule.get_tracking_postids()
num_currently_tracking = len(tracking_post_ids)

if (num_currently_tracking == 0):
	sys.exit("No posts are being tracked right now.")
print "Currently tracking " + str(num_currently_tracking) + " posts"

##########################################
## HAS ENOUGH TIME PASSED?
##########################################


# get current time
nowdatetime = weibomodule.get_current_chinatime()
timelapsed = -1

# when was the last time we checked
most_recent_check = weibomodule.get_most_recent_check()

if most_recent_check == -1:
	print "Never been tracked!"

else:	
	# okay, so has it been long enough?
	timelapsed = nowdatetime - most_recent_check

	print "It's been " + weibomodule.minsec(timelapsed.seconds) + " min since our most recent check, which was on" , most_recent_check	

print "We're checking posts every " + weibomodule.minsec(weibomodule.tracking_period_seconds) + " minutes." 

##########################################
## GET LIST OF LIVE POSTS
##########################################

print "########## POSTS TRACKING ##########"
print "# of posts we're tracking: " , len(tracking_post_ids)

if (len(tracking_post_ids) > 0):

	for this_post_id in tracking_post_ids:
		print "Checking post #" + this_post_id + ":",

		this_post_new = weibomodule.get_most_recent_post(this_post_id)
		this_post_old = weibomodule.get_oldest_post(this_post_id)

		print "alive: new/old repost count (" , this_post_new["post_repost_count"] , " / " , this_post_old["post_repost_count"] , ") "

		elapsedtime  = nowdatetime - weibomodule.set_timezone_to_china(this_post_new["started_tracking_at"]) 
		print "elapsed time = " ,  elapsedtime
#k		print elapsedtime.seconds


		#print this_post_old["checked_at"]
		#print this_post_old["started_tracking_at"]
#		print weibomodule.minsec(this_post_new["checked_at"] - this_post_new["started_tracking_at"]) + " since tracking start"
		#print this_post_check["checked_at"] , " " , this_post_old["started_tracking_at"]


##########################################
## GET LIST OF DEAD POSTS
##########################################


deleted_post_ids = weibomodule.get_deleted_postids()

print ""
print "########## DEAD POSTS ##########"
num_dead_posts = len(deleted_post_ids)
print "# of dead posts we've tracked: " + str(num_dead_posts)
if (num_dead_posts > 0):
	dead_post_ids = []

	for this_post_id in deleted_post_ids:
		print "Checking post # " + this_post_id

		# get the post info from postids_live collection,
		# since if the post was deleted we wouldn't have any of that info anymore

		this_post_new = weibomodule.get_most_recent_post(this_post_id)
		this_post_old = weibomodule.get_oldest_post(this_post_id)



		print "alive: new/old repost count (" , this_post_new["post_repost_count"] , " / " , this_post_old["post_repost_count"] , ") "
	#	print " >> post alive: new/old repost count (" + str(statusresponse["reposts_count"]) + " / " + str(this_post["post_repost_count"]) + ") "

##########################################
## GET LIST OF RETIRED POSTS
##########################################


retired_post_ids = weibomodule.get_retired_postids()

print ""
print "########## RETIRED POSTS ##########"
num_retired_posts = len(retired_post_ids)
print "# of retired posts we've tracked: " + str(num_retired_posts)
if (num_retired_posts > 0):
	retired_post_ids = []

	for this_post_id in retired_post_ids:
		print "Checking post # " + this_post_id

		# get the post info from postids_live collection,
		# since if the post was retired we wouldn't have any of that info anymore

		this_post_new = weibomodule.get_most_recent_post(this_post_id)
		this_post_old = weibomodule.get_oldest_post(this_post_id)



		print "alive: new/old repost count (" , this_post_new["post_repost_count"] , " / " , this_post_old["post_repost_count"] , ") "
	#	print " >> post alive: new/old repost count (" + str(statusresponse["reposts_count"]) + " / " + str(this_post["post_repost_count"]) + ") "


