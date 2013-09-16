import codecs
import pymongo
import csv
import json
import datetime
from dateutil.parser import parse
import requests
import logging
import re
import os
import weibo_settings
import weibo_module

this_post_id = "3622155533096449"

this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

csvline = this_post["post_id"] , this_post["user_id"] , this_post["user_name"] , this_post["user_follower_count_initial"] , this_post["user_follower_count"] , this_post["post_original_pic"] , this_post["post_created_at"] , this_post["post_repost_count_initial"] , this_post["post_repost_count"] , this_post["post_text"] , this_post["started_tracking_at"] , this_post["is_deleted"] , this_post["is_retired"] , this_post["error_message"] , this_post["error_code"] , this_post["last_checked_at"] , this_post["post_lifespan"]


csvline = map((lambda x: unicode(x)), csvline)
csvline = u','.join(csvline)

print csvline


