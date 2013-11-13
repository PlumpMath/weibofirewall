import codecs
import json
import datetime
from dateutil.parser import parse
import sys
import weibo_settings
import weibo_module
import hashlib

### TAKES JSON FILE AND OBFUSCATES IT
## HASHES user_id and post_id

d = "3634509566164678"
salt = "w3ibo"
print int(hashlib.sha512(d + salt).hexdigest(), 16) % 10000

