import json
import weibo_settings
from pprint import pprint

json_filename = weibo_settings.deleted_log_json_filename 

json_data=open(json_filename)

data = json.load(json_data)

json_data.close()

postids = []
for thispost in data:
	postids.append(int(thispost["post_id"]))

print postids
