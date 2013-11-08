import json
import weibo_settings
from pprint import pprint
import os.path
from PIL import Image
import math
from subprocess import call


json_filename = weibo_settings.deleted_log_json_filename 
imgblurdir = weibo_settings.imgblurdir
imgdir = weibo_settings.imgdir

def stampheight(imagewidth):
	# figured this out by plotting image width and stamp height and doing a linear regression
	return math.ceil((imagewidth * 0.056) + 13)

def getfilename(post_id, fullfilename):
	thisextension = os.path.splitext(fullfilename)[1]
	thisfilename = post_id + thisextension
	return thisfilename


def run_blur_imagemagick(post_id, filename, imgdir, imgblurdir):

	print "Processing " , post_id
	width, height = get_image_size(imgdir + filename)
	# does the blurring
	thisstampheight = stampheight(width)

	# in imagemagick
	# first we want to make a mask, where most of the mask is white
	# and the bottom (height - stampheight) to (height) in the y direction is blurred
	# as a rectangle, this would be UL (0, height - stampheight), LR (width, height)
	# mask making operation:
	# convert -gamme 0 -fill white -size WIDTHxHEIGHT xc:none -draw 'rectangle 0, HEIGHT-STAMPHEIGHT WIDTH, HEIGHT' MASKIMAGE
	# blurring operation:
	# convert SOURCEIMAGE -blur 0x6 BLURIMAGE
	# composite operation:
	# convert SOURCEIMAGE BLURIMAGE MASKIMAGE -composite FINALIMAGE

	# chained together:
	# convert -size WIDTHxHEIGHT xc:none -draw 'rectangle 0, HEIGHT-STAMPHEIGHT WIDTH, HEIGHT' -write mpr:mask +delete convert SOURCEIMAGE -blur 0x6 -write mpr:blur +delete convert SOURCEIMAGE mpr:blur mpr:mask -composite FINALIMAGE


	maskblurstring = "/usr/bin/convert -gamma 0 -fill white -size " + str(width) + "x" + str(height) + " xc:none -draw 'rectangle 0, " + str(height - thisstampheight) + " " + str(width) + ", " + str(height) + "' -write mpr:mask +delete " + imgdir + filename + " -blur 0x" + math.ceil(thisstampheight / 4) + " -write mpr:blur +delete " + imgdir + filename + " mpr:blur mpr:mask  -composite " + imgblurdir + filename

#	call(maskstring, shell=True)
#	call(blurstring, shell=True)
#	call(compositestring, shell=True)
	call(maskblurstring, shell=True)

	print "blurred the bottom of ", filename , " by ", thisstampheight , " pixels, storead as " + imgblurdir + filename


def get_image_size(fullfilename):
	# pick an image file you have in the working directory
	img = Image.open(fullfilename)
	# get the image's width and height in pixels
	width, height = img.size
	return width, height

	
#### MAIN


# get json data
json_data=open(json_filename)
posts = json.load(json_data)
json_data.close()

print "data loaded"

print "images analyzed"

#sort lean posts. not really necessary but hey.
#leanposts = sorted(leanposts, key=lambda k: k['post_id']) 

iter = 0
for thispost in posts:

	iter += 1
	thisfilename = getfilename(thispost["post_id"], thispost["post_original_pic"])

	print "(" , iter , "/" , len(posts) , "): attempting post # ", thispost["post_id"]

	# check if original file exists
	if(not os.path.isfile(imgdir + thisfilename)):
		print "DOES NOT EXIST: "  + imgdir + thisfilename 
		continue

	# check if blurred file exists
	if(os.path.isfile(imgblurdir + thisfilename)):
		print "already exists: " + imgblurdir + thisfilename
		continue

	# if original file exists and blurred doesn't, let's do this

	run_blur_imagemagick(thispost["post_id"], thisfilename, imgdir, imgblurdir)




