import codecs
import json
import datetime
from dateutil.parser import parse
import sys
import weibo_settings
import weibo_module
import weibo_accesstokens
import hashlib



def json_obfuscate(oldfilename, newfilename):

	oldjson = []
	with codecs.open(oldfilename, "rt") as f:
		oldjson = json.load(f)
			

	newf = codecs.open(newfilename, "wb")
#	print oldjson

	newf.write("[ " + "\n")

	#iterate through posts
	postno = 0
	for thisjson in oldjson:

		postno += 1

		prevpostid = thisjson['post_id']

		thisjson['user_id'] = weibo_module.hashmod(thisjson['user_id'], weibo_accesstokens.salt, weibo_accesstokens.user_id_mod)
		thisjson['post_id'] = weibo_module.hashmod(thisjson['post_id'], weibo_accesstokens.salt, weibo_accesstokens.post_id_mod)

		print prevpostid + "," + thisjson['post_id']
		#wf.write(json.dumps(thisjson, ensure_ascii=False))
		newf.write(json.dumps(thisjson))

		if postno != len(oldjson):
			newf.write(", ")

		newf.write("\n")

	newf.write(" ]" + "\n")
	
	newf.close()


#json_obfuscate(weibo_settings.deleted_log_json_filename, weibo_settings.deleted_log_json_obfuscated_filename)
json_obfuscate("data/deleted_weibo_log_launch_v1.json", weibo_settings.deleted_log_json_obfuscated_filename)

