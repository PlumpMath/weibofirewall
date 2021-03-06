import MySQLdb
import requests
import json
import sys
from datetime import datetime
from dateutil import tz
from dateutil import parser
import weibo_settings
import weibo_accesstokens
import hashlib
# accesstokens are at  weibo_accesstokens.accesstokens

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
## GLOBAL VARIABLES 
##########################################

db = None
thistoken = None

##########################################
## DB connection
##########################################

def open_db():
	global db
	if not db:
		db = MySQLdb.connect(weibo_settings.dbhost, weibo_settings.dbuser, weibo_settings.dbpass, weibo_settings.dbname, charset='utf8')
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
	if (weibo_settings.track_posts_override != -1):
		return weibo_settings.track_posts_override

	numtokens = len(weibo_accesstokens.accesstokens)
	return int(numtokens * weibo_settings.tracking_period * weibo_settings.queries_per_token)

# if we're on manual, this alerts everyone if w'ere tracking too many to count
def post_alert():
	numtokens = len(weibo_accesstokens.accesstokens)
	num_can_track =  numtokens * weibo_settings.tracking_period * weibo_settings.queries_per_token

	if (weibo_settings.track_posts_override >= num_can_track):
		return "WARNING - you can only track " + str(num_can_track) + ", yet you're trying to track " + str(weibo_settings.track_posts_override)

	return "You can track " + str(num_can_track) + " posts"

#get a new token- starting from the first token and working its way to the end
def getnewtoken():
	global thistoken
	numtokens = len(weibo_accesstokens.accesstokens)

	thistokenindex = -1 


	#print "Let's get a new token. currently using" , thistoken
	print "Getting new token.."

	#if token doesn't exist, get the first token
	if (thistoken == None):	
		thistoken = weibo_accesstokens.accesstokens[0]
	else:
		# try to get the next token, making sure that we're not at the end
		thistokenindex = weibo_accesstokens.accesstokens.index(thistoken)
		if (thistokenindex + 1 >= numtokens):
			#error on our hands - we've reached the last token!
			thistoken = -1
			print "OUT OF TOKENS"
			sys.exit()
		else:
			#get the next token
			thistoken = weibo_accesstokens.accesstokens[thistokenindex + 1]
#			print "got the next token"

	thistokenindex += 1
	print "Access Token #" , (thistokenindex + 1) , "/" , len(weibo_accesstokens.accesstokens) , " being used: " + thistoken
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
	thistoken = gettoken()

	# should be a while loop, but just doing this so we don't get caught in an infinite loop
	for i in xrange(len(weibo_accesstokens.accesstokens)):

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
			print "* error = " , jsondata["error"]
			print "* error_code = " , jsondata["error_code"]
			#see for error codes: http://open.weibo.com/wiki/Error_code
			if(jsondata["error_code"] == 10022 or jsondata["error_code"] == 10023 or jsondata["error_code"] == 10024):
				print "* Hitting rate limit!"
				#we're hitting a rate limit!
				thistoken = getnewtoken()
			else:
				#oh wait, an interesting error - maybe post has been deleted
				return jsondata
		else:
			#got a successful response
			return jsondata


	print "OUT OF TOKENS"	
	sys.exit()
	return -1

#get status of friends
#usually call this without a parameter, since the max is 100, and this query only costs us 1 out of the 150 per hour query.
def accessfriends(count=100, page=1):
	jsondata = requests_get_wrapper(weibo_settings.apiurl_accessfriends, params={"access_token": "TOKEN", "count": count, "page": page})
	return jsondata


# check each status
def checkstatus(post_id):
	jsondata = requests_get_wrapper(weibo_settings.apiurl_checkstatus, params={"access_token": "TOKEN", "id": post_id})
	#print jsondata
	return jsondata

