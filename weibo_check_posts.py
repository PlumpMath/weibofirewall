import time
import sys
import weibo_settings
import weibo_module
import traceback
from json import loads
from urllib import urlretrieve
from os.path import splitext, isdir
from dateutil import parser


##########################################
## OPEN DB
##########################################

dbcursor = weibo_module.db_cursor()

tracking_post_ids = weibo_module.get_tracking_postids()
num_currently_tracking = len(tracking_post_ids)

if (num_currently_tracking == 0):
	sys.exit("No posts are being tracked right now.")
print "Currently tracking " + str(num_currently_tracking) + " posts"
print weibo_module.post_alert()

##########################################
## GET LIST OF LIVE POSTS
##########################################

#print tracking_post_ids

##########################################
## HAS ENOUGH TIME PASSED?
##########################################

# get current time
nowdatetime = weibo_module.get_current_chinatime()
timelapsed = -1

# when was the last time we checked
most_recent_check = weibo_module.get_most_recent_checktime()

# okay, so has it been long enough?
timelapsed = nowdatetime - most_recent_check

print "It's been " + weibo_module.minsec(weibo_module.total_seconds(timelapsed)) + " min since our most recent check, which was on" , most_recent_check	

if (weibo_module.total_seconds(timelapsed) < weibo_settings.tracking_period_seconds):
	#not enough time has passed, too bad!
	print "... But we're checking posts every " + weibo_module.minsec(weibo_settings.tracking_period_seconds) + " minutes!" 
	print "We'll check next time."
	sys.exit(0)

# never been tracked! so let's just go ahead
print "Let's start tracking!"
print "====================="

##########################################
## CHECK EACH POST & LOG IN DB
##########################################

#iterate through all of them, rotating tokens. 

# pseudocode
# does it exist? NO --- it was deleted! turn the flag on, log in checklog
# does it exist? YES! -- too old? NO:  log in checklog
# does it exist? YES! -- too old? YES: turn flag on,  log in checklog

checkpostcount = 0 

for this_post_id in tracking_post_ids:
	checkpostcount += 1

	print "=========================="
	print "CHECK", checkpostcount , ":: checking post # " + this_post_id
	thispost_is_alive = True


	this_post_newest = weibo_module.get_most_recent_live_post(this_post_id)
	this_post_oldest = weibo_module.get_oldest_post(this_post_id)
	thispost_created_at = weibo_module.set_timezone_to_china(this_post_newest['post_created_at'])
	elapsedtime = nowdatetime - thispost_created_at 

#	print "now is = " , nowdatetime
#	print "newest sez created at = " , this_post_newest["post_created_at"]
#	print "oldt commitest sez created at = " , this_post_oldest["post_created_at"]
	print "* time elapsed = " , elapsedtime, " and in seconds" , weibo_module.total_seconds(elapsedtime)


# so - we look for the post
# if we have an error, assemble a skeletal post consisting of post id, is_deleted, error message, error code, checekd_at, and then put it in checklog.
# whic means that we should check first for the existenc of an error
# refreshpost will give us back the error, otherwise returns a dict 


	try:
		refreshedpost  =  weibo_module.refreshpost(this_post_id)
	except:
		#hmm. can't even check status. weird.
		print "okay weird error"
		traceback.print_exc(file=sys.stdout)
		continue


	#set post checked_at time
	refreshedpost["checked_at"] = nowdatetime

#	print "* refrehsedpost = " ,refreshedpost

	if ("error_code" in refreshedpost):
		#the post has been DELETED
		#let's flag, add to checklog
		print " >> POST DELETED: " + refreshedpost["error_message"]
		weibo_module.checklog_insert(refreshedpost)

	else:
	
		#post EXISTS

		print "* post alive: new/old repost count (" + str(refreshedpost["post_repost_count"]) + " / " + str(this_post_oldest["post_repost_count"]) + ") "

#		print "* elapsed time = " , weibo_module.total_seconds(elapsedtime) 
#		print "* our timeout is = " , weibo_module.track_posts_timeout
#		print "* so has more time passed? " , (weibo_module.total_seconds(elapsedtime) > weibo_module.track_posts_timeout)

		if (weibo_module.total_seconds(elapsedtime) > weibo_settings.track_posts_timeout):
			#TOO MUCH TIME HAS PASSED - let's retire this
			print "Too much time has passed! We're not tracking this anymore."
			#LOOK THIS POST UP AGAIN
			refreshedpost["is_retired"] = 1
			weibo_module.checklog_insert(refreshedpost)

		else:
			#post EXISTS as usual.	
			#print "Okay, log it and move on.."
			weibo_module.checklog_insert(refreshedpost)


print "Done."
