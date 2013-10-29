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
accesstokens = [
	'2.00Ga5TmDFObaNC7aeeff1e5cZR1oTD', 
	'2.00YJl5fDtbWV2B908f7d5e64BIPIwC',
	'2.00Ga5TmDGX4hRE1447f826bclbRQJC',
	'2.00Ga5TmD0Ugujs972d9aab4724Dt4D',
	'2.00X32EqBHyA86B7b7f20b938QdUbLC',
	'2.00X32EqB2NJFhC94e6fe6b490_6uQ_',
	'2.00X32EqBnWX2zCa083e0c752msL92D',
	'2.00X32EqBD_zIbEc7dd5071230n1Xja',
	'2.00z4C41CF2V28Cef83cba5efoiFpYD',
	'2.00z4C41C1CN68Ed1f57dff5axMwWTC',
	'2.00z4C41Co8UM6D63e6869f8cESV6EE',
	'2.00z4C41CSmOUJC8c9a0a1a14kqcSWD',
	'2.00z4C41CJnBlGE28d98ab90e0u579F',
	'2.00z4C41C0NARpO5c5964082fzqj7DB',
	'2.00z4C41Cc55p9B808aaed88b0k8T1o',
	'2.00z4C41C0vOLq78a5ddc308bpp3xXE',
	'2.00z4C41C0eDJLU80a1b73b6ffjPUaB',
	'2.00z4C41Ci4LUAEce47b71dbe0mY3Bp',
	'2.00Di62ME0qyitGf0f1be1db0rgiqdC',
	'2.00Di62MEFOH5hCe4419280ebeNQR_C',
	'2.00Di62ME0D3TJI2ba7dbb5e8XkLqQD',
	'2.00Di62ME0V6KnF23fe7b27f9hCpuOB',
	'2.00Di62MEzdLR7Cb5a9ed458amgmt_C'
]


apiurl_accessfriends = "https://api.weibo.com/2/statuses/friends_timeline.json"
apiurl_checkstatus = "https://api.weibo.com/2/statuses/show.json"

imgdir = "/home/provolot/www/SIDL/firewall_dev/weibo_images/" #with trailing slash

queries_per_token = 100 #hardcoded - set this to 100 to give us some padding, really is 150

pagemax = 2 # let's not go more than 10 pages back while looking for anything

to_timezome_name = 'Asia/Shanghai'
display_timezone = "Asia/Shanghai"

#the WEIBO API KEY only takes 150 REQUESTS PER HOUR. 
#So our limiting factor is the check time. 
#At a checking resolution of 1 hr (each post is checked once every hour),
#only 150 posts can be tracked per api token.
#At a checking resolution of 30 min, only 75 posts can be tracked per api token.
#At a checking resolution of X hours, only 150 * X posts can be tracked per api token.
#
#HOWEVER the code gets a little complex if X > 1. if X = 10, for example, then checking 1500 posts would still be staggered over 10 hours, requiring each post to be inserted into a 'queue' to check, etc. For the sake of simplicity, then, X <= 1.

# period of tracking, unit: hours. 
# ex) 0.5 = track each post every 30 minutes
tracking_period = 0.03 

# default: set to -1 to determine tracking posts based on period, set to number to specificy number of posts to track
# mostly for debugging purposes
# ex) 5 = track only 5 posts at a time
track_posts_override = -1 

#timeout - if a post is alive past this many seconds, then go onto the next
track_posts_timeout = 14400 #4 houts

deleted_csv_filename = "/home/provolot/www/SIDL/firewall_dev_dev/data/deleted_weibo.csv"
deleted_log_csv_filename = "/home/provolot/www/SIDL/firewall_dev/data/deleted_weibo_log.csv"
all_log_csv_filename = "/home/provolot/www/SIDL/firewall_dev/data/all_weibo_log.csv"

#period, in seconds
tracking_period_seconds = tracking_period * 3600

#delim = u'|||'
delim = chr(31)
delim_log = u','
