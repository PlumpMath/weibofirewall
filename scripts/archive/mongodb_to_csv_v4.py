import pymongo
import csv
import json
import datetime
from dateutil.parser import parse
import requests
import logging
import re
import os

logging.basicConfig(filename='example.log',level=logging.DEBUG)


#ideal data format
#poster,path,filename,created_at,deleted_at

db_hostname = "ec2-107-21-88-135.compute-1.amazonaws.com"
db_username = "journalist"
db_userpass = "journalist"

#https://api.weibo.com/2/statuses/show.json?access_token=2.00YJl5fDtbWV2B908f7d5e64BIPIwC&id=3578217296405470
weibo_accesstoken = "2.00YJl5fDtbWV2B908f7d5e64BIPIwC"
weibo_postid_querystring = "https://api.weibo.com/2/statuses/show.json?access_token=" + weibo_accesstoken + "&id="

from pymongo import MongoClient
client = MongoClient(db_hostname, 27017)

#print client.database_names()

db = client.wb

#print db.collection_names()


sample_weibo = db.sample_weibo
deleted_weibo = db.deleted_weibo


def deleted_in_sample():
	docno = 0

	with open("deleted_in_sample.csv", "w") as wf:

		print "post_id, created_at, poster_id"
		wf.write("post_id, created_at, poster_id \n")

		for post in deleted_weibo.find():

			postid =  post['delpost_id'] 

			samplefind = sample_weibo.find( { 'post_id': postid })
	#		print samplefind.count()
			if(samplefind.count() != 0):
				#print "post = " + postid
				for doc in samplefind:
					docno += 1
					#print "this is the doc = " + str(docno)
					#print doc
					thiscreated = parse(doc['created_at']).strftime('%s')
					print postid + "," + thiscreated + "," , doc['id']
					wf.write(postid + "," + thiscreated + "," + str(doc['id']) + "\n")
			samplefind.rewind()

def csvize_sample():

	#Fri May 03 07:49:13 +0800 2013
	#%a %b %d %H:%M:%S %z %Y

	with open("sample_weibo.csv", "w") as wf:

		wf.write("post_id, created_at, poster_id \n")
		print "post_id, created_at, poster_id"
		for doc in sample_weibo.find().sort("created_at").limit(10):
			#print doc
			thiscreated = parse(doc['created_at']).strftime('%s')
			thisname = doc["screen_name"].encode("utf8")
			print doc["post_id"] + "," + thiscreated + "," , doc["id"]
			wf.write(doc["post_id"] + "," + thiscreated + "," + str(doc["id"]) + "\n")
			#print doc["followers_count"]
			#screen_name, post_id, created_at,deleted_at


def csvize_deleted():

	#Fri May 03 07:49:13 +0800 2013
	#%a %b %d %H:%M:%S %z %Y

	deleted_weibo_filename = "deleted_weibo.csv"
	deleted_weibo_temp = "deleted_weibo_temp.csv"

	### IF TEMP FILE HAS SOMETHING IN IT, MERGE WITH MASTER FILE
	if(os.stat(deleted_weibo_temp)[6] != 0):
		with open(deleted_weibo_temp, "r") as rf:
			tempcontent = rf.readlines()

		with open(deleted_weibo_filename, "a") as af:
			
			for eachline in tempcontent:
				if(re.match("post_id.*", eachline)):
					pass
					#is header
				else:
					af.write(eachline)
						


	### GET THE LAST POST WE SCANNED SO WE DON'T DUPLICATE SCAN
	lastpost_id = -1
	if(os.path.exists(deleted_weibo_filename)):
		
		lines= os.popen("tail -3 " + deleted_weibo_filename).readlines()
		for thisline in reversed(lines):
			if(thisline != "\n"):
				regresult = re.search("(\d*),",thisline)
				lastpost_id = regresult.groups()[0]
				print lastpost_id
				break

		if lastpost_id == -1:
			print "error reading previous file."
			return "yo"				

	## OPEN A TEMPORARY FILE

	with open(deleted_weibo_temp, "w") as wf:
		wf.write("post_id, created_at, poster_id \n")
		print "post_id, created_at, poster_id"

		maxcount =  deleted_weibo.find().count()
		inc = 0
		skipover = True

		for doc in deleted_weibo.find():

			thispostid = doc["delpost_id"]

			### UNTIL WE FIND THE LAST POST WE SCANNED, SKIP OVER

			if(thispostid == lastpost_id):
				skipover = False
				continue
		
			if(skipover == True):
				continue			

			inc += 1
			if inc % 10 == 0:
				print "======================" + str(inc * 1.0 / maxcount) + "% done"
			#print doc
			#print doc["delurl"]
			#print thispostid
			#print doc["followers_count"]
			#screen_name, post_id, created_at,deleted_at
			created_at = search_date(thispostid)
			if(created_at == -1):
				continue
			if(created_at == -10):
				print "LIMIT EXCEEDED - TRY AGAIN NEXT HOUR"
				break
	
			regresult = re.search("uid=(\d*)\&", doc["delurl"])
			thisposter_id = regresult.groups()[0]

			print thispostid + "," + created_at + "," + thisposter_id
			wf.write( thispostid + "," + created_at + "," + thisposter_id + "\n")


def search_date(postid):

	print "=========" 
	print "==POSTID = " + str(postid) 


	thiscreated = -1

	for i in xrange(1,10, 1):
		increment = i
		searchid = int(postid) + increment

		r = requests.get('https://api.weibo.com/2/statuses/show.json', params={"access_token": weibo_accesstoken, "id": searchid })

		rdata = r.json()

#		print rdata
		try:
			if rdata["error"] == "User requests out of rate limit!":
			#try agin later
				return -10
		except:
			pass

		print rdata
		if "created_at" in rdata:
		#if rdata["created_at"] is not None:
			#print rdata["created_at"]
			print  "=====  searching for " + str(searchid )+ ": FOUND" 
#			logging.debug(rdata["created_at"])
			thiscreated = parse(rdata['created_at']).strftime('%s')
			return thiscreated

		print  "=====  searching for " + str(searchid )+ ": NO" 

	return thiscreated


	#weibo_postid_querystring

#csvize_sample()
csvize_deleted()
#deleted_in_sample()


