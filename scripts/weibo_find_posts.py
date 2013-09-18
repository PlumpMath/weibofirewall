import time
import pytz
import sys
import weibo_module
import weibo_settings
from json import loads
from urllib import urlretrieve
from os.path import splitext, isdir
from dateutil import parser
import urllib2
import socket
socket.setdefaulttimeout(30)


## WHAT WE DO HERE
## WE CHECK HOW MANY POSTS WE NEED TO TRACK MORE, IF ANY
## IF WE DO, WE ITERATE THROUGH THE POSTS OF FRIENDS
## AND FIND NEW POSTS THAT WE DON'T CURRENLTY HAVE
## WE INSERT THEM INTO col_currently_tracking
## AS WELL AS LOG A CHECK INTO col_checklog

#"SCHEMA"
"""
post_id
user_id
user_name
user_follower_count
post_original_pic
post_created_at
post_repost_count
post_text
started_tracking_at
is_deleted
is_retired
error_message
error_code
checked_at
"""
# CREATE TABLE checklog (post_id VARCHAR(20), user_id VARCHAR(20), user_name VARCHAR(30), user_follower_count INT, post_original_pic TEXT, post_created_at DATETIME, post_repost_count INT, post_text TEXT, started_tracking_at DATETIME, is_deleted  TINYINT, is_retired TINYINT, error_message VARCHAR(255), error_code VARCHAR(255), checked_at DATETIME);

##########################################
## INIT VARIABLES
##########################################

thispostbuffer = []

newpostcount = 0
statuspage = 1



##########################################
## OPEN DB, CHECK TO SEE IF IMG FOLDER EXISTS
##########################################

dbcursor = weibo_module.db_cursor()

if(isdir(weibo_settings.imgdir) == False):
	sys.exit("No such directory " + weibo_settings.imgdir)

##########################################
## CHECK TO SEE HOW MANY POSTS WE ARE TRACKING
##########################################

tracking_post_ids = weibo_module.get_tracking_postids()
num_currently_tracking = len(tracking_post_ids)
num_posts_to_track = weibo_module.num_posts_to_track()
num_trackmore = num_posts_to_track - num_currently_tracking 

nowdatetime =  weibo_module.get_current_chinatime()

print "The DATE/TIME IS " , nowdatetime

# if we're tracking more than we need, exit.
if (num_trackmore <= 0):
	print "Currently tracking all " + str(num_currently_tracking) + " posts:"
	print "After all, we can only track a max of " + str(weibo_module.num_posts_to_track()) + " posts"
	counter = 1
	for thispostid in tracking_post_ids:
		thispost = weibo_module.get_most_recent_live_post(thispostid)
		print "post #" , counter ,":" + thispost["post_id"] + ", started tracking at" , thispost["started_tracking_at"]
		print "was created at " , thispost["post_created_at"]
		counter += 1
	sys.exit(0)
#	sys.exit("Currently tracking all " + str(num_currently_tracking) + " posts.")

print "Currently tracking " + str(num_currently_tracking) + " posts"
print "Attempting to find " + str(num_trackmore) + " more posts to track"
print " -- for a total of " + str(num_posts_to_track) + " tracked posts"
print weibo_module.post_alert()


##########################################
## GET DATA
##########################################

statuspage = 1
loop = True 

# get current time
# EVERYTHING IS ON CHINA TIME, YOU UNDERSTAND

nowdatetime =  weibo_module.get_current_chinatime()

