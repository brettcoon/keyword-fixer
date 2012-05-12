#!/usr/bin/env python

from smugpy import SmugMug

import re

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
#  (1) Download keyword strings for images in albums matching album_re
#      Input:  regular expression to limit albums
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
# Generate map of each keyword with each letter removed
#   Cross reference this list to identify letter swaps.  (how??)


acnt = 0
keyword_cnt = dict()
keyword_dict = dict()
keywords = dict()
albums = smugmug.albums_get(NickName="brettcoon")
for album in albums["Albums"]:
    acnt = acnt + 1
    if acnt > 5:
      break
    albumID = album["id"]
    albumKey  = album["Key"]
    image_list = smugmug.images_get(AlbumID=album["id"],AlbumKey=album["Key"])
    # for k in image_list["Album"].keys():
    #   print "%s, %s has key=%s" % (album["id"], album["Title"], k)
    print "%s, %s has %d images" % (album["id"], album["Title"],
                                    image_list["Album"]["ImageCount"])
    re_keydiv = re.compile(',\s*')
    re_numonly = re.compile('^\d+$')
    re_nummostly = re.compile('\d\d\d\d')
    re_nonums = re.compile('^\D+$')
    re_suspicious = re.compile('(^\d+$)|\W|\d{4}|(^$)')
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
        # print "Found kw='%s'" % (kw)
        if re_suspicious.search(kw):
          print "** Found bad keyword='%s' in image (%s,%s)" % (kw,imId,imKey)
        elif re.search(re_nummostly,kw):
          print "** Found SUSPICIOUS kw=%s" % (kw)

        # Update count for this keyword
        if kw not in keywords:
          keywords[kw] = dict()
          keywords[kw]["cnt"] = 0
          keywords[kw]["images"] = list()

        keywords[kw]["cnt"] = 1 + keywords[kw].get("cnt",0)
        # Add this keyword to our list
        keywords[kw].setdefault("images",list())
        keywords[kw]["images"].append((imId,imKey))
