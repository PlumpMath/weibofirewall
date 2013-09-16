from json import loads
import time
import sys
from urllib import urlretrieve
from os.path import splitext, isdir
from dateutil import parser
#from IPython.core.display import Image
import weibomodule

##########################################
## INIT VARIABLES
##########################################

screen_name=[]
followers_count=[]
text = []
original_pic = []
created_at = []
post_id = []
user_id = []
total_reposts_count = []
newpostcount = 0


##########################################
## OPEN DB, CHECK TO SEE IF IMG FOLDER EXISTS
##########################################

collection_checklog = weibomodule.get_db_collection(weibomodule.collection_checklog)
collection_postids_live = weibomodule.get_db_collection(weibomodule.collection_postids_live)

if(isdir(weibomodule.imgdir) == False):
	sys.exit("No such directory " + weibomodule.imgdir)

##########################################
## CHECK TO SEE HOW MANY POSTS WE ARE TRACKING
##########################################

num_live_posts = collection_postids_live.count()

num_posts_to_track = weibomodule.num_posts_to_track()
num_trackmore = num_posts_to_track - num_live_posts

# if we're tracking more than we need, exit.
if (num_trackmore <= 0):
	print "Currently tracking all " + str(num_live_posts) + " posts:"
	for lpis in collection_postids_live.find():
		print lpis["post_id"]
	sys.exit(0)
#	sys.exit("Currently tracking all " + str(num_live_posts) + " posts.")

print "Currently tracking " + str(num_live_posts) + " posts"
print "Attempting to track " + str(num_trackmore) + " posts"
print " -- for a total of " + str(num_posts_to_track) + " tracked posts"

##########################################
## GET DATA
##########################################


print "Accessing statuses..."

# grab json-decoded statuses of friends
statusresponse = weibomodule.accessfriends()

#response = statusdata.json()
# extract statuses
jarray = statusresponse["statuses"]

# get current time
nowtimestamp = int(time.time())

##########################################
## PUSH DATA INTO MEMORY
##########################################

print "Parsing statuses..."

for i in xrange(len(jarray)):
# If this is a retweet and the original Weibo has an image, get the original
	if "retweeted_status" in jarray[i] and "original_pic" in jarray[i]["retweeted_status"]:
		screen_name.append(jarray[i]["retweeted_status"]["user"]["screen_name"])
		user_id.append(jarray[i]["retweeted_status"]["user"]["id"])
		followers_count.append(jarray[i]["retweeted_status"]["user"]["followers_count"])
		text.append(unicode(jarray[i]["retweeted_status"]["text"]))
		original_pic.append(jarray[i]["retweeted_status"]["original_pic"])
		created_at.append(jarray[i]["retweeted_status"]["created_at"])
		post_id.append(jarray[i]["retweeted_status"]["idstr"])
		total_reposts_count.append(jarray[i]["retweeted_status"]["reposts_count"])

	# If this is an original Weibo, no retweets and it has an image
	elif "original_pic" in jarray[i]:
		screen_name.append(jarray[i]["user"]["screen_name"])
		user_id.append(jarray[i]["user"]["id"])
		followers_count.append(jarray[i]["user"]["followers_count"])
		text.append(unicode(jarray[i]["text"]))
		original_pic.append(jarray[i]["original_pic"])
		created_at.append(jarray[i]["created_at"])
		post_id.append(jarray[i]["idstr"])
		total_reposts_count.append(jarray[i]["reposts_count"])

##########################################
## REPARSE SOME DATA
##########################################

for i in xrange(len(post_id)):
	#convert time into unix timestamp
	created_at[i] =  parser.parse(created_at[i]).strftime('%s')


##########################################
## STORE IN DATABASE
##########################################

print "Storing statuses in db..."

# store in db.
# we're looking for new posts only
for i in xrange(len(post_id)):

	#only put in as many as we need.
	if(newpostcount >= num_trackmore):
		break

  	#if you can't find the post already in Mongo, put it in:
	existing_post = collection_checklog.find_one({'post_id':post_id[i]})

	if (existing_post == None):
		newpostcount += 1
		imgpath = weibomodule.imgdir + str(post_id[i])+ splitext(original_pic[i])[1]
		urlretrieve(original_pic[i], imgpath)
		collection_postids_live.insert({'post_id':post_id[i]})
		doc = {
		  "post_id": post_id[i],
		  "user_id":user_id[i],
		  "checked_at": nowtimestamp,
		  "user_name": screen_name[i],
		  "user_follower_count": followers_count[i],
		  "post_original_pic":original_pic[i], 
		  "post_created_at": created_at[i], 
		  "post_repost_count": total_reposts_count[i],
		  "post_text": text[i]
		}
		collection_checklog.insert(doc)
		print "Storing postID " + str(post_id[i])
	else:
		print "post " + str(post_id[i]) + " already exists"

"""
for i in xrange (len(screen_name)):
	print jarray[i]
	print '\n'
	print 'Post_id: ' + post_id[i]  
	print 'WeiboID: '+ screen_name[i]
	print 'UserID: ' +   str(user_id[i])
	print 'Followers: '+ str(followers_count[i])
	print 'Original Pic: ' + original_pic[i]
	print 'Created_at: '+ created_at[i]
	print 'Total Reposts: ' + str(total_reposts_count[i])
	print 'Post: '+ text[i]
	print '\n'
"""

print str(newpostcount) + " posts added, for a total of " + str(num_live_posts + newpostcount) + " posts"


def main():
	print "hello"

if __name__ == "__main__":
    main()
