#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Eduardo Hueso on 2012-07-28.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt

import time
import os
import os.path
import shutil
import string

import PIL
from PIL import Image

help_message = '''
The help message goes here.
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def moveFilesIntoFoldersByDate (source=None, destination=None):
	for root, dirs, files in os.walk(source, topdown=False):
		for file in files:
			os.stat (os.path.join(root.file))			
			extension = string.upper(os.path.splitext(file)[1][1:])
			destinationPath = os.path.join(destination,extension)
			if os.path.exists(destinationPath) != True:
				os.mkdir(destinationPath)
			if os.path.exists(os.path.join(destinationPath,file)):
				print 'WARNING: this file was not copied :' + os.path.join(root,file)
			else:
				shutil.copy2(os.path.join(root,file), destinationPath)

def get_minimum_creation_time(exif_data):
    mtime = None
    if 306 in exif_data and exif_data[306] < mtime: # 306 = DateTime
        mtime = exif_data[306]
    if 36867 in exif_data and exif_data[36867] < mtime: # 36867 = DateTimeOriginal
        mtime = exif_data[36867]
    if 36868 in exif_data and exif_data[36868] < mtime: # 36868 = DateTimeDigitized
        mtime = exif_data[36868]
    return mtime
	
import PIL.ExifTags			
def exifTime(filepath):
	print filepath
	img = Image.open(filepath)
	exif_data = img._getexif()

#	exif = {
#	    PIL.ExifTags.TAGS[k]: v
#	    for k, v in img._getexif().items()
#	    if k in PIL.ExifTags.TAGS
#	}
#	print exif
	
	mtime = get_minimum_creation_time (exif_data)
	if (mtime == None):
		return None
		
	tokens = mtime.split()[0].split(':')
	return tokens
	
	
	
def doit (source, destinationRoot):
	index = {} # destination index ex. {'2012-01-01':[(IMG_10132.JPG, 1,023,231), (IMG_10133.JPG, 1023323)], 2012-01-02:[(IMG_3432.JPG, 342323423), (IMG_4332.JPG, 3423234)] }
	#nameCountIndex = {} # ex. {('2012-01-01', 'IMG_342.JPG'):3}
	sourcesIndex = {} #ex. {'2012-01-01':['/Users/eddy/Pictures/2012-01-01/IMG_32342.JPG', '/Users/eddy/Pictures/2012-01-01/IMG_3434.JPG'], '2012-01-02:[]}
	conflictIndex = {} #
	copies = {}
	conflicts = []
	print source
	for root, dirs, files in os.walk(source, topdown=False):
		for file in files:
			print file
			(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(root,file))
#			mtime = os.path.getmtime(os.path.join(root,file))
			extension = string.upper(os.path.splitext(file)[1][1:])
			if (extension == 'JPG' or extension == 'AVI' or extension == 'MOV' or extension == 'PNG'):
				filepath = os.path.join(root,file)
				print filepath
				struct = exifTime(filepath)
				if (struct == None):
					struct = time.localtime (mtime);
					
				destinationFolder = "%s-%02i-%02i" % (struct[0], struct[1], struct[2]);
				
				# create destination index entry if it doesn't exist
				if (not destinationFolder in index):
					index[destinationFolder] = []
					sourcesIndex[destinationFolder] = []
					#nameCountIndex[destinationFolder] = []
					#prepolulate index with destination folder files
					destPath = os.path.join (destinationRoot, destinationFolder)
					if (os.path.exists (destPath)):
						for destTop, destDirectories, destFiles in os.walk(destPath, topdown=True):
							for destFile in destFiles:
								(destMode, destIno, destDev, destNlink, destUid, destGid, destSize, destAtime, destMtime, destCtime) = os.stat(os.path.join(destTop,destFile))
								index[destinationFolder].append ((destFile, destSize))
#								nameCountIndex[(destinationFolder, destFile)] = 1
							
				
				#print destinationFolder
				destination = os.path.join(destinationRoot, destinationFolder)
				destination = os.path.join(destination, file)
				
				#see if destination folder already contains this version of file
				suffixCounter = 1
				newFile = file
				done = False
				while (not done):
					found = False
					for e in index[destinationFolder]:
						if (e[0] == newFile):
							found = True
							if (e[1] == size):
								done = True
								#log conflict
								conflicts.append (os.path.join (root,newFile))
								if (newFile not in conflictIndex):
									conflictIndex[newFile] = []
								conflictIndex[newFile].append ((os.path.join(root,file), size))								
							else:
								newFile = file+'_'+`suffixCounter`
								suffixCounter+= 1
							break;
					if (not found):
						index [destinationFolder].append((newFile, size))
						copies[os.path.join(root,file)] = os.path.join(destinationFolder, newFile)
						done = True
						
				sourcesIndex[destinationFolder].append (os.path.join(root, file))

#	for key in sourcesIndex.keys():
#		print key
#		for source in sourcesIndex[key]:
#			print "	   " + source
#			
#	for key in conflictIndex.keys():
#		print key
#		if (len(conflictIndex[key]) > 1):
#			for source in conflictIndex[key]:
#				print "	   %s	 %i" % (source[0] , source[1])
#	print len(conflicts)
	
	print len(copies.keys())
	counter = 0
	for key in copies.keys():
		dest = os.path.join(destinationRoot,copies[key])
		destFolder = os.path.dirname(dest)
		if (not os.path.exists(destFolder)):
			os.mkdir(destFolder)
		print "%i) %s -> %s" % (counter, key, dest)
		copied = False
		retryCount = 0
		while copied == False and retryCount < 2:
		    try:
		        shutil.copy2 (key, dest)
		        copied = True
		    except:
		        print 'Copy failed - retrying'
		        retryCount+= 1
		
		#if (counter >= 1000):
		#	break
		counter+=1
	print len(conflicts)
	for conflict in conflicts:
		print conflict;
				
def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "ho:v", ["help", "output="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-o", "--output"):
				output = value
	
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2
		
	#doit ('/Volumes/Data/Picture Sources/Deepblue/Pictures_Old', '/Volumes/Data/Photo Organizer Library')
	#test2()
if __name__ == "__main__":
	sys.exit(main())