#this could be a while loop, but let's not go more than a given number of  pages back.
for i in xrange(weibo_settings.pagemax):

	print "Accessing statuses - page " + str(statuspage) + " ..."

	# grab json-decoded statuses of friends
	statusresponse = weibo_module.accessfriends(page=statuspage)

	#response = statusdata.json()
	# extract statuses
	jarray = statusresponse["statuses"]


	##########################################
	## PUSH DATA INTO MEMORY
	##########################################

	print "Parsing statuses..."


	for i in xrange(len(jarray)):
	# If this is a retweet and the original Weibo has an image, get the original

		if "retweeted_status" in jarray[i] and "original_pic" in jarray[i]["retweeted_status"]:

			#createdtimestamp = parser.parse(jarray[i]["created_at"]).strftime('%s')
			# THIS IS CHINA TIME
			createddatetime = parser.parse(jarray[i]["created_at"]).strftime('%Y-%m-%d %H:%M:%S')

			thispost = {
				"post_id": jarray[i]["retweeted_status"]["idstr"],
				"user_id": jarray[i]["retweeted_status"]["user"]["id"],
				"user_name": jarray[i]["retweeted_status"]["user"]["screen_name"],
				"user_follower_count": jarray[i]["retweeted_status"]["user"]["followers_count"],
				"post_original_pic": jarray[i]["retweeted_status"]["original_pic"],
				"post_created_at": createddatetime,
				"post_repost_count": jarray[i]["retweeted_status"]["reposts_count"],
				"post_text": unicode(jarray[i]["retweeted_status"]["text"]),
				"started_tracking_at": nowdatetime,
				"is_deleted": 0,
				"is_retired": 0,
				"error_message": "",
				"error_code": "",
				"checked_at": nowdatetime,
			}

			thispostbuffer.append(thispost)


		# If this is an original Weibo, no retweets and it has an image
		elif "original_pic" in jarray[i]:
			createdtimestamp = parser.parse(jarray[i]["created_at"]).strftime('%s')
			createddatetime = parser.parse(jarray[i]["created_at"]).strftime('%Y-%m-%d %H:%M:%S')

			thispost = {
				"post_id":	jarray[i]["idstr"],
				"user_id":	jarray[i]["user"]["id"],
				"user_name":	jarray[i]["user"]["screen_name"],
				"user_follower_count":	jarray[i]["user"]["followers_count"],
				"post_original_pic":	jarray[i]["original_pic"],
				"post_created_at":	createddatetime,
				"post_repost_count":	jarray[i]["reposts_count"],
				"post_text":	unicode(jarray[i]["text"]),
				"started_tracking_at": nowdatetime,
				"is_deleted": 0,
				"is_retired": 0,
				"error_message": "",
				"error_code": "",
				"checked_at": nowdatetime
			}

			thispostbuffer.append(thispost)
	

	##########################################
	## STORE IN DATABASE
	##########################################

	print "Storing statuses in db..."

	# store in db.
	# we're looking for new posts only
	for i in xrange(len(thispostbuffer)):

		#only put in as many as we need.
		if(newpostcount >= num_trackmore):
			# break out of larger loop
			loop = False
			break


		thispost = thispostbuffer[i]

		#print thispost["post_id"]

		#if you can't find the post already in Mongo, put it in:
		if (weibo_module.postexists(thispost["post_id"]) == False):
			#POST IS NEW - let's save it

			newpostcount += 1

			imgpath = weibo_settings.imgdir + str(thispost["post_id"])+ splitext(thispost["post_original_pic"])[1]
			print "Storing postID -- tracking post #" , (num_currently_tracking + newpostcount)
			print "Storing postID " + str(thispost["post_id"] + " image to file")


			#DOWNLOAD IMAGE
			"""	req = urllib2.Request(thispost["post_original_pic"])
			response = urllib2.urlopen(req)
			output = open(l'wb')
			output.write(response.read())
			output.close()"""

			urlretrieve(thispost["post_original_pic"], imgpath)

			print "Storing postID " + str(thispost["post_id"] + " to database")
			weibo_module.checklog_insert(thispost)

		else:
			print "post " + str(thispost["post_id"]) + " already exists"

	if (loop == False):
		break

	statuspage += 1

print str(newpostcount) + " posts added, for a total of " + str(num_currently_tracking + newpostcount) + " posts"




