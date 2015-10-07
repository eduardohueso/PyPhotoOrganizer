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
import shelve

import PIL
from PIL import Image

help_message = '''
The help message goes here.
'''
class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def get_minimum_creation_time(exif_data):
	if (exif_data == None):
		return None

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
	try:
		img = Image.open(filepath)
		exif_data = img._getexif()
	except Exception, e:
		print 'Error obtaining exif data for file ' + filepath
		return None

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
	
####################
# Class photoLibrary
####################
class PhotoLibrary:
    suffixSeparator = "_*_"
    libraryFilename = 'PhotoOrganizerLibrary'
    indicesFilename = 'indices'
    sizeToleranceFactor = 0.05 
    
    def __init__(self, libraryPath):
        self.libraryPath = libraryPath
        self.library = {}
#        self.sourcesIndex = {}
        self.ignoreIndex = {}
        self.doNothing = False
    
    def loadLibrary(self):
        filename = os.path.join(self.libraryPath, self.libraryFilename)
        print 'Loading library from file ' + filename
        libFile = shelve.open(filename)
#        print libFile
        self.library = libFile['library']
        self.ignoreIndex = libFile['ignoreIndex']
        libFile.close()
        
    def saveLibrary(self):
        filename = os.path.join(self.libraryPath, self.libraryFilename)
        libFile = shelve.open(filename)
        libFile['library'] = self.library 
        libFile['ignoreIndex'] = self.ignoreIndex
        libFile.close()
    
    def createLibraryDB(self, source):
        destPath = os.path.join(source, self.libraryFilename)
        if (os.path.isfile(destPath)):
            print 'DB file already exists, aborting.'
        else:
            for root, dirs, files in os.walk(source, topdown=False):
                #print root
                for file in files:
                    extension = string.upper(os.path.splitext(file)[1][1:])
                    if (extension == 'JPG' or extension == 'AVI' or extension == 'MOV' or extension == 'PNG'):
                        filepath = os.path.join(root,file)
                        try:
                            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filepath)
                        except Exception, e:
                            print 'Error: could not read file ' + filepath
                            continue       
                        if (not root in self.library.keys()):                
                            self.library[root] = []							
                        self.library[root].append((file, size, filepath))
            
    
    #destinationFilename:
    # returns '' if the file is a duplicate of a file already in the destination folder or a filename which includes a version suffix if the file doesn't exist already.
    # A file is considered a duplicate if it has the same base name and same size (within a threshold).
    # the version suffix is used if a file with the same <name> | <name>_*_<version> already exists. If any number of files already exists with the same base name, a new name is generated incrementing the highest exisitng version.
    
    def destinationFilename (self, root, file, size, destinationFolder):
    	#see if destination folder already contains this version of file
    	suffixValue = -1
    	newFile = file
    	isDup = False
        numDups = 0
    	isHigherRes = False
    	for e in self.library[destinationFolder]:
            tokens = e[0].split('.')
            destFilename = '.'.join(tokens[0:-1])
            destExtension = tokens[-1]
            
            tokens = destFilename.split(self.suffixSeparator)
            destSuffix = ''
            destPrefix = tokens[0]
            
            if (len(tokens) == 2): 
                destSuffix = tokens[-1]
                
            newFilename = '.'.join(newFile.split('.')[0:-1])
            newExtension = newFile.split('.')[-1]
            
            if (destPrefix == newFilename):
                if (len(destSuffix)): # we found the file with a suffix. 
                    newSuffixValue = int(destSuffix)            
                    if (newSuffixValue > suffixValue):
                        suffixValue = newSuffixValue
                else:# We found the file but without a suffix
                    suffixValue = 0
                
                if (e[1] > size*self.sizeToleranceFactor): # Only create versions which are larger than the existing one by some margin
                    numDups +=1
                    isDup = True
                    break
                                        
        if (isDup):
            return ''
            
        suffixValue += 1
        if (suffixValue > 0):
            newFile = newFilename+self.suffixSeparator+str(suffixValue)+'.'+newExtension
        return newFile
	    
    def consolidateLibrary(self, destinationRoot, startIndex = 0, overwrite = False):
        counter = 0
        skippedExistingCount = 0
        copiedCount = 0
        for key in self.library.keys():
            destFolder = os.path.join(destinationRoot, key)
    	    if (not os.path.exists(destFolder)):
    	        os.mkdir(destFolder)
            for (filename, size, sourcePath) in self.library[key]:
                if (counter <= startIndex):
                    counter+=1                
                    continue
                
                destPath = os.path.join(destFolder, filename)
                copied = False
                retryCount = 0
                if (not overwrite):
                    if (os.path.isfile(destPath)):
                        skippedExistingCount +=1
                        #print "%i) %s -> skipping" % (counter, sourcePath)                        
                        counter+=1
                        continue
                    else:
                        print "%i) %s -> %s" % (counter, sourcePath, destPath)
                
                if (not self.doNothing):
                    while copied == False and retryCount < 2:
                        try:
                            shutil.copy2 (sourcePath, destPath)
                            copied = True
                            copiedCount +=1
                        except:
                            print 'Copy failed - retrying'
                            retryCount+= 1		
                counter+=1
        print 'copied: %i    skipped: %i' % (copiedCount, skippedExistingCount)
    
    def importSource (self, source):
        destinationIndex = {} 
        print source
        dups = 0
        news = 0
        for root, dirs, files in os.walk(source, topdown=False):
            #print root
            numNew = 0
            numDups = 0
            numVersions = 0
            for file in files:
                extension = string.upper(os.path.splitext(file)[1][1:])
                if (extension == 'JPG' or extension == 'AVI' or extension == 'MOV' or extension == 'PNG'):
                    filepath = os.path.join(root,file)
                    try:
                        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filepath)
                    except Exception, e:
                        print 'Error: could not read file ' + filepath
                        continue
                    dateStruct = None
                    if (extension == 'JPG'):
                        dateStruct = exifTime(filepath)
					
                    if (dateStruct == None):
                        dateStruct = time.localtime (mtime);
                        
                    destinationFolder = "%s-%02i-%02i" % (dateStruct[0], dateStruct[1], dateStruct[2])
                    
                    # Add new folder to the library if needed
                    if (not destinationFolder in self.library.keys()):
                        self.library[destinationFolder] = []							
                        self.ignoreIndex[destinationFolder] = []
				
                    newFile = self.destinationFilename(root, file, size, destinationFolder)
                    if (len(newFile) >0): 
                        self.library[destinationFolder].append((newFile, size, filepath))
                        numNew +=1
                    else:
                        if (not filepath in self.ignoreIndex[destinationFolder]):
                            self.ignoreIndex[destinationFolder].append(filepath)
                        numDups+=1 
            dups += numDups
            news += numNew
        print source + ' duplicates: ' + `dups` + '  new: ' + `news` 
		
    def printLibrary(self):
        totalFiles = 0
        totalIgnores = 0
        totalSize = 0
        for key in self.library.keys():
            print key
            for file in self.library[key]:
                print '    '+file[0] + '    ' + str(file[1]/1000) +'kb' + '    ' + file[2]
                totalFiles +=1
                totalSize += file[1]
                
        for key in self.ignoreIndex.keys():
            totalIgnores += len(self.ignoreIndex[key])
            
        print 'total files: ' + str(totalFiles) + '    ' + 'total size: ' + str(totalSize/1000) + ' KB'
        print 'total ignores: ' + str(totalIgnores)
        

    def printIgnored(self):
        totalIgnores = 0
        for key in self.ignoreIndex.keys():
            print key
            for file in self.ignoreIndex[key]:
                print '    '+file
            totalIgnores += len(self.ignoreIndex[key])
            
        print 'total ignores: ' + str(totalIgnores)
        
#Class photoLibrary - end
def load(path):
    po = PhotoLibrary(path)
    po.loadLibrary()
    return po
    
def createDB():
    po = PhotoLibrary('PhotoOrganizerLibrary')
    po.createLibraryDB('PhotoOrganizerLibrary')
    return po

def test():
    po = load()
#    po.loadLibrary()
    po.importSource('PhotoSource/Run1')
    po.importSource('PhotoSource/Run2')
    po.saveLibrary()
    print 'Library'
    print po.library
    print 'Ignores'
    print po.ignoreIndex
    po.consolidateLibrary('Library')
    

def main(argv=None):
    test()
    

if __name__ == "__main__":
	sys.exit(main())
