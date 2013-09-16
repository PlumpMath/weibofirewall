import pymongo
import csv



db_hostname = "ec2-107-21-88-135.compute-1.amazonaws.com"
db_username = "journalist"
db_userpass = "journalist"


from pymongo import MongoClient
client = MongoClient()

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
for doc in sample_weibo.find().limit(50):
	print doc
