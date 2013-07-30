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

num_live_posts = collection_postids_live.find({"is_alive":"True"}).count()
if (num_live_posts == 0):
	sys.exit("No posts are being tracked right now.")
print "Currently tracking " + str(num_live_posts) + " posts"
print weibomodule.post_alert()

##########################################
## GET LIST OF LIVE POSTS
##########################################

live_post_ids = []
for lpis in collection_postids_live.find({"is_alive":"True"}):
	live_post_ids.append(lpis["post_id"])

print live_post_ids

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
	print "Let's start tracking!"
	pass

else:	
	# okay, so has it been long enough?
	timelapsed = nowtimestamp - lasttimestamp

	print "It's been " + weibomodule.minsec(timelapsed) + " min"	
	if (timelapsed < weibomodule.tracking_period_seconds):
		#not enough time has passed, too bad!
		print "... But we're checking posts every " + weibomodule.minsec(weibomodule.tracking_period_seconds) + " minutes!" 
		sys.exit(1)

##########################################
## CHECK EACH POST & LOG IN DB
##########################################

logged_checked_at = False

#iterate through all of them, rotating tokens. log an updated check into the checklog db
#actually we'd just use the friends timeline to do this. savea  few api calls



for this_post_id in live_post_ids:
	print "Checking post # " + this_post_id
	thispost_is_alive = True

	# get the post info from postids_live collection,
	# since if the post was deleted we wouldn't have any of that info anymore
	this_post = collection_postids_live.find_one({'post_id':unicode(this_post_id), "is_alive":"True"})

	try:
		statusresponse =  weibomodule.checkstatus(this_post_id)
	except:
		print "okay weird error"
		continue



	if ("error" in statusresponse):
		#the post has been DELETED
		print " >> POST DELETED: " + statusresponse["error"]

		thispost_is_alive = False

		#remove document from postids_live collection
		#by 'remove' we mean 'turn off the 'is_alive' tag
		#note error message and error code and deleted by
		collection_postids_live.update(
			{"post_id":this_post_id}, 
			{	'$set': {
					"is_alive":"False",
					"error_message": statusresponse['error'],
					"error_code": statusresponse['error_code'],
					"deleted_by": nowtimestamp 
					}
			}
		)
	
		# we're gonna adda nyways to the checklog - prepare info	

		#add an entry to the checklog no matter what
		#this way the checklog has the full info
		doc = {
		  "post_id": this_post_id,
		  "user_id": this_post["user_id"],
		  "checked_at": nowtimestamp,
		  "user_name": this_post["user_name"],
		  "user_follower_count": statusresponse["user"]["followers_count"],
		  "post_original_pic": statusresponse["original_pic"],
		  "post_created_at": statusresponse["created_at"],
		  "post_repost_count": statusresponse["reposts_count"],
		  "post_text": statusresponse["text"],
		  "deleted_by": nowtimestamp,
		  "error_message": api_response['error'],
		  "error_code": api_response['error_code'],
		  "is_alive" : "False"		
		}

	else:
		print " >> post alive: new/old repost count (" + str(statusresponse["reposts_count"]) + " / " + str(this_post["post_repost_count"]) + ") "

		# the post is still alive! prepare the doc accordingly
		doc = {
		  "post_id": this_post_id,
		  "user_id": this_post["user_id"],
		  "checked_at": nowtimestamp,
		  "user_name": this_post["user_name"],
		  "user_follower_count": statusresponse["user"]["followers_count"],
		  "post_original_pic": statusresponse["original_pic"],
		  "post_created_at": statusresponse["created_at"],
		  "post_repost_count": statusresponse["reposts_count"],
		  "post_text": statusresponse["text"],
		  "is_alive" : "True"
		}

	collection_checklog.insert(doc)
	# just log once the checked at time so we know when the last successful check was

if (logged_checked_at == False):
	collection_checked_at_times.insert({'checked_at':nowtimestamp})
	logged_checked_at = True


print "Done."
