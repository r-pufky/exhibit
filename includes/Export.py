#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
# Copyright 2008, Robert Pufky
# Exhibit - file export Class
#
""" Exports images from iPhoto to a given local directory

Functional Notes:
  All files are exported to the specified directory in exhibit.config:
    Thumbnails pictures are uploaded as: [LibraryID][GUID][T].[extension]
    Image data are uploaded as: [LibraryID][GUID].[extension]
    Originals are uploaded as: [LibraryID][GUID].[extension]
  
  Movies, and other image datatype will always have a thumbnail picture, with
    the actual data stored in Image data ([LibraryID][GUID].[extension])

Known Bugs:
  If the destination file has an actual '\' in the name, it will be removed as 
  all escape characters ('\') are automatically removed.  This should not happen too often, as this is a very rare case.  Export will thrown an "Export failed"
  message with the bad filename.  Might need to implement regular expressions to
  fix this bug.

Testing:
  Test cases are setup for a generic MySQL database.  Look at the test cases at
  the bottom of this class, and setup (or change) the connection information to
  your database to verify the test passes.  These tests REQUIRE that AlbumData
  and MySQL modules can be imported, and that an example AlbumData.xml file
  exists in the same directory.
  
  All tests passed before releasing.

Debugging:
  Removing the optimization flag (-OO) from this file will turn debugging on.

Attributes:
  Class Export: Exports current images in SQL database to a local directory.
"""
from __future__ import division
__author__ = "Robert Pufky (github.com/r-pufky)"
import os
import sys
import shutil
import commands
import ProgressIndicator