# refresh post (basically, a better checkstatus)
# returns skeletal post upon error
# consisting of post id, is_deleted, error message, error code, checekd_at, and then put it in checklog.
# otherwise returns formatted schema format in dict
def refreshpost(this_post_id):
	jsondata = requests_get_wrapper(weibo_settings.apiurl_checkstatus, params={"access_token": "TOKEN", "id": this_post_id})


	this_post_old = get_oldest_post(this_post_id)

	#okay, so we get post data
	#if it has an error (which means that it's been deleted), then  assemble skeeletal 

	if "error_code" in jsondata:

		thispost = {
			"post_id":	this_post_id,
#			"user_id":	jsondata["user"]["id"],
#			"user_name":	jsondata["user"]["screen_name"],
#			"user_follower_count":	jsondata["user"]["followers_count"],
#			"post_original_pic":	jsondata["original_pic"],
#			"post_created_at":	createddatetime,
#			"post_repost_count":	jsondata["reposts_count"],
#			"post_text":	unicode(jsondata["text"]),
			"started_tracking_at": this_post_old["started_tracking_at"],
			"is_deleted": 1,
#			"is_retired": 0,
			"error_message": jsondata["error"],
			"error_code": jsondata["error_code"],
	#		"checked_at":
		}

		return thispost

	else:

		createddatetime = parser.parse(jsondata["created_at"]).strftime('%Y-%m-%d %H:%M:%S')
		#otherwise format it ccording to our schema


		thispost = {
			"post_id":	this_post_id,
			"user_id":	jsondata["user"]["id"],
			"user_name":	jsondata["user"]["screen_name"],
			"user_follower_count":	jsondata["user"]["followers_count"],
			"post_original_pic":	jsondata["original_pic"],
			"post_created_at":	createddatetime,
			"post_repost_count":	jsondata["reposts_count"],
			"post_text":	unicode(jsondata["text"]),
			"started_tracking_at": this_post_old["started_tracking_at"],
			"is_deleted": 0,
			"is_retired": 0,
#			"error_message": "",
#			"error_code": "",
	#		"checked_at":
		}

	return thispost



# find all postids!
def get_all_postids():

	db = open_db()
	cursor = db.cursor()

	query = 'SELECT DISTINCT post_id FROM %s' % (weibo_settings.checklog_tablename)
	cursor.execute(query)
	allpostids = cursor.fetchall()
	allpostids = map(lambda x: x[0], allpostids)
	
	return allpostids


# find posts that we're tracking
def get_tracking_postids():

	#query is: "of all posts that have "is_deleted" = 0 and "is_retired" = 0, find unique ids, sort descended by checked timestamp

	#BUT REALLY - we want all the posts that never have either of the two flags.
	
	#SO we can achieve this by 1) getting all the post ids 2) getting all the post ids that are flagged 3) getting set 1 - set 2
	db = open_db()
	cursor = db.cursor()

	query = 'SELECT DISTINCT post_id FROM %s' % (weibo_settings.checklog_tablename)
	cursor.execute(query)
	allpostids = cursor.fetchall()
	allpostids = map(lambda x: x[0], allpostids)
	
	query = 'SELECT DISTINCT post_id FROM %s WHERE is_deleted <> 0 OR is_retired <> 0' % (weibo_settings.checklog_tablename)
	cursor.execute(query)
	nottrackingpostids = cursor.fetchall()
	nottrackingpostids = map(lambda x: x[0], nottrackingpostids)


	trackingpostids = list(set(allpostids) - set(nottrackingpostids))

	return trackingpostids



# find posts that have been deleted
def get_deleted_postids(error_code=-1, exclude_error_code=False):

	db = open_db()
	cursor = db.cursor()

	if error_code == -1:
		query = 'SELECT DISTINCT post_id FROM %s WHERE is_deleted <> 0' % (weibo_settings.checklog_tablename)
	else:
		if exclude_error_code == False:
			query = 'SELECT DISTINCT post_id FROM %s WHERE is_deleted <> 0 AND error_code = %s' % (weibo_settings.checklog_tablename, error_code)
		else:
			query = 'SELECT DISTINCT post_id FROM %s WHERE is_deleted <> 0 AND error_code <> %s' % (weibo_settings.checklog_tablename, error_code)

	cursor.execute(query)
	deletedpostids = cursor.fetchall()
	deletedpostids = map(lambda x: x[0], deletedpostids)

	return deletedpostids



# find posts that have been retired
def get_retired_postids():

	db = open_db()
	cursor = db.cursor()

	query = 'SELECT DISTINCT post_id FROM %s WHERE is_retired <> 0' % (weibo_settings.checklog_tablename)
	cursor.execute(query)
	retiredpostids = cursor.fetchall()
	retiredpostids = map(lambda x: x[0], retiredpostids)

	return retiredpostids


# Does a post exist in the checklog, no matter its status"
def postexists(post_id):
	query = "SELECT COUNT(*) FROM %s WHERE post_id = %s" %(weibo_settings.checklog_tablename, post_id)
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
def get_most_recent_live_post(post_id):

	query = "SELECT * FROM %s WHERE post_id = %s AND post_repost_count IS NOT NULL ORDER BY checked_at DESC LIMIT 1" %(weibo_settings.checklog_tablename, post_id)

	db = open_db()
	cursor = db.cursor()
	cursor.execute(query)
	
	#get keys for dictionary
	cols = [d[0] for d in cursor.description]

	result = cursor.fetchall()

	#formulate into dictionary
	thispost = dict(zip(cols, result[0]))

	return thispost
	


