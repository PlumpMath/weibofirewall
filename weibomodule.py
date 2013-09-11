import MySQLdb
import requests
import json

##########################################
## CONSTANTS
##########################################

dbname = "jumpingthegreatfirewall"
dbhost = "localhost"
dbuser = "weibofirewall"
dbpass = "w3ibofirewall"

## ALRIGHT NEW SETUP
## THERE IS ONE COLLECTION
## THIS KEEPS THE DBS SIMPLE. ALL OTHER PROCESSING IS DONE THROUGH CODE

checklog_tablename = "checklog"

#accesstokens = ['2.00Ga5TmDFObaNC7aeeff1e5cZR1oTD']
accesstokens = ['2.00Ga5TmDFObaNC7aeeff1e5cZR1oTD', '2.00YJl5fDtbWV2B908f7d5e64BIPIwC','2.00Ga5TmDGX4hRE1447f826bclbRQJC','2.00Ga5TmD0Ugujs972d9aab4724Dt4D']

apiurl_accessfriends = "https://api.weibo.com/2/statuses/friends_timeline.json"
apiurl_checkstatus = "https://api.weibo.com/2/statuses/show.json"

imgdir = "/home/provolot/www/SIDL/firewall/weibo_images/" #with trailing slash

queries_per_token = 100 #hardcoded - set this to 100 to give us some padding

pagemax = 10 # let's not go more than 10 pages back while looking for anything

#display_timezone = "Asia/Shanghai"
display_timezone = "America/New_York"

"""
the WEIBO API KEY only takes 150 REQUESTS PER HOUR. 
So our limiting factor is the check time. 
At a checking resolution of 1 hr (each post is checked once every hour),
only 150 posts can be tracked per api token.
At a checking resolution of 30 min, only 75 posts can be tracked per api token.
At a checking resolution of X hours, only 150 * X posts can be tracked per api token.

HOWEVER the code gets a little complex if X > 1. if X = 10, for example, then checking 1500 posts would still be staggered over 10 hours, requiring each post to be inserted into a 'queue' to check, etc. For the sake of simplicity, then, X <= 1.
"""

# period of tracking, unit: hours. 
# ex) 0.5 = track each post every 30 minutes
tracking_period = 0.25 

# default: set to -1 to determine tracking posts based on period, set to number to specificy number of posts to track
# mostly for debugging purposes
# ex) 5 = track only 5 posts at a time
track_posts_override = -1 

#timeout - if a post is alive past this many seconds, then go onto the next
track_posts_timeout = 259200 #72 hours


##########################################
## VARIABLES AND CALCULATIONS
##########################################

db = None
thistoken = None

#period, in seconds
tracking_period_seconds = tracking_period * 3600

##########################################
## DB connection
##########################################

def open_db():
	global db
	if not db:
		db = MySQLdb.connect(dbhost, dbuser, dbpass, dbname)
	return db

"""
def get_db_collection(collection_name):
	global db
	if not db:
		open_connection()
	collection = db[collection_name]
	return collection 
	"""

def db_cursor():
	global db
	if not db:
		open_db()
	cursor = db.cursor()
	return cursor

def close_db():
	db.close()

##########################################
## PROCESSES
##########################################

#just converts seconds to minutes and seconds
def minsec(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return "%d:%02d:%02d" % (h, m, s)

# returns the number of posts to track
def num_posts_to_track():
	if (track_posts_override != -1):
		return track_posts_override

	numtokens = len(accesstokens)
	return numtokens * tracking_period * queries_per_token

# if we're on manual, this alerts everyone if w'ere tracking too many to count
def post_alert():
	numtokens = len(accesstokens)
	num_can_track =  numtokens * tracking_period * queries_per_token

	if (track_posts_override >= num_can_track):
		return "WARNING - you can only track " + str(num_can_track) + ", yet you're trying to track " + str(track_posts_override)

	return ""

#get a new token- starting from the first token and working its way to the end
def getnewtoken():
	global thistoken
	global accesstokens
	numtokens = len(accesstokens)

	#if token doesn't exist, get the first token
	if (thistoken == None):	
		thistoken = accesstokens[0]
	else:
		# try to get the next token, making sure that we're not at the end
		thistokenindex = accesstokens.index(thistoken)
		if (thistokenindex + 1 >= numtokens):
			#error on our hands - we've reached the last token!
			thistoken = -1
		else:
			#get the next token
			thistoken = accesstokens[thistokenindex + 1]

	thistokenindex = accesstokens.index(thistoken)
	print "Access Token #" , (thistokenindex + 1) , " being used: " + thistoken
	return thistoken

#checks and gets a working access token.
def gettoken():
	global thistoken
	if (thistoken == None):
		thistoken = getnewtoken()
	return thistoken

# wrapper for requests.get
# launches a request. if api is out, switches to the next token. sends -1 if all tokens have been used.
def requests_get_wrapper(url, params):
	global thistoken
	global accesstokens
	thistoken = gettoken()

	# should be a while loop, but just doing this so we don't get caught in an infinite loop
	for i in xrange(len(accesstokens)):

		#replace param with our token
		params["access_token"] = thistoken

		#attempt to get request	
	
		#print "data = requests.get(" + url + ", params=" 
		#print params
		data = requests.get(url, params=params)
		#print data.text

		jsondata = data.json()

		#print jsondata	
		try:
			# if we get an error
			if jsondata["error"] == "User requests out of rate limit!":

				# failure! try another token
				thistoken = getnewtoken()

				#if we ran out of tokens!
				if (thistoken == -1):
					return -1

				#loop and try again
			else:
				return jsondata

		except:
			# success - exit out
			return jsondata
		else:
			#oh, we actually have another error
			#print jsondata["error"]
			#return jsondata
			# loop around
			pass

		

#get status of friends
#usually call this without a parameter, since the max is 100, and this query only costs us 1 out of the 150 per hour query.
def accessfriends(count=100, page=1):
	jsondata = requests_get_wrapper(apiurl_accessfriends, params={"access_token": "TOKEN", "count": count, "page": page})
	return jsondata


# check each status
def checkstatus(post_id):
	jsondata = requests_get_wrapper(apiurl_checkstatus, params={"access_token": "TOKEN", "id": post_id})
	return jsondata

# find current posts only
def getcurrentpostids():
	db = open_db()

	#query is: "of all posts that have "is_deleted" = 0 and "is_retired" = 0, find unique ids, sort descended by checked timestamp

	cursor = db.cursor()

	currentpostids = cursor.execute("SELECT DISTINCT post_id FROM " + checklog_tablename + " WHERE is_deleted = 0")

	return currentpostids