class Export(object):
  """ Exports image data to a local directory.
  
  Attributes:
    Run(): exports image data to local directory
  """
  __author__ = "Robert Pufky (github.com/r-pufky)"
  __version__ = "1.0"
  
  def __init__(self, album_data=None, db=None, export_options=None, 
               quiet=False):
    """ Initializes export module.
    
    Args:
      album_data: Dictionary from album_data processing
      db: A SQL query object with Close,DatabaseCheck,Insert,Update,Delete, 
          and Select functions
      export_options: Dictionary with options to use for rsync:
          {'export_path' - path to store exported albums
           'link'}       - True if files should be symlinked, False for copy

    Kills:
      sys.exit: Invalid arugments passed to object
    """
    self.__DEBUG_INFO = "DEBUG:[Export."
    self.__WARNING_INFO = "WARNING:[Export."
    self.__IMAGE_TRANSLATION = (
        {'ThumbPath':"T",'OriginalPath':"O",'ImagePath':""})
    self.__escape_characters = [' ','"',"'",'`','(',')','&','<','>','-','.']
    if not db:
      sys.exit("%(debug)s__init__] SQL connector object not provided!" %        
               {'debug':self.__DEBUG_INFO})
    if not album_data:
      sys.exit("%(debug)s__init__] AlbumData dict not provided!" % 
               {'debug':self.__DEBUG_INFO})
    if not export_options:
      sys.exit("%(debug)s__init__] Server options not provided!" % 
               {'debug':self.__DEBUG_INFO})
    if not isinstance(quiet, bool):
      sys.exit("%(debug)s__init__] Quiet option was not specified correctly!" % 
               {'debug':self.__DEBUG_INFO})
    self.__db = db
    self.__album_data = album_data
    self.__export = export_options
    self.__quiet = quiet
    self.__db_library_id = self.__db.Select(
        "iPhotoLibrary",
        {'Path':self.__album_data.properties['Path'],
        'ArchiveID':self.__album_data.properties['ArchiveID']},
        limit=1)
    if self.__db_library_id:
      self.__db_library_id = self.__db_library_id[0]['ID']
    else:
      sys.exit("%(debug)s__init__] iPhotoLibraryID could not be retreived!" % 
               {'debug':self.__DEBUG_INFO})

  def __VerifyImageInDatabase(self, image_key=None):
    """ Verifies the image  actually exists in the database.
    
    If the image does not exist, a warning is issued, and None is returned.
    
    Args:
      image_key: Integer iPhoto Library's image id
      
    Kills:
      sys.exit: Bad SQL Query, invalid argument passed
      
    Returns:
      A dictionary containing image location data; or None
          {'GUID',
          'ThumbPath',
          'ImagePath',
          'OriginalPath'}
    """
    if not image_key:
      sys.exit("%(debug)s__VerifyImageInDatabase] Image ID is not valid!" % 
               {'debug':self.__DEBUG_INFO})
    image_dict = self.__db.Select("Images",
                                  {'iPhotoLibraryID':self.__db_library_id,
                                  'ImageID':image_key},
                                  limit=1)
    if image_dict:
      location_data = {}
      location_data['GUID'] = image_dict[0]['GUID']
      if image_dict[0]['ThumbPath']:
        location_data['ThumbPath'] = image_dict[0]['ThumbPath']
      if image_dict[0]['ImagePath']:
        location_data['ImagePath'] = image_dict[0]['ImagePath']
      if image_dict[0]['OriginalPath']:
        location_data['OriginalPath'] = image_dict[0]['OriginalPath']
      return location_data
    else:
      print ("%(warn)s__VerifyImageInDatabase] Image [%(key)s] not in SQL "
             "database!" % {'warn':self.__WARNING_INFO,'key':image_key})
      return None

  def __GetDestFilename(self, GUID=None, image_key=None, path=None):
    """ Builds the destination filename based on image image_key.

    Args:
      GUID: String GUID of the image
      image_key: String image_key passed (must exist in __IMAGE_TRANSLATION)
      path: String path of the given image image_key

    Kills:
      sys.exit: Invalid arugments

    Returns:
      A string containing the destination filename to use
    """
    if not path or not image_key or not GUID:
      sys.exit("%(debug)s__GetDestFilename] Invalid Arguments passed!\n"
               "%(debug)s__GetDestFilename] GUID: %(guid)s\n"
               "%(debug)s__GetDestFilename] image_key: %(key)s\n"
               "%(debug)s__GetDestFilename] PATH: %(path)s" % {
               'debug':self.__DEBUG_INFO,
               'guid':GUID,
               'key':image_key,
               'path':path})
    if image_key in self.__IMAGE_TRANSLATION:
      destination = (str(self.__db_library_id) + GUID + 
                     self.__IMAGE_TRANSLATION[image_key] + 
                     os.path.splitext(path)[1])
    else:
      sys.exit("%(debug)s__GetDestFilename] Translation key [%(key)s] does not "
               "exist!\n"
               "%(debug)s__GetDestFilename] Translation dictionary: %(dict)s" % 
               {'debug':self.__DEBUG_INFO,
               'key':image_key,
               'dict':self.__IMAGE_TRANSLATION})
    return destination

  def Run(self):
    """ Exports all the images in AlbumData that exist on the SQL server.

    Args:
      link: Boolean True to use symlinks in export directory, False to copy
    
    Kills:
      sys.exit: Fatal copy command error, bad arugments
    """
    count = 0
    total = len(self.__album_data.images)
    indicator = ProgressIndicator.ProgressIndicator()
    if not self.__quiet:
      print ("\nExporting images to %(path)s (%(num)s images):     " %
            {'path':self.__export['export_path'], 'num':total}),
    failed_images = []
    for image_key in self.__album_data.images:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
      image_data = self.__VerifyImageInDatabase(image_key)
      if image_data:
        if __debug__:
          print ("%(debug)sRun] Image location data: %(data)s" %
                 {'debug':self.__DEBUG_INFO,'data':image_data})
        for image_key in image_data:
          if image_key != "GUID":
            destination_file = (self.__export['export_path'] + 
                                self.__GetDestFilename(image_data['GUID'],
                                                       image_key, 
                                                       image_data[image_key]))
            if __debug__:
              print ("%(debug)sRun] Exporting %(data)s TO: %(dest)s" % {
                     'debug':self.__DEBUG_INFO,
                     'data':image_data[image_key],
                     'dest':destination_file})
            # try to copy files via symlinking or normal copy.  If it fails, add
            # it to a list to get re-processed with another command later
            if not self.__export['link']:
              try:
                shutil.copy(image_data[image_key].replace('\\',''),
                            destination_file)
              except Exception, e:
                if e.errno == 2:
                  failed_images.append({'source':image_data[image_key],
                                       'destination':destination_file})
                else:
                  sys.exit("%(debug)sRun] Export failed: %(error)s" % 
                           {'debug':self.__DEBUG_INFO,'error':e})
              if os.path.isfile(destination_file):
                if __debug__:
                  print "%sRun] Export succeeded!" % self.__DEBUG_INFO
              else:
                failed_images.append({'source':image_data[image_key],
                                     'destination':destination_file})
            else:
              try:
                os.symlink(image_data[image_key].replace('\\',''),
                           destination_file)
              except OSError, e:
                if e.errno == 17:
                  os.remove(destination_file)
                  try:
                    os.symlink(image_data[image_key].replace('\\',''),
                               destination_file)
                  except Exception, e:
                    sys.exit("%(debug)sRun] Export failed: %(error)s" %
                             {'debug':self.__DEBUG_INFO,'error':e})
                else:
                  failed_images.append({'source':image_data[image_key],
                                       'destination':destination_file})
    if failed_images:
      count = 0
      total = len(failed_images)
      print ("\nFailed to export %s images on first try; retrying with a "
             "slower, but more precise command:" % total)
      for image in failed_images:
        print ("RETRY: %(source)s TO %(dest)s" % 
               {'source':image['source'],'dest':image['destination']})
        try:
          failed_results = commands.getstatusoutput(
              "cp \"" + image['source'] + "\" \"" + image['destination'] + "\"")
        except Exception, e:
          sys.exit("%(debug)sRun] Fatal error exporting image: %(source)s to "
                   "%(dest)s.\n"
                   "%(debug)sRun] ERROR: %(error)s" % {
                   'debug':self.__DEBUG_INFO,
                   'source':image['source'],
                   'dest':image['destination'],
                   'error':e})
        if failed_results[0] != 0:
          print ("%(warn)sRun] Export of image %(source)s TO %(dest)s FAILED." %
                 {'warn':self.__WARNING_INFO,
                 'source':image['source'],
                 'dest':image['destination']})



if __name__ == "__main__":
  import MySql
  import album_data
  print "Testing Export Class with MySQL..."
  print "-->Generating AlbumData class from AlbumData.xml:"
  Album = album_data.AlbumData(iphoto_library="AlbumData.xml")
  print "-->DONE!\n"
  print "-->Connecting to MySQL database:"
  sql_connection = {'address':'localhost',
                    'username':'exhibit', 
                    'password':'exhibit',
                    'database':'website_database', 
                    'prepend':'exhibit_test_'}
  SQL = MySql.MySql(connection=sql_connection)
  print "-->DONE!"
  print "-->Uploading Image data to server:"
  exporter = Export(album_data=Album,
                    db=SQL,
                    export_options={'export_path':"/tmp/"},
                    quiet=False)
  exporter.Run()
  print "-->DONE!"
  print "\n\nTesting completeled successfully!\n\n"
