PyPhotoOrganizer
================

Python script to organize image files in folders by date.

Usage:
photoOrganizer [-v]  <source_directory> <destination_directory>

Behavior:
Traverses the source directory recursively and copies image files found (.mov, .avi, .jpg, .png) into a corresponding date folder in the destination directory.
The destination date folder corresponds to the day in the image date. The format for the destination folder is YYYY-mm-dd, .e.g. 2013-01-01.
The date of the image is determined from the mtime as follows:

struct = time.localtime (mtime);
				destinationFolder = "%s-%02i-%02i" % (struct[0], struct[1], struct[2]);


Goals
------

1. Avoid duplicates: Files with the same name, size and date are considered duplicates. 
2. Preserve versions: Files with the same name and date but different size are preserved with its file size as suffix. E.g. photo.jpg and photo_1343342.jpg.
3. Incremental: photoOrganizer can be ran with different source folders and the same destination folder to incrementally add photos to the collection.

