from time import gmtime, strftime
from urllib import urlopen
from urllib import urlretrieve
from json import loads
from random import randint
import math
import pymongo
conn = pymongo.Connection()
db = conn['wb']

access_tokens = ['2.00YJl5fDtbWV2B908f7d5e64BIPIwC','2.00Ga5TmDGX4hRE1447f826bclbRQJC','2.00Ga5TmD0Ugujs972d9aab4724Dt4D']
token_loop_count = 0

interval_count = math.floor(db.v2_sample_weibo.count() / 440)
interval = randint(0, interval_count)

startcount = interval * 440
endcount = startcount + 440

if (endcount > db.v2_sample_weibo.count()):
    endcount = db.v2_sample_weibo.count()

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