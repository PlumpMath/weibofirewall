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

num_live_posts = collection_postids_live.count()
if (num_live_posts == 0):
	sys.exit("No posts are being tracked right now.")
print "Currently tracking " + str(num_live_posts) + " posts"
print weibomodule.post_alert()

##########################################
## GET LIST OF LIVE POSTS
##########################################

live_post_ids = []
for lpis in collection_postids_live.find():
	live_post_ids.append(lpis["post_id"])

print live_post_ids

##########################################
## HAS ENOUGH TIME PASSED?
##########################################


# get current time
nowtimestamp = int(time.time())
timelapsed = -1

most_recent_check = collection_checked_at_times.find_one({}, {'checked_at': -1})

# when was the last time we checked
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



print live_post_ids

"""
# just log once the checked at time so we know when the last successful check was
if (logged_checked_at == False):
logged_checked_at = True
collection_checked_at_times.insert({'checked_at':nowtimestamp})
"""

"""
for d in db.v2_sample_weibo.find()[startcount:endcount]:
  # Currently searching for this post:
  post_id_search = d['post_id']
  current_post_in_db = db.v2_sample_weibo.find({'post_id':d['post_id']})[0]

  # print str(token_loop_count) + " " + access_tokens[token_loop_count]
  url_temp="https://api.weibo.com/2/statuses/show.json?id=" + post_id_search + "&access_token=" + access_tokens[token_loop_count]
  print url_temp

  # Loop through the three access tokens
  if token_loop_count == 2:
    token_loop_count = 0
  else:
    token_loop_count += 1

  api_data = urlopen(url_temp).read()
  api_response = loads(api_data)

  # The post has been deleted
  if "error" in api_response:
    print 'DELETED ' + api_response['error'] 
    deleted_image_url = current_post_in_db['original_pic']
    deleted_by = strftime("%A %b %d %H:%M:%S +0000", gmtime())
    
    deldoc = {
      "user_id":current_post_in_db['user_id'],
      "check_url":url_temp,
      "deleted_image_url":deleted_image_url, 
      "delpost_id":d['post_id'], 
      "deleted_by":deleted_by,
      "text": current_post_in_db['text'],
      "screen_name": current_post_in_db['screen_name'],
      "created_at": current_post_in_db['created_at'],
      "followers_count": current_post_in_db['followers_count'],
      "total_reposts_count": current_post_in_db['total_reposts_count'],
      "error_message": api_response['error'],
      "error_code": api_response['error_code']
    }
    db['v2_deleted_weibo'].insert(deldoc)
    db['v2_sample_weibo'].remove({'post_id':d['post_id']})

  # If the post isn't deleted, update the data
  else: 
    updated_time = strftime("%A %b %d %H:%M:%S +0000", gmtime())

    print "Prev: " + str(current_post_in_db['total_reposts_count']) + " | " + "New: " + str(api_response['reposts_count'])
    db.v2_sample_weibo.update(current_post_in_db, {
      "$set": {
        "total_reposts_count": api_response['reposts_count'],
        "updated_time": updated_time
      }
    })

"""

print "done"
