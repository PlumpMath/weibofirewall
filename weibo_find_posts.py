import time
import pytz
import sys
import weibomodule
from json import loads
from urllib import urlretrieve
from os.path import splitext, isdir
from dateutil import parser
from datetime import datetime


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

dbcursor = weibomodule.db_cursor()

if(isdir(weibomodule.imgdir) == False):
	sys.exit("No such directory " + weibomodule.imgdir)

##########################################
## CHECK TO SEE HOW MANY POSTS WE ARE TRACKING
##########################################

thistest = weibomodule.getcurrentpostids()


# TEMPORARY FIX
num_currently_tracking = 0
num_posts_to_track = weibomodule.num_posts_to_track()
num_trackmore = num_posts_to_track - num_currently_tracking 

print num_trackmore
print "end_num_trackmire"

# if we're tracking more than we need, exit.
if (num_trackmore <= 0):
	print "Currently tracking all " + str(num_currently_tracking) + " posts:"
	print "After all, we can only track a max of " + str(weibomodule.num_posts_to_track()) + " posts"
	for lpis in collection_postids_live.find():
		thisdate = datetime.fromtimestamp(int(lpis["started_tracking_at"]), tz=pytz.timezone(weibomodule.display_timezone)).strftime('%Y-%m-%d %H:%M:%S %Z')
		print "post " + lpis["post_id"] + ", started tracking at " +  thisdate
	sys.exit(0)
#	sys.exit("Currently tracking all " + str(num_currently_tracking) + " posts.")

print "Currently tracking " + str(num_currently_tracking) + " posts"
print "Attempting to find " + str(num_trackmore) + " more posts to track"
print " -- for a total of " + str(num_posts_to_track) + " tracked posts"
print weibomodule.post_alert()


##########################################
## GET DATA
##########################################

statuspage = 1
loop = True 

# get current time
nowtimestamp = int(time.time())

#this could be a while loop, but let's not go more than a given number of  pages back.
for i in xrange(weibomodule.pagemax):

	print "Accessing statuses - page " + str(statuspage) + " ..."

	# grab json-decoded statuses of friends
	statusresponse = weibomodule.accessfriends(page=statuspage)

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

			createdtimestamp = parser.parse(jarray[i]["created_at"]).strftime('%s')
			createddatetime = parser.parse(jarray[i]["created_at"]).strftime('%Y-%m-%d %H:%M:%S')

			print createdtimestamp
			print createddatetime

			thispost = {
				"post_id": jarray[i]["retweeted_status"]["idstr"],
				"user_id": jarray[i]["retweeted_status"]["user"]["id"],
				"user_name": jarray[i]["retweeted_status"]["user"]["screen_name"],
				"user_follower_count": jarray[i]["retweeted_status"]["user"]["followers_count"],
				"post_original_pic": jarray[i]["retweeted_status"]["original_pic"],
				"post_created_at": createdtimestamp,
				"post_repost_count": jarray[i]["retweeted_status"]["reposts_count"],
				"post_text": unicode(jarray[i]["retweeted_status"]["text"]),
				"started_tracking_at": nowtimestamp,
				"is_deleted": 0,
				"is_retired": 0,
				"error_message": "",
				"error_code": "",
				"checked_at": nowtimestamp
			}

			thispostbuffer.append(thispost)

		# If this is an original Weibo, no retweets and it has an image
		elif "original_pic" in jarray[i]:
			createdtimestamp = parser.parse(jarray[i]["created_at"]).strftime('%s')

			thispost = {
				"post_id":	jarray[i]["idstr"],
				"user_id":	jarray[i]["user"]["id"],
				"user_name":	jarray[i]["user"]["screen_name"],
				"user_follower_count":	jarray[i]["user"]["followers_count"],
				"post_original_pic":	jarray[i]["original_pic"],
				"post_created_at":	createdtimestamp,
				"post_repost_count":	jarray[i]["reposts_count"],
				"post_text":	unicode(jarray[i]["text"]),
				"started_tracking_at": nowtimestamp,
				"is_deleted": 0,
				"is_retired": 0,
				"error_message": "",
				"error_code": "",
				"checked_at": nowtimestamp
			}

			thispostbuffer.append(thispost)
	
#		print thispost
	sys.exit()

	##########################################
	## STORE IN DATABASE
	##########################################

	print "Storing statuses in db..."

	# store in db.
	# we're looking for new posts only
	for i in xrange(len(post_id)):

		#only put in as many as we need.
		if(newpostcount >= num_trackmore):
			# break out of larger loop
			loop = False
			break

		print "xxx"
		print post_id[i]
		print "xxx"

		#if you can't find the post already in Mongo, put it in:
		#dbcursor.execute("SELECT * FROM %s WHERE post_id = %s", (weibomodule.checklog_tablename , post_id[i]))
		query = "SELECT COUNT(*) FROM %s WHERE post_id = %s" %('checklog', post_id[i])
		dbcursor.execute(query)
		res=dbcursor.fetchone()
		num_existing_posts=res[0]



		if (num_existing_posts == 0):
			newpostcount += 1
			imgpath = weibomodule.imgdir + str(post_id[i])+ splitext(original_pic[i])[1]
			print "Storing postID " + str(post_id[i] + " image to file")
			urlretrieve(original_pic[i], imgpath)
			print "Storing postID " + str(post_id[i] + " to database")
			collection_postids_live.insert({
				'post_id':post_id[i],
				'user_id':user_id[i],
				"checked_at": nowtimestamp,
				'started_tracking_at': nowtimestamp,
				'initial_user_follower_count':followers_count[i],
				'initial_post_repost_count':total_reposts_count[i],
				"user_name": screen_name[i],
				"user_follower_count": followers_count[i],
				"post_original_pic":original_pic[i], 
				"post_created_at": created_at[i], 
				"post_repost_count": total_reposts_count[i],
				"post_text": text[i],
				"is_alive":"True",
				"is_tracking":"True"
			})

			doc = {
				"post_id": post_id[i],
				"user_id":user_id[i],
				"checked_at": nowtimestamp,
				"user_name": screen_name[i],
				"user_follower_count": followers_count[i],
				"post_original_pic":original_pic[i], 
				"post_created_at": created_at[i], 
				"post_repost_count": total_reposts_count[i],
				"post_text": text[i],
				"is_alive":"True",
				"is_tracking":"True"
			}
			collection_checklog.insert(doc)
		else:
			print "post " + str(post_id[i]) + " already exists"

	if (loop == False):
		break

	statuspage += 1

print str(newpostcount) + " posts added, for a total of " + str(num_currently_tracking + newpostcount) + " posts"




