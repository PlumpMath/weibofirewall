import time
import sys
import weibomodule
import traceback
from json import loads
from urllib import urlretrieve
from os.path import splitext, isdir
from dateutil import parser


##########################################
## OPEN DB
##########################################

dbcursor = weibomodule.db_cursor()

tracking_post_ids = weibomodule.get_tracking_postids()
num_currently_tracking = len(tracking_post_ids)

if (num_currently_tracking == 0):
	sys.exit("No posts are being tracked right now.")
print "Currently tracking " + str(num_currently_tracking) + " posts"
print weibomodule.post_alert()

##########################################
## GET LIST OF LIVE POSTS
##########################################

#print tracking_post_ids

##########################################
## HAS ENOUGH TIME PASSED?
##########################################

# get current time
nowdatetime = weibomodule.get_current_chinatime()
timelapsed = -1

# when was the last time we checked
most_recent_check = weibomodule.get_most_recent_check()

# okay, so has it been long enough?
timelapsed = nowdatetime - most_recent_check

print "It's been " + weibomodule.minsec(timelapsed.seconds) + " min since our most recent check, which was on" , most_recent_check	

if (timelapsed.seconds < weibomodule.tracking_period_seconds):
	#not enough time has passed, too bad!
	print "... But we're checking posts every " + weibomodule.minsec(weibomodule.tracking_period_seconds) + " minutes!" 
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

for this_post_id in tracking_post_ids:
	print "Checking post # " + this_post_id
	thispost_is_alive = True


	# get the post info from postids_live collection,
#	this_post = collection_postids_live.find_one({'post_id':unicode(this_post_id)})
	this_post = weibomodule.get_most_recent_post(this_post_id)

	thispost_createdat = weibomodule.makedateaware(this_post['post_created_at'])
	elapsedtime = nowdatetime - thispost_createdat 

	refreshedpost  =  weibomodule.refreshpost(this_post_id)
	refreshedpost["started_tracking_at"] = this_post["started_tracking_at"]
	refreshedpost["checked_at"] = nowdatetime
	try:
		statusresponse =  weibomodule.checkstatus(this_post_id)
	except:
		print "okay weird error"
		traceback.print_exc(file=sys.stdout)

		continue



	if ("error" in statusresponse):
		#the post has been DELETED
		#let's flag, add to checklog
		print " >> POST DELETED: " + statusresponse["error"]

		refreshedpost["is_deleted"] = 1
		refreshedpost["error_message"] = statusresponse["error"]
		weibomodule.checklog_insert(refreshedpost)

	else:
	
		#post EXISTS

		print " >> post alive: new/old repost count (" + str(statusresponse["reposts_count"]) + " / " + str(this_post["post_repost_count"]) + ") "

		if (elapsedtime.seconds > weibomodule.track_posts_timeout):
			#TOO MUCH TIME HAS PASSED - let's retire this
			print "Too much time has passed! We're not tracking this anymore."
			#LOOK THIS POST UP AGAIN
			refreshedpost["is_retired"] = 1
			weibomodule.checklog_insert(refreshedpost)

		else:
			#post EXISTS as usual.	
			#print "Okay, log it and move on.."
			weibomodule.checklog_insert(refreshedpost)


print "Done."
