#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
# Copyright 2008, Robert Pufky
# Exhibit - data processing Class
#
""" Data processing Class for Exhibit

Testing:
  Test cases are setup for a generic MySQL database.  Look at the test cases at
  the bottom of this class, and setup (or change) the connection information to
  your database to verify the test passes.  These tests REQUIRE that AlbumData
  and MySQL modules can be imported, and that an example AlbumData.xml file
  exists in the same directory.  All tests passed before releasing.

Debugging:
  Removing the optimization flag (-OO) from this file will turn debugging on.

Attributes:
  Class ProcessData: Inserts data from album_data to a SQL database
"""
from __future__ import division
__author__ = "Robert Pufky (github.com/r-pufky)"
import sys
import time
import ProgressIndicator



class ProcessData(object):
  """ Processes data for Exhibit; from AlbumData to the SQL connector
  
  Attributes:
    FullImport(): imports full AlbumData to SQL
    ProcessImages(): imports only images from AlbumData to SQL
    ProcessAlbums(): imports only albums from AlbumData to SQL
    ProcessRolls(): imports only rolls from AlbumData to SQL
  """
  __author__ = "Robert Pufky (github.com/r-pufky)"
  __version__ = "1.0"
  
  def __init__(self, album_data=None, db=None, quiet=False):
    """ Initalizes and prepares ProcessData for data processing

    This will setup internal pointers to album_data and SQL objects, as well as
    attempt to pull the current album_data's database ID from the server (it is
    created and pulled if it does not already exists).  
    
    This also prepares the data in album_data to be inserted into the database
    before any queries on the database are executed.
    
    Args:
      album_data: Dictionary from album_data processing
      db: A SQL query object with Close,DatabaseCheck,Insert,Update,Delete, 
          and Select functions
      quiet: Boolean True to suppress status messages, but not ERROR or WARNING 
          messages, False for full reporting
          
    Kills:
      sys.exit: Invalid arguments, iPhotoLibrary's DBID not retrievable
    """
    self.__DEBUG_INFO = "DEBUG:[ProcessData."
    if not album_data:
      sys.exit("%(debug)s__init__] AlbumData dict not provided!" % 
               {'debug':self.__DEBUG_INFO})
    if not db:
      sys.exit("%(debug)s__init__] SQL connector not provided!" %
               {'debug':self.__DEBUG_INFO})
    if not isinstance(quiet, bool):
      sys.exit("%(debug)s__init__] quiet option must be boolean!" %
               {'debug':self.__DEBUG_INFO})
    self.__album_data = album_data
    self.__db = db    
    self.__quiet = quiet
    self.__image_keywords = []
    self.__album_images = []
    self.__filters = []
    self.__keywords = []
    self.__keywords_dict = self.__album_data.properties['Keywords']
    del self.__album_data.properties['Keywords']
    self.__db_library_id = self.__db.Select(
        "iPhotoLibrary",
        {'Path':self.__album_data.properties['Path'],
        'ArchiveID':self.__album_data.properties['ArchiveID']},
        limit=1)
    if self.__db_library_id:
      self.__db_library_id = self.__db_library_id[0]['ID']
    else:
      self.__db.Insert("iPhotoLibrary",self.__album_data.properties)
      self.__db_library_id = self.__db.Select(
          "iPhotoLibrary",
          {'Path':self.__album_data.properties['Path'],
          'ArchiveID':self.__album_data.properties['ArchiveID']},
          limit=1)
      if self.__db_library_id:
        self.__db_library_id = self.__db_library_id[0]['ID']          
      else:
        sys.exit("%(debug)s__init__] Could not select iPhotoLibrary DBID." %
                 {'debug':self.__DEBUG_INFO})
    if not self.__quiet:
      print "Preparing data to be uploaded to SQL server..."
    for keyword_id in self.__keywords_dict:
      self.__keywords.append({'KeywordID':keyword_id,
                             'iPhotoLibraryID':self.__db_library_id,
                             'Keyword':self.__keywords_dict[keyword_id]})
    del self.__keywords_dict
    if not self.__quiet:
      print "--> Prepared properties."
    for image_key in self.__album_data.images:
      self.__album_data.images[image_key]['iPhotoLibraryID'] = (
          self.__db_library_id)
      self.__album_data.images[image_key]['OriginalDate'] = (
          self.__UnixEpochAsDateString(
          self.__album_data.images[image_key]['OriginalDate']))
      self.__album_data.images[image_key]['ImportDate'] = (
          self.__UnixEpochAsDateString(
          self.__album_data.images[image_key]['ImportDate']))
      if "ModifiedDate" in self.__album_data.images[image_key]:
        self.__album_data.images[image_key]['ModifiedDate'] = (
            self.__UnixEpochAsDateString(
            self.__album_data.images[image_key]['ModifiedDate']))
      if "RotationIsOnlyEdit" in self.__album_data.images[image_key]:
        self.__album_data.images[image_key]['RotationIsOnlyEdit'] = (
            int(self.__album_data.images[image_key]['RotationIsOnlyEdit']))
      if "Keywords" in self.__album_data.images[image_key]:
        for keyword in self.__album_data.images[image_key]['Keywords']:
          self.__image_keywords.append({'ImageID':image_key,
                                       'iPhotoLibraryID':self.__db_library_id,
                                       'KeywordID':keyword})
        del self.__album_data.images[image_key]['Keywords']
    if not self.__quiet:
      print "--> Prepared images."
    for album_key in self.__album_data.albums:
      self.__album_data.albums[album_key]['iPhotoLibraryID'] = (
          self.__db_library_id)
      if "Master" in self.__album_data.albums[album_key]:
        self.__album_data.albums[album_key]['Master'] = (
            int(self.__album_data.albums[album_key]['Master']))
      if "PlayMusic" in self.__album_data.albums[album_key]:
        self.__album_data.albums[album_key]['PlayMusic'] = (
            int(self.__album_data.albums[album_key]['PlayMusic']))
      if "RepeatSlideShow" in self.__album_data.albums[album_key]:
        self.__album_data.albums[album_key]['RepeatSlideShow'] = (
            int(self.__album_data.albums[album_key]['RepeatSlideShow']))
      if "SlideShowUseTitles" in self.__album_data.albums[album_key]:
        self.__album_data.albums[album_key]['SlideShowUseTitles'] = (
            int(self.__album_data.albums[album_key]['SlideShowUseTitles']))
      if "PanAndZoom" in self.__album_data.albums[album_key]:
        self.__album_data.albums[album_key]['PanAndZoom'] = (
            int(self.__album_data.albums[album_key]['PanAndZoom']))
      if "ShuffleSlides" in self.__album_data.albums[album_key]:
        self.__album_data.albums[album_key]['ShuffleSlides'] = (
            int(self.__album_data.albums[album_key]['ShuffleSlides']))
      for image in self.__album_data.albums[album_key]['KeyList']:
        self.__album_images.append({'iPhotoLibraryID':self.__db_library_id,
                                   'AlbumID':album_key,
                                   'ImageID':image})
      del self.__album_data.albums[album_key]['KeyList']
      if "Filters" in self.__album_data.albums[album_key]:
        for filter in self.__album_data.albums[album_key]['Filters']:
          self.__filters.append({'iPhotoLibraryID':self.__db_library_id,
                                'AlbumID':album_key,
                                'Count':filter['Count'],
                                'Operation':filter['Operation'],
                                'Type':filter['Type']})
        del self.__album_data.albums[album_key]['Filters']
    if not self.__quiet:
      print "--> Prepared albums."
    for roll_key in self.__album_data.rolls:
      self.__album_data.rolls[roll_key]['iPhotoLibraryID'] = (
          self.__db_library_id)
      self.__album_data.rolls[roll_key]['RollDate'] = (
          self.__UnixEpochAsDateString(
          self.__album_data.rolls[roll_key]['RollDate']))
      del self.__album_data.rolls[roll_key]['KeyList']
    if not self.__quiet:
      print "--> Prepared rolls."

  def __UnixEpochAsDateString(self, unix_time=None):
    """ Converts a unix timestamp into a datetime string
    
    This converts the UNIX EPOCH seconds to a standard date formate.  This is 
    required as the generic insert / update / delete statements wrap everything
    in quotes, which will cause a typical FROM_UNIXTIME(#) operation to fail.
    
    Args:
      unix_time: integer unix timestamp to convert
      
    Returns:
      A string timestamp in the format 'YYYY-MM-DD HH:MM:SS'
    """
    if not unix_time or not isinstance(unix_time, int):
      return "0000-00-00 00:00:00"
    else:
      return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unix_time))    

  def FullImport(self):
    """ Runs a full AlbumData to SQL import session.
    
    Automatically runs a complete import session for the given album.  This
    allows for an easy 'full' import, while also allowing individual sections to
    be imported if a future case exists.
    """
    self.ProcessImages()
    self.ProcessAlbums()
    self.ProcessRolls()

  def ProcessImages(self):
    """ Uploads image data/metadata to SQL database.
    
    This data includes building the Images, ImageKeywords and Keywords tables.

    Kills:
      sys.exit: Bad SQL statements
    """
    count = 0
    total = len(self.__album_data.images)
    indicator = ProgressIndicator.ProgressIndicator()
    if not self.__quiet:
      print "Uploading Image metadata to SQL server (%s images):     " % total,
    for image_key in self.__album_data.images:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
      db_image = self.__db.Select("Images",
                                  {'iPhotoLibraryID':self.__db_library_id,
                                  'ImageID':image_key},
                                  limit=1)
      if db_image:
        if __debug__:
          print ("%(debug)sProcessImages] Existing Image: %(key)s updating..." %
                 {'debug':self.__DEBUG_INFO,'key':image_key})
        self.__db.Update("Images",
                         {'iPhotoLibraryID':self.__db_library_id,
                         'ImageID':image_key},
                         self.__album_data.images[image_key])
      else:
        if __debug__:
          print ("%(debug)sProcessImages] New Image to add: %(key)s" % 
                 {'debug':self.__DEBUG_INFO,'key':image_key})
        self.__db.Insert("Images",self.__album_data.images[image_key])
    count = 0
    total = len(self.__image_keywords)
    if not self.__quiet:
      print ("\nUploading Image Keyword pair metadata to SQL server "
             "(%s pairs):     " % total),
    self.__db.ResetTable("ImageKeywords")
    self.__db.ResetTable("Keywords")
    for image_keyword in self.__image_keywords:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
      self.__db.Insert("ImageKeywords",image_keyword)
    count = 0
    total = len(self.__keywords)
    if not self.__quiet:
      print ("\nUploading Keyword metadata to SQL server (%s keywords):     " %
             total),
    for keyword in self.__keywords:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
        self.__db.Insert("Keywords",keyword)

  def ProcessAlbums(self):
    """ Uploads album data/metadata to SQL database.

    This data includes building the Albums, AlbumImages, and Filters tables.
    
    Kills:
      sys.exit: Bad SQL statements
    """
    count = 0
    total = len(self.__album_data.albums)
    indicator = ProgressIndicator.ProgressIndicator()
    if not self.__quiet:
      print ("\nUploading Album metadata to SQL server (%s albums):     " %
             total),
    for album_key in self.__album_data.albums:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
      db_album = self.__db.Select("Albums",
                                  {'iPhotoLibraryID':self.__db_library_id,
                                  'AlbumID':album_key},
                                  limit=1)
      if db_album:
        if __debug__:
          print ("%(debug)sProcessAlbums] Existing Album: %(key)s updating..." %
                 {'debug':self.__DEBUG_INFO,'key':album_key})
        self.__db.Update("Albums",
                         {'iPhotoLibraryID':self.__db_library_id,
                         'AlbumID':album_key},
                         self.__album_data.albums[album_key])
      else:
        if __debug__:
          print ("%(debug)sProcessAlbums] New Album to add: %(key)s" %
                 {'debug':self.__DEBUG_INFO,'key':album_key})
        self.__db.Insert("Albums",self.__album_data.albums[album_key])
    count = 0
    total = len(self.__album_images)
    if not self.__quiet:
      print ("\nUploading Album Image metadata to SQL server (%s Album Images)"
             ":     " % total),
    self.__db.ResetTable("AlbumImages")
    self.__db.ResetTable("Filters")
    for album_image in self.__album_images:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
      self.__db.Insert("AlbumImages",album_image)
    count = 0
    total = len(self.__filters)
    if not self.__quiet:
      print ("\nUploading Album Filter metadata to SQL server (%s Filters):"
             "     " % total),
    for filter in self.__filters:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
      self.__db.Insert("Filters",filter)

  def ProcessRolls(self):
    """ Uploads album data/metadata to SQL database.

    Kills:
      sys.exit: Bad SQL statements
    """
    count = 0
    total = len(self.__album_data.rolls)
    indicator = ProgressIndicator.ProgressIndicator()
    if not self.__quiet:
      print "\nUploading Roll metadata to SQL server (%s rolls):     " % total,
    for roll_key in self.__album_data.rolls:
      if not self.__quiet:
        count += 1
        indicator.Tick(int(count/total*100))
      db_roll = self.__db.Select("Rolls",
                                 {'iPhotoLibraryID':self.__db_library_id,
                                 'RollID':roll_key},
                                 limit=1)
      if db_roll:
        if __debug__:
          print ("%(debug)sProcessRolls] Existing Roll: %(key)s updating..." % {
                 'debug':self.__DEBUG_INFO,
                 'key':roll_key})
        self.__db.Update("Rolls",
                         {'iPhotoLibraryID':self.__db_library_id,
                         'RollID':roll_key},
                         self.__album_data.rolls[roll_key])
      else:
        if __debug__:
          print ("%(debug)sProcessRolls] New Roll to add: %(key)s" % {
                 'debug':self.__DEBUG_INFO,
                 'key':roll_key})
        self.__db.Insert("Rolls",self.__album_data.rolls[roll_key])



if __name__ == "__main__":
  import MySql
  import album_data
  print "Testing ProcessData Class with MySQL..."
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
  print "-->DONE!\n"
  print "-->Forcing Complete Rebuild of Database:"
  SQL.DatabaseCheck(force=True)
  print ("-->DONE!\n")
  print "-->Creating new Data Procssor with AlbumData and SQL connection:"
  processor = ProcessData(album_data=Album,db=SQL,quiet=False)
  print "-->PASS!\n"
  print "-->Running Process data on a fresh database:"
  processor.FullImport()
  print "-->PASS!\n"
  print "-->Running Process data on a populated database:"
  processor.FullImport()
  print "-->PASS!\n"
  print "\n\nTesting completeled successfully!\n\n"