#given a post id, get its most recent post
def get_oldest_post(post_id):

	query = "SELECT * FROM %s WHERE post_id = %s ORDER BY checked_at ASC LIMIT 1" %(weibo_settings.checklog_tablename, post_id)

	db = open_db()
	cursor = db.cursor()
	cursor.execute(query)
	
	#get keys for dictionary
	cols = [d[0] for d in cursor.description]

	result = cursor.fetchall()

	#formulate into dictionary
	thispost = dict(zip(cols, result[0]))

	return thispost
	


#given a post id, get its deletion post
#take error code if desired
def get_deletion_post(post_id, error_code=-1):

	if error_code == -1:
		query = "SELECT * FROM %s WHERE post_id = %s AND is_deleted <> 0 ORDER BY checked_at DESC LIMIT 1" %(weibo_settings.checklog_tablename, post_id)
	else:
		query = "SELECT * FROM %s WHERE post_id = %s AND is_deleted <> 0 AND error_code = %s ORDER BY checked_at DESC LIMIT 1" %(weibo_settings.checklog_tablename, post_id, error_code)


	db = open_db()
	cursor = db.cursor()
	cursor.execute(query)
	
	#get keys for dictionary
	cols = [d[0] for d in cursor.description]

	result = cursor.fetchall()

	if result == ():
		return -1


	#formulate into dictionary
	thispost = dict(zip(cols, result[0]))

	return thispost


	# EVERYTHING IS ON CHINA TIME, YOU UNDERSTAND
def get_current_chinatime():
	utcnow =  datetime.utcnow()
	from_zone=tz.tzutc()
	to_zone = tz.gettz(weibo_settings.to_timezome_name)
	utcnow = utcnow.replace(tzinfo=from_zone)
	chinanow =  utcnow.astimezone(to_zone)
	return chinanow
	#nowdatetime = chinanow.strftime('%Y-%m-%d %H:%M:%S')
	#return nowdatetime


def set_timezone_to_china(thisdatetime):
#	print "* thisdatetime = ", thisdatetime
	to_zone = tz.gettz(weibo_settings.to_timezome_name)
	thisdatetime =  thisdatetime.replace(tzinfo=to_zone)
	return thisdatetime


# check then the most recent checktime was
def get_most_recent_checktime():
	db = open_db()
	db.commit()

	query = "SELECT checked_at FROM %s ORDER BY checked_at DESC LIMIT 1" %(weibo_settings.checklog_tablename)

	cursor = db.cursor()
	cursor.execute(query)

	#get the data
	result = cursor.fetchone()

	if(result == None):
		return -1

	chinatime =  result[0]

	#set timezone to china
	to_zone = tz.gettz(weibo_settings.to_timezome_name)
	chinatime=  chinatime.replace(tzinfo=to_zone)

	#print chinatime

	return chinatime

def total_seconds(td):
	#because python 2.6 doesn't have totalseconds
	return td.seconds + td.days * 24 * 3600

def merge_deleted_from_new_old(this_post_id):

	this_post_new = get_most_recent_live_post(this_post_id)
	this_post_old = get_oldest_post(this_post_id)
	this_post_deleted = get_deletion_post(this_post_id)
	#the only items that change between the two is the "initial" items

	thispost_last_check = set_timezone_to_china(this_post_new['checked_at'])
	thispost_created_at = set_timezone_to_china(this_post_old['post_created_at'])
	thispost_lifespan = thispost_last_check - thispost_created_at
	thispost_lifespan = total_seconds(thispost_lifespan)

	this_post = this_post_old
	this_post["user_follower_count_initial"] = str(this_post_old["user_follower_count"])
	this_post["user_follower_count"] = str(this_post_new["user_follower_count"])
	this_post["post_repost_count_initial"] = str(this_post_old["post_repost_count"])
	this_post["post_repost_count"] = str(this_post_new["post_repost_count"])
	this_post["started_tracking_at_epoch"] = this_post_old["started_tracking_at"].strftime('%s')
	this_post["started_tracking_at"] = this_post_old["started_tracking_at"].strftime('%Y-%m-%d %H:%M:%S')
	if(this_post_deleted != -1):
		this_post["error_code"] = this_post_deleted["error_code"] 
		this_post["error_message"] = this_post_deleted["error_message"] 
		this_post["is_deleted"] = this_post_deleted["is_deleted"] 
	else:
		this_post["error_code"] = ""
		this_post["error_message"] = ""
		this_post["is_deleted"] = 0
	# we're setting the "deleted time" to be when it was found to be deleted
	# that means that, depending on the interval T, 
	# the actual deletion time is always between 0 and T later
	this_post["last_checked_at_epoch"] = this_post_new["checked_at"].strftime('%s')
	this_post["last_checked_at"] = this_post_new["checked_at"].strftime('%Y-%m-%d %H:%M:%S')
	this_post["post_created_at_epoch"] = this_post_new["post_created_at"].strftime('%s')
	this_post["post_created_at"] = this_post_new["post_created_at"].strftime('%Y-%m-%d %H:%M:%S')
	this_post["post_lifespan"] = thispost_lifespan

	return this_post


