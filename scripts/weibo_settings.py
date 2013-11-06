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
deleted_log_json_filename = "/home/provolot/www/SIDL/firewall_dev/data/deleted_weibo_log.json"
all_log_csv_filename = "/home/provolot/www/SIDL/firewall_dev/data/all_weibo_log.csv"

#period, in seconds
tracking_period_seconds = tracking_period * 3600

#delim = u'|||'
delim = chr(31)
delim_log = u','
