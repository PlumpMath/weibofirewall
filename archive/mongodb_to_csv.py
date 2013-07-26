import pymongo
import csv
import json
import datetime
from dateutil.parser import parse

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

docno = 0

'''
for post in deleted_weibo.find():

	print "post = "
	postid =  post['delpost_id'] 
	print postid

	samplefind = sample_weibo.find( { 'post_id': postid })
	for doc in samplefind:
		docno += 1
		print "this is the doc = " + str(docno)
		print doc
	samplefind.rewind()

'''


def csvize_sample():

	#Fri May 03 07:49:13 +0800 2013
	#%a %b %d %H:%M:%S %z %Y

	print "post_id, created_at, screen_name"
	for doc in sample_weibo.find().sort("created_at").limit(10):
		#print doc
		thiscreated = parse(doc['created_at']).strftime('%s')
		thisname = doc["screen_name"].encode("utf8")
		print doc["post_id"] + ", " + thiscreated + ", " , thisname
		#print doc["followers_count"]
		#screen_name, post_id, created_at,deleted_at


def csvize_deleted():

	#Fri May 03 07:49:13 +0800 2013
	#%a %b %d %H:%M:%S %z %Y

	print "post_id"
	for doc in deleted_weibo.find().limit(1):
		#print doc
		thisid = doc["delpost_id"]
		print thisid
		#print doc["followers_count"]
		#screen_name, post_id, created_at,deleted_at

		print search_date(thisid)


def search_date(postid):
	print "==="
	print "searching for " + postid
	return "blahblah" + postid

	weibo_postid_querystring

csvize_deleted()


