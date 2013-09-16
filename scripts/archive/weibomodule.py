
##########################################
## CONSTANTS
##########################################

dbname = "weibo_firewall_db"

collection_postids_live = "postids_live"
collection_postids_dead = "postids_dead"

collection_checklog = "checklog"

accesskeys = ["2.00Ga5TmDFObaNC7aeeff1e5cZR1oTD"]

query_accessfriends = "https://api.weibo.com/2/statuses/friends_timeline.json?count=COUNT&access_token=ATOKEN"

imgdir = "/home/provolot/www/SIDL/firewall/weibo_images/" #with trailing slash

queries_per_key = 150 #hardcoded

##########################################
## SETTINGS
##########################################

#WEIBO API KEY only takes 150 REQUESTS PER HOUR. 
"""
So our limiting factor is the check time. 
At a checking resolution of 1 hr (each post is checked once every hour),
only 150 posts can be tracked per api key.
At a checking resolution of 30 min, only 75 posts can be tracked per api key.
At a checking resolution of X hours, only 150 * X posts can be tracked per api key.

HOWEVER the code gets a little complex if X > 1. if X = 10, for example, then checking 1500 posts would still be staggered over 10 hours, requiring each post to be inserted into a 'queue' to check, etc. For the sake of simplicity, then, X <= 1.
"""

# period of tracking, unit: hours. 
# ex) 0.5 = track each post every 30 minutes
tracking_period = 1.0 

# set to -1 for normal behavior, set to number to specificy number of posts to track
# mostly for debugging purposes
# ex) 5 = track only 5 posts at a time
track_posts_override = -1

# set to -1 for normal behavior, set to number to specificy number of posts to track
# mostly for debugging purposes
# ex) 5 = track only 5 posts at a time
posts_to_search track_posts_override = -1

##########################################
## PROCESSES
##########################################

# returns the number of posts to track
def num_posts_to_track():
	if (track_posts_override != -1):
		return track_posts_override

	numkeys = len(accesskeys)
	return numkeys * tracking_period * queries_per_key


#checks and gets a working access key.
def getkey():
	return accesskeys[0]

#adds a key to a query string
def addkey(query, replacename):
	return query.replace(replacename, getkey())

#get status of friends
#usually call this without a parameter, since the max is 100, and this query only costs us 1 out of the 150 per hour query.
def accessfriends(count=100):
	return addkey(query_accessfriends, "ATOKEN").replace("COUNT", str(count))



