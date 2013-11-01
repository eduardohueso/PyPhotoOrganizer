#!/usr/bin/env python
# encoding: utf-8

import sys
import photoOrganizer
import shutil 
import os


def clearFolderRecursively(folder):
	for root, dirs, files in os.walk(folder, topdown=False):
		for file in files:
		    file_path = os.path.join(root, file)
		    try:
		        if os.path.isfile(file_path):
		            os.unlink(file_path)
		    except Exception, e:
		        print e	
		if (not root == folder):
			try:
				os.unlink(root)
			except Exception, e:
				print e				
			
def clearFolder(folder):
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    try:
	        if os.path.isfile(file_path):
	            os.unlink(file_path)
	    except Exception, e:
	        print e

def main(argv=None):
#	photoOrganizer.exifTime('../Tests/PhotoSource/Run1/2013-09-23/IMG_4957.JPG')
	clearFolderRecursively('../Tests/PhotoDestination')
	photoOrganizer.doit ('../Tests/PhotoSource/Run1', '../Tests/PhotoDestination')
	photoOrganizer.doit ('../Tests/PhotoSource/Run2', '../Tests/PhotoDestination')

if __name__ == "__main__":
	sys.exit(main())