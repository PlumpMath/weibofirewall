from urllib import urlopen
from urllib import urlretrieve
from json import loads
from time import gmtime, strftime
#from IPython.core.display import Image

screen_name=[]
followers_count=[]
text = []
original_pic = []
created_at = []
post_id = []
user_id = []
total_reposts_count = []

# Grab 100 posts every six minutes to get 1000 per hour
url="https://api.weibo.com/2/statuses/friends_timeline.json?access_token=2.00Ga5TmDFObaNC7aeeff1e5cZR1oTD&count=100"
data = urlopen(url).read()
# data
response = loads(data)

# type(response["statuses"])
jarray = response["statuses"]

for i in range(len(jarray)):
  # If this is a retweet and the original Weibo has an image, get the original
  if "retweeted_status" in jarray[i] and "original_pic" in jarray[i]["retweeted_status"]:
    screen_name.append(jarray[i]["retweeted_status"]["user"]["screen_name"])
    user_id.append(jarray[i]["retweeted_status"]["user"]["id"])
    followers_count.append(jarray[i]["retweeted_status"]["user"]["followers_count"])
    text.append(jarray[i]["retweeted_status"]["text"])
    original_pic.append(jarray[i]["retweeted_status"]["original_pic"])
    created_at.append(jarray[i]["retweeted_status"]["created_at"])
    post_id.append(jarray[i]["retweeted_status"]["idstr"])
    total_reposts_count.append(jarray[i]["retweeted_status"]["reposts_count"])

  # If this is an original Weibo, no retweets and it has an image
  elif "original_pic" in jarray[i]:
    screen_name.append(jarray[i]["user"]["screen_name"])
    user_id.append(jarray[i]["user"]["id"])
    followers_count.append(jarray[i]["user"]["followers_count"])
    text.append(jarray[i]["text"])
    original_pic.append(jarray[i]["original_pic"])
    created_at.append(jarray[i]["created_at"])
    post_id.append(jarray[i]["idstr"])
    total_reposts_count.append(jarray[i]["reposts_count"])

import pymongo
conn = pymongo.Connection()

db = conn['wb']
collection = db['v2_sample_weibo']

# save all posts with images in mongo
for i in range(len(post_id)):
  hnh = db.v2_sample_weibo.find_one({'post_id':str(post_id[i])})

  # print hnh == None
  # If you can't find the post already in Mongo, put it in:
  if (hnh == None):
    doc = {
      "screen_name": screen_name[i],
      "user_id":user_id[i],
      "followers_count": followers_count[i],
      "text": text[i], 
      "original_pic":original_pic[i], 
      "created_at": created_at[i], 
      "post_id": post_id[i],
      "archive_id": post_id[i],
      "total_reposts_count": total_reposts_count[i]
    }
    collection.insert(doc)
    print "putting in Mongo " + str(post_id[i])
    urlretrieve(original_pic[i],'sample_img/'+str(post_id[i])+original_pic[i][-4:])

  # If the post is already in Mongo, update the data:
  else:
    print "updating mongo " + str(post_id[i])
    print "Prev: " + str(hnh["total_reposts_count"]) + " | " + "New: " + str(total_reposts_count[i])
    updated_time = strftime("%A %b %d %H:%M:%S +0000", gmtime())
    db.v2_sample_weibo.update(hnh, {
      "$set": {
        "total_reposts_count": total_reposts_count[i],
        "updated_time": updated_time
      }
    })

# for i in range (len(screen_name)):
#     print jarray[i]
#     print '\n'
#     print 'WeiboID: '+ screen_name[i]
#     print 'UserID: ' +   str(user_id[i])
#     print 'Followers: '+ str(followers_count[i])
#     print 'Post: '+ text[i]
#     # display(Image(url=original_pic[i]))
#     print 'Created_at: '+ created_at[i]
#     print 'Post_id: ' + post_id[i]  
#     print 'Original: ' + str(original_reposts_count[i])
#     print 'Current: ' + str(current_reposts_count[i])
#     print 'Total: ' + str(total_reposts_count[i])
#     print '\n'