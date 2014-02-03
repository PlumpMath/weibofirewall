#NOTICE: This repository is obsolete, as it has moved to a private repository.

# Jumping The Great Firewall

#### With the ADVP at GSAPP - http://advp.gsapp.org

SHORT SUMMARY: 
These scripts grab image-laden posts from the friends ofa Sina Weibo account, and tracks the posts for sudden deletions (aka censorship). The scripts then massage the data out to a CSV file, which can then be read by a visualization client.

LESS SHORT SUMMARY:
* Detecting the deletion of a post is only possible by frequently checking the post at regular intervals. Given a desired interval, the script automatically calculates the number of posts trackable given the API rate limit.
* Temporal data (such as repost count, follower count) is logged continuously into a single 'checklog' database, which means that we can grab data about the increasing popularity of a post before its deletion.
* When tracking posts, the scripts download the image initially, so the image is accessible after the deletion of the post.
* Given a certain duration from the posts's creation, the script will 'retire' checking of the posts so that it's not tracking a post unlikely to be deleted. For example, a post that is a week old is probably unlikely to be deleted.
* A wrapper around the Requests API uses a rotating list of API keys as to get around Weibo's 150 requests per hour rate limit. The wrapper will automatically detect when a rate limit error is given, and will swap out an API key with a new one.

LONGER SUMMARY:
* To come