def get_all_posts(post_id):
	query = "SELECT * FROM %s WHERE post_id = %s GROUP BY checked_at ASC" %(weibo_settings.checklog_tablename, post_id)

	db = open_db()
	cursor = db.cursor()
	cursor.execute(query)
	
	result = cursor.fetchall()

	#print "RESULT " , result
	#print "RESULTLEN " , len(result)
	
	if result == ():
		return -1

	#get keys for dictionary
	cols = [d[0] for d in cursor.description]

	dictlist = []
	for thisresult in result:
		#formulate into dictionary
		thisdict = dict(zip(cols, thisresult))
		dictlist.append(thisdict)

	return dictlist



def get_csv_header():
	csv_header = 'post_id,user_id,user_name,user_follower_count_initial,user_follower_count,post_original_pic,post_created_at,post_created_at_epoch,post_repost_count_initial,post_repost_count,post_text,started_tracking_at,started_tracking_at_epoch,is_deleted,is_retired,error_message,error_code,last_checked_at,last_checked_at_epoch,post_lifespan,post_repostlog'
	csv_header_unicode = csv_header.replace(',', weibo_settings.delim)
	return csv_header_unicode


def make_csvline_from_post(this_post):
#	print "THISPOST" , this_post

	csvline = this_post["post_id"] , this_post["user_id"] , this_post["user_name"] , this_post["user_follower_count_initial"] , this_post["user_follower_count"] , this_post["post_original_pic"] , this_post["post_created_at"] , this_post["post_created_at_epoch"] ,this_post["post_repost_count_initial"] , this_post["post_repost_count"] , this_post["post_text"] , this_post["started_tracking_at"] , this_post["started_tracking_at_epoch"] , this_post["is_deleted"] , this_post["is_retired"] , this_post["error_message"] , this_post["error_code"] , this_post["last_checked_at"] , this_post["last_checked_at_epoch"] , this_post["post_lifespan"]
#	print "wmodule csvline= " , csvline
	return csvline


def make_jsonlist_from_post(this_post):
#	print "THISPOST" , this_post

	thislist = { "post_id": this_post["post_id"],
		"user_id": this_post["user_id"],
		"user_name": this_post["user_name"],
		"user_follower_count_initial": this_post["user_follower_count_initial"],
		"user_follower_count": this_post["user_follower_count"],
		"post_original_pic": this_post["post_original_pic"],
		"post_created_at": this_post["post_created_at"],
		"post_created_at_epoch": this_post["post_created_at_epoch"],
		"post_repost_count_initial": this_post["post_repost_count_initial"],
		"post_repost_count": int(this_post["post_repost_count"]),
		"post_text": this_post["post_text"],
		"started_tracking_at": this_post["started_tracking_at"],
		"started_tracking_at_epoch": this_post["started_tracking_at_epoch"],
		"is_deleted": this_post["is_deleted"],
		"is_retired": this_post["is_retired"],
		"error_message": this_post["error_message"],
		"error_code": this_post["error_code"],
		"last_checked_at": this_post["last_checked_at"],
		"last_checked_at_epoch": this_post["last_checked_at_epoch"],
		"post_lifespan": this_post["post_lifespan"] }
	return thislist


## HASHES user_id and post_id
def obfuscate_hashmod(data, salt, modnum=10000):
	return str(int(hashlib.sha512(data + salt).hexdigest(), 16) % modnum)

## obfuscates username
def obfuscate_username(data, salt):
#	thishash = obfuscate_hashmod(data, salt, 10000)
	return "ANON"


