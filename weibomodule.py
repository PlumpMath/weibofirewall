import MySQLdb
import requests
import json
import sys
from datetime import datetime
from dateutil import tz
from dateutil import parser

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

to_timezome_name = 'Asia/Shanghai'
display_timezone = "Asia/Shanghai"

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
		db = MySQLdb.connect(dbhost, dbuser, dbpass, dbname, charset='utf8')
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
	return int(numtokens * tracking_period * queries_per_token)

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


		#print "trying to get token" , i , "token is " , thistoken
		#attempt to get request	
	
		#print "data = requests.get(" + url + ", params=" 
		#print params
		data = requests.get(url, params=params)
		#print data.text

		jsondata = data.json()

	#	print jsondata

		if "error" in jsondata:
			# failure! try another token
			thistoken = getnewtoken()
		else:
			print "got working token"
			return jsondata


	print "OUT OF TOKENS"	
	sys.exit()
	return -1

#get status of friends
#usually call this without a parameter, since the max is 100, and this query only costs us 1 out of the 150 per hour query.
def accessfriends(count=100, page=1):
	jsondata = requests_get_wrapper(apiurl_accessfriends, params={"access_token": "TOKEN", "count": count, "page": page})
	return jsondata


# check each status
def checkstatus(post_id):
	jsondata = requests_get_wrapper(apiurl_checkstatus, params={"access_token": "TOKEN", "id": post_id})
	#print jsondata
	return jsondata

# refresh post (basically, a better checkstatus)
def refreshpost(post_id):
	jsondata = requests_get_wrapper(apiurl_checkstatus, params={"access_token": "TOKEN", "id": post_id})

	createddatetime = parser.parse(jsondata["created_at"]).strftime('%Y-%m-%d %H:%M:%S')

	thispost = {
		"post_id":	jsondata["idstr"],
		"user_id":	jsondata["user"]["id"],
		"user_name":	jsondata["user"]["screen_name"],
		"user_follower_count":	jsondata["user"]["followers_count"],
		"post_original_pic":	jsondata["original_pic"],
		"post_created_at":	createddatetime,
		"post_repost_count":	jsondata["reposts_count"],
		"post_text":	unicode(jsondata["text"]),
#		"started_tracking_at": nowdatetime,
		"is_deleted": 0,
		"is_retired": 0,
		"error_message": "",
		"error_code": "",
#		"checked_at":
	}

	return thispost



# find posts that we're tracking
def get_tracking_postids():

	#query is: "of all posts that have "is_deleted" = 0 and "is_retired" = 0, find unique ids, sort descended by checked timestamp

	#BUT REALLY - we want all the posts that never have either of the two flags.
	
	#SO we can achieve this by 1) getting all the post ids 2) getting all the post ids that are flagged 3) getting set 1 - set 2
	db = open_db()
	cursor = db.cursor()

	query = 'SELECT DISTINCT post_id FROM %s' % (checklog_tablename)
	cursor.execute(query)
	allpostids = cursor.fetchall()
	allpostids = map(lambda x: x[0], allpostids)
	
	query = 'SELECT DISTINCT post_id FROM %s WHERE is_deleted <> 0 OR is_retired <> 0' % (checklog_tablename)
	cursor.execute(query)
	nottrackingpostids = cursor.fetchall()
	nottrackingpostids = map(lambda x: x[0], nottrackingpostids)


	trackingpostids = list(set(allpostids) - set(nottrackingpostids))

	return trackingpostids


# Does a post exist in the checklog, no matter its status"
def postexists(post_id):
	query = "SELECT COUNT(*) FROM %s WHERE post_id = %s" %(checklog_tablename, post_id)
	db = open_db()
	cursor = db.cursor()
	cursor.execute(query)
	result = cursor.fetchone()
	num_existing_posts = result[0]
	#close_db()

	return num_existing_posts != 0


def checklog_insert(thispost):
	#print thispost


	columns = ', '.join(thispost.keys())
	parameters = ', '.join(['%({0})s'.format(k) for k in thispost.keys()])

	#sqlinsert = "INSERT into checklog ('user_id', 'user_name', 'user_follower_count', 'post_original_pic', 'post_created_at', 'post_repost_count', 'post_text', 'started_tracking_at', 'is_deleted', 'is_retired', 'error_message', 'error_code', 'checked_at') VALUES (%(user_id)s, %(user_name)s, %(user_follower_count)s, %(post_original_pic)s, %(post_created_at)s, %(post_repost_count)s, %(post_text)s, %(started_tracking_at)s, %(is_deleted)s, %(is_retired)s, %(error_message)s, %(error_code)s, %(checked_at)s)" 

	query = 'INSERT INTO checklog ({columns}) VALUES ({parameters})'.format(columns=columns, parameters=parameters)

	#print query

	#close_db()
	db = open_db()
	cursor = db.cursor()
	cursor.execute(query, thispost)
	db.commit()
	#close_db()



#given a post id, get its most recent post
def get_mostrecent_post(post_id):

	query = "SELECT * FROM %s WHERE post_id = %s ORDER BY 'checked_at' DESC LIMIT 1" %(checklog_tablename, post_id)

	db = open_db()
	cursor = db.cursor()
	cursor.execute(query)
	
	cols = [d[0] for d in cursor.description]

	result = cursor.fetchall()

	thispost = dict(zip(cols, result[0]))

	#print "HEYHEY"
	#print thispost["post_text"].encode("ascii", "xmlcharrefreplace")

	#print thispost
	return thispost
	

# EVERYTHING IS ON CHINA TIME, YOU UNDERSTAND
def get_current_chinatime():
	utcnow =  datetime.utcnow()
	from_zone=tz.tzutc()
	to_zone = tz.gettz(to_timezome_name)
	utcnow = utcnow.replace(tzinfo=from_zone)
	chinanow =  utcnow.astimezone(to_zone)
	return chinanow
	#nowdatetime = chinanow.strftime('%Y-%m-%d %H:%M:%S')
	#return nowdatetime


def get_most_recent_check():
	db = open_db()
	db.commit()

	query = "SELECT checked_at FROM %s ORDER BY checked_at DESC LIMIT 1" %(checklog_tablename)

	cursor = db.cursor()
	cursor.execute(query)

	#get the data
	result = cursor.fetchone()
	chinatime =  result[0]

	#set timezone to china
	to_zone = tz.gettz(to_timezome_name)
	chinatime=  chinatime.replace(tzinfo=to_zone)

	print chinatime

	return chinatime

def makedateaware(thisdate):
	to_zone = tz.gettz(to_timezome_name)
	thisdate = thisdate.replace(tzinfo=to_zone)
	return thisdate

