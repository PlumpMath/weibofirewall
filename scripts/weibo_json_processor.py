import codecs
import json
import datetime
from dateutil.parser import parse
import sys
import weibo_settings
import weibo_module
import hashlib



def json_obfuscate(orgfilename, newfilename):
	newf = codecs.open(newfilename, "wb")

	oldf = codecs.open(newfilename, "r")
	oldjson = json.load(oldf)

	newf.write("[ " + "\n")

	#iterate through posts
	postno = 0
	for thisjson in oldjson:

		postno += 1
		print "\n==PROCESSING (", postno, " / ", len(odljson), ") POST "

		thisjson['user_id'] = weibo_module.hashmod(thisjson['user_id'], weibo_settings.salt, weibo_settings.user_id_mod)
		thisjson['post_id'] = weibo_module.hashmod(thisjson['post_id'], weibo_settings.salt, weibo_settings.post_id_mod)

		#wf.write(json.dumps(thisjson, ensure_ascii=False))
		newf.write(json.dumps(thisjson))

		if postno != num_query_posts:
			newf.write(", ")

		newf.write("\n")

	newf.write(" ]" + "\n")

json_obfuscate(weibo_settings.deleted_log_json_filename, weibo_settings.deleted_log_json_obfuscated_filename)

