#!/usr/bin/env python

from smugpy import SmugMug

import re
import time

API_KEY = "yTTjttx2pkK1QSTIPS4geSsTzXZqtdxp"
OAUTH_SECRET = "786c1e774f5d6c5dda7e92bdf7d4b30c"

# smugmug = SmugMug(api_key=API_KEY, oauth_secret=OAUTH_SECRET,
#                   app_name="keyword-fixer")

# #Oauth handshake
# smugmug.auth_getRequestToken()
# raw_input("Authorize app at %s\n\nPress Enter when complete.\n" % (smugmug.authorize()))
# smugmug.auth_getAccessToken()

smugmug = SmugMug(  api_key=API_KEY, api_version="1.3.0",
                    app_name="keyword-fixer")

print "smugmug object BEGIN\n"
print smugmug
print "smugmug object END\n"

# Basic flow:
#  (1) Download keyword strings for images in albums matching condition
#      Input:  Condition to filter albums: regex, LastUpdated, ??
#      Output: file mapping imageID to keyword string
#  (2) Analyze keyword strings, suggest remapping
#      Input:  file mapping imageID to keyword string
#      Output: file listing each keyword, its frequency, and suggested mapping
#              e.g.   "cardbaord"  x 3  -> "cardboard"
#  (3) Remap keywords
#      Input:  Output files from previous two steps, possibly after editing
#      Output: New file mapping imageID to keyword string
#        Q:  Should file include both before and after keywords?
#        Q:  Should it include unchanged keywords?
#  (4) Upload keyword strings.
#      Input:  File mapping imageID to keyword string
#
# Basic data structure:
# keyinfo["images"][imageID]["old"] : original keywork string
#                           ["new"] : updated keywork string
#                           ["key"] : Image key
#        ["keywords"][keyword]["cnt"] : Frequency
#
# Better data structure:
# Struct Album:
#   Id:
#   Key:
#   Images:  List of Image structs
#
# Struct Image:
#   Id:
#   Key:
#   OrigKeywordString:
#   OrigKeywords:  list()
#   Keywords:  list() of proposed new keywords for image
#
# Struct Keyword:
#   string Word:
#   int	   Count:
#   list   Variations:  typographically close variations, e.g. 1 letter
#                	dropped, two letters swapped

#
# Generate map of each keyword with each letter removed
#   Cross reference this list to identify letter swaps.  (how??)
#   See http://norvig.com/spell-correct.html


acnt = 0
keywords = dict()
months_ago = 3
last_updated = int(time.time() - 3600*24*30*months_ago);
albums = smugmug.albums_get(NickName="brettcoon",LastUpdated=last_updated)
for album in albums["Albums"]:
    acnt = acnt + 1
    if acnt > 5:
      break
    albumID = album["id"]
    albumKey  = album["Key"]
    image_list = smugmug.images_get(AlbumID=album["id"],
				    AlbumKey=album["Key"],
				    LastUpdated=last_updated)
    # for k in image_list["Album"].keys():
    #   print "%s, %s has key=%s" % (album["id"], album["Title"], k)
    print "%s, %s has %d images" % (album["id"], album["Title"],
                                    image_list["Album"]["ImageCount"])
    re_keydiv = re.compile(',\s*')
    for image in image_list["Album"]["Images"]:
      imId = image["id"]
      imKey = image["Key"]
      imInfo = smugmug.images_getInfo(ImageID=imId,ImageKey=imKey)
      # print "\nimInfo start:"
      # print imInfo
      # print "imInfo end.\n"
      kwords = imInfo["Image"]["Keywords"]
      print "  image id=%s key=%s kwords='%s'" % (imId,imKey,kwords)
      for kw in re_keydiv.split(kwords):
        # Update count for this keyword
        if kw not in keywords:
          keywords[kw] = dict()
          keywords[kw]["cnt"] = 0
          keywords[kw]["images"] = list()

        keywords[kw]["cnt"] = 1 + keywords[kw]["cnt"]
        keywords[kw]["images"].append((imId,imKey))

re_numonly = re.compile('^\d+$')
re_nummostly = re.compile('\d{5}')
re_nonums = re.compile('^\D+$')
re_inside_space = re.compile('^\S.*\s.*\S')
re_suspicious = re.compile('(^\d+$)|\W|\d{4}|(^$)')
for kw in keywords:
    print "Keyword: %-30s  Cnt: %3d  " % (kw,keywords[kw]["cnt"]),
    if re_inside_space.search(kw):
	print " probably needs to be split better",
    elif re_numonly.search(kw):
	print " is BAD",
    elif re_suspicious.search(kw):
	print " is really SUSPICIOUS",
    elif re_nummostly.search(kw):
	print " is SUSPICIOUS",
    print



