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

collection_checklog = weibomodule.get_db_collection(weibomodule.collection_checklog)
collection_postids_live = weibomodule.get_db_collection(weibomodule.collection_postids_live)
collection_checked_at_times = weibomodule.get_db_collection(weibomodule.collection_checked_at_times)

print "##################################"
print "########## WEIBO STATUS ##########"
print "##################################"

num_live_posts = collection_postids_live.find({"is_alive":"True"}).count()
if (num_live_posts == 0):
	sys.exit("No posts are being tracked right now.")
print "Currently tracking " + str(num_live_posts) + " posts"


##########################################
## HAS ENOUGH TIME PASSED?
##########################################


# get current time
nowtimestamp = int(time.time())
timelapsed = -1

# when was the last time we checked
most_recent_check = collection_checked_at_times.find_one({}, sort=[('checked_at', -1)])

try:
	lasttimestamp = int(most_recent_check["checked_at"])

except:
	# never been tracked! so let's just go ahead
	print "Never been tracked!"

else:	
	# okay, so has it been long enough?
	timelapsed = nowtimestamp - lasttimestamp

	print "It's been " + weibomodule.minsec(timelapsed) + " since we last checked"	

print "We're checking posts every " + weibomodule.minsec(weibomodule.tracking_period_seconds) + " minutes." 

##########################################
## GET LIST OF LIVE POSTS
##########################################

print "########## LIVE POSTS ##########"
num_live_posts = collection_postids_live.find({"is_alive":"True"}).count()
print "# of live posts we've tracked: " + str(num_live_posts)
if (num_live_posts > 0):
	live_post_ids = []
	for lpis in collection_postids_live.find({"is_alive":"True"}):
		live_post_ids.append(lpis["post_id"])
#	print live_post_ids


	for this_post_id in live_post_ids:
		print "Checking post #" + this_post_id + ":",

		this_post_old = collection_postids_live.find_one({'post_id': this_post_id, "is_alive":"True"}, sort=[('checked_at', -1)])
		this_post_check = collection_checklog.find_one({'post_id': this_post_id, "is_alive":"True"}, sort=[('checked_at', -1)])

		print "alive: new/old repost count (" + str(this_post_check["post_repost_count"]) + " / " + str(this_post_old["initial_post_repost_count"]) + ") "

		print weibomodule.minsec(this_post_check["checked_at"] - this_post_old["started_tracking_at"]) + " since tracking start"
		#print this_post_check["checked_at"] , " " , this_post_old["started_tracking_at"]


##########################################
## GET LIST OF DEAD POSTS
##########################################

print "########## DEAD POSTS ##########"
num_dead_posts = collection_postids_live.find({"is_alive":"False"}).count()
print "# of dead posts we've tracked: " + str(num_dead_posts)
if (num_dead_posts > 0):
	dead_post_ids = []
	for lpis in collection_postids_live.find({"is_alive":"False"}):
		dead_post_ids.append(lpis["post_id"])
	print dead_post_ids


	for this_post_id in dead_post_ids:
		print "Checking post # " + this_post_id

		# get the post info from postids_live collection,
		# since if the post was deleted we wouldn't have any of that info anymore
		this_post = collection_postids_live.find_one({'post_id': this_post_id, "is_alive":"True"})

	#	print " >> post alive: new/old repost count (" + str(statusresponse["reposts_count"]) + " / " + str(this_post["post_repost_count"]) + ") "


