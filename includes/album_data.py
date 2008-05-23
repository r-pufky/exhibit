#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
# Copyright 2008, Robert Pufky
# iPhoto AlbumData.xml module for python
#
""" Processes and stores a given iPhoto Library in an object

Processes a given AlbumData.xml file from iPhoto and stores it in the 
instantiated AlbumData class.  Data is stored as easy to use dict's, and can be
retrieved from this class.

Testing:
  This module can be tested  by running this file from the command line, with an
  existing AlbumData.xml file in the same (current) directory.  This will catch
  any significant errors reading an AlbumData.xml file, though may not catch the
  more subtle interactions.

Debugging:
  Removing the optimization flag (-OO) from this file will turn debugging on.

Attributes:
  Class AlbumData: Processes and Holds a given AlbumData.xml file
"""
__author__ = "Robert Pufky (github.com/r-pufky)"
import os
import sys
import plistlib



class AlbumData(object):
  """ Stores iPhoto's AlbumData.xml file as easy to use dictionaries.

  Processes a given AlbumData.xml file from iPhoto, and stores / cleans data in
  an easy to use dictionary format.  A more in-depth explanation of each 
  attribute is listed below the attributes section.  Please note that NOT ALL 
  dictionary entries are guaranteed to exist; you should check to make sure a 
  key exists before using it.
  
  Apple Terminology:
    Rolls: iPhoto's EVENTS.  These can be considered the album for most people.
    Albums: iPhoto's categories on the leftside.  You probably want ROLLS.
    Images: Not really.  These are just data.  They can be movies, images, etc.

  Attributes:
    properties: Dictionary iPhotoLibrary's properties
    rolls: Dictionary of dictionaries of iPhotoLibrary's Roll information
    albums: Dictionary of dictionaries of iPhotoLibrary's Album information
    images: Dictionary iPhotoLibrary's image information
    GetUnixEpochTime(): Converts Apple Timer to standard UNIX time

  Properties dictionary:
    MinorVersion: Integer AlbumData minor version
    MajorVersion: Integer AlbumData major version
    Keywords: Dictionary all keywords used in this iPhoto Library
    Path: String full path to the iPhoto Library
    iPhotoVersion: String iPhoto version
    ArchiveID: Integer iPhoto's interal library ID (in case there are
        multiple libraries used for that iPhoto application)
    
    i.e.:
      {'MinorVersion':2, 
       'MajorVersion':0,
       'Keywords':{'1':'family','2':'fun'},
       'Path':'/Users/me/iPhoto Library',
       'iPhotoVersion':'7.1.3 (364)',
       'ArchiveID':1}
    
  Rolls dictionary:
    RollID: Integer ID of the roll for current iPhoto Library
    KeyList: List of image ID's that are in the roll
    RollName: String user's name for the roll
    PhotoCount: Integer number of Images in an album
    KeyPhoto: Integer image ID for the album's cover photo
    RollDateAsAppleTimer: Floatdate the roll was made (Apple Timer)
    RollDate: Integer date the roll was made (UNIX EPOCH)
    
    i.e.:
      {
       'N':{...},
       'N+1':{'RollID':1,
              'KeyList':['1','2','3'],
              'RollName':'Example Event Title',
              'PhotoCount':3,
              'KeyPhoto':2,
              'RollDateAsAppleTimer':107292766.000000,
              'RollDate':1085599966},
       'N+2':{...}
      }

  Albums dictionary:
    AlbumID: Integer ID of album for current iPhoto Library
    AlbumName: String user's name for the album
    KeyList: List of image ID's that are in the album
    AlbumType: String description of the type of the album
    FilterMode: String type of filter being used on the album
    Filters: List of dictionaries of the filters used on the album,
        stored as {Count, Operation, Type}
    Master: Boolean True if album is the master album, False otherwise
    GUID: String unique iPhoto ID of the album, in the format
        XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    PhotoCount: Integer number of Images in the album
    PlayMusic: Boolean True if music is played during an iPhoto slideshow
    RepeatSlideShow: Boolean True if iPhoto loops slideshow
    SecondsPerSlide: Integer number of seconds to show each slide on slideshow
    SlideShowUseTitles: Boolean True if titles are shown during a slideshow
    SongPath: String full path to music file to play during slideshow
    TransitionDirection: Integer number representing direction slides move
    TransitionName: String type of transition to use (i.e. Dissolve)
    TransitionSpeed: Float length of time for transition in number of seconds
        and fractions of a second
    PanAndZoom: Boolean True if the photo should be panned/zoomed on a slideshow
    ShuffleSlides: Boolean True if Images should be shuffled during a slideshow
    
    i.e.:
      {
       'N':{...},
       'N+1':{'AlbumID':1,
              'AlbumName':"Example Album Name",
              'KeyList':['1','2','3'],
              'AlbumType':"auto-generated",
              'FilterMode':"All",
              'Filters':[{...},
                         {'Count':0, 'Operation':"In Key List", 'Type':"Roll"},
                         {...}]
              'Master':True,
              'GUID':"EEBF1D90-7A64-49F7-A49E-0925D1BBEF50",
              'PhotoCount':3,
              'PlayMusic':True,
              'RepeatSlideShow':True,
              'SecondsPerSlide':3,
              'SlideShowUseTitles':True,
              'SongPath':
                "/Applications/iPhoto.app/Contents/Music/Minuet in G.mp3",
              'TransitionDirection':0,
              'TransitionName':"Dissolve",
              'TransitionSpeed':1.0,
              'PanAndZoom':True,
              'ShuffleSlides':False},
       'N+2':{...}
      }
 
  Images dictionary:
    GUID: String unique iPhoto ID of the image, in the format
        XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    RollID: Integer roll ID that this image belongs to
    ImageID: Integer iPhoto ID for this image
    Rating: Integer user's rating of the image
    Comment: String comments on the image
    Caption: String original image name
    MediaType: String type of image media (i.e. Image, Video, etc)
    AspectRatio: Float aspect ratio of the picture
    RotationIsOnlyEdit: Boolean True if this was the only change to the image
    OriginalDate: Integer date image was taken (UNIX EPOCH)
    OriginalDateAsAppleTimer: Float date image was taken (Apple Timer)
    ModifiedDate: Integer date the image was modified (UNIX EPOCH)
    ModifiedDateAsAppleTimer: Float date image was modified (Apple Timer)
    ImportDate: Integer date the image was added (UNIX EPOCH)
    ImportDateAsAppleTimer: Float date image was added (Apple Timer)
    ThumbPath: String full path to the thumbnail image
    ImagePath: String full path to the current 'fullsized' image
        (this is the modified image, or the original video file, etc)
    OriginalPath: String full path to the original image, if the image was 
        modified by iPhoto.  If it was not modified, this is not used, instead
        ImagePath is used.
    Keywords: List of Keyword ID's from the iPhoto Library (see properties)
    
    i.e.:
      {
       {...},
       {'GUID':"A91BD448-2DA1-48AA-920F-086290E15EC4",
        'RollID':1,
        'ImageID':1,
        'Rating':5,
        'Comment':"This is a great pic.",
        'Caption':"IMG_2671",
        'MediaType':"Image",
        'AspectRatio':1.32635,
        'RotationIsOnlyEdit':False,
        'OriginalDate':1172814275,
        'OriginalDateAsAppleTimer':194507075.39234,
        'ModifiedDate':1185143002,
        'ModifiedDateAsAppleTimer':206835802.21532,
        'ImportDate':1209069601,
        'ImportDateAsAppleTimer':230762401.31222,
        'ThumbPath':"/Users/me/iPhoto Library/Data/2007/me/IMG_267.jpg",
        'ImagePath':"/Users/me/iPhoto Library/Modified/me/IMG_267.jpg",
        'OriginalPath':"/Users/me/iPhoto Library/Originals/me/IMG_267.jpg",
        'Keywords':['1','2','3']},
       {...}
      }
  """
  __author__ = "Robert Pufky (github.com/r-pufky)"
  __version__ = "1.1"
  
  def __init__(self, iphoto_library=None):
    """ Initalizes AlbumData with a given iPhoto AlbumData.xml file.
    
    Args:
      iphoto_library: String path to an iPhoto AlbumData.xml file, defaults to 
          current users default iPhoto library
      
    Raises:
      SyntaxError: Invalid arguments specified
      EnvironmentError: Library could not be opened/loaded
    """
    self.__DEBUG_INFO = "DEBUG:[AlbumData."
    self.__WARNING_INFO = "WARNING:[AlbumData."
    self.__TESTED_VERSION = {'major': ['7', '1', '5'], 'minor': '378'}
    self.__UNIX_EPOCH_ADJUSTMENT = 978307200
    self.__library = None
    self._library_version = {}
    self.rolls = None
    self.albums = None
    self.images = None
    self.properties = None
    self.Load(iphoto_library)

  def __ConvertBoolean(self, key=None):
    """ Converts any given iPhoto Library boolean type to True or False
    
    Sets a boolean attribute from any iPhoto Library boolean datatype.  Will 
    always return False if no value is passed, or if value cannot be identified.
    
    Args:
      boolean/string: iPhoto boolean value to convert
    Returns:
      The converted boolean value
    """
    if not key:
      return False
    
    if key == "YES" or key == True or key == 1:
      return True
    else:
      print ("%(warn)s__ConvertBoolean] Not a valid iPhoto boolean, returning "
             "False." % {'warn':self.__WARNING_INFO})
      return False

  def GetUnixEpochTime(self, timer=0):
    """ Converts a given apple timer interval to the UNIX EPOCH standard.

    Apple stores datetimes in iPhoto as the number of seconds that have occurred
    since 2001/1/1 (which I will call the Apple EPOCH).  This number includes a
    decimal value as well, which indicates fractions of a second.  This is not
    converted as the UNIX EPOCH does not have that time resolution.  Apple EPOCH
    stores previous dates (i.e. pre-2001) as negative negative number.
    
    Number of seconds from UNIX EPOCH to Apple EPOCH = 978307200
    UNIX EPOCH conversion = 978307200 + Apple Timer, cast to an integer.
    
    Args:
      timer: integer/float/string, the Apple timer to convert
      
    Returns:
      Integer UNIX EPOCH time
    """
    return int(self.__UNIX_EPOCH_ADJUSTMENT + timer)

  def CompareLibraryVersion(self, version_string):
    """ Compares major version album data information.
    
    Args:
      version_string: String version of album data to test.
    
    Returns:
      A boolean True if the major versions match, False otherwise.
    """
    major_version, minor_version = version_string.split(' ')
    self._library_version['major'] = major_version.split('.')
    self._library_version['minor'] = minor_version.strip('()')
    if self._library_version['major'] == self.__TESTED_VERSION['major']:
      if self._library_version['minor'] != self.__TESTED_VERSION['minor']:
        print ("%(warn)sCompareLibraryVersion] Possible data lost may occur!\n"
            "%(warn)sCompareLibraryVersion] --> Current Version: '%(app)s' \n"
            "%(warn)sCompareLibraryVersion] --> Supported Version: '%(test)s'" %
            {'warn': self.__WARNING_INFO,
             'app': self._library_version,
             'test': self.__TESTED_VERSION})
      return True
    else:
      print ("%(debug)sCompareLibraryVersion] IMCOMPATABLE VERSIONS.\n"
          "%(debug)sCompareLibraryVersion] --> Current Version: '%(app)s' \n"
          "%(debug)sCompareLibraryVersion] --> Supported Version: '%(test)s'" %
          {'debug': self.__DEBUG_INFO,
           'app': self._library_version,
           'test': self.__TESTED_VERSION})
      return False

  def Load(self, iphoto_library):
    """ Loads or reloads the object with the given album data file
    
    Current data existing in the object will be destroyed.
    
    Args:
      iphoto_library: String path to an iPhoto AlbumData.xml file, defaults to 
          current users default iPhoto library.
      
    Raises:
      SyntaxError: Invalid arguments specified
      EnvironmentError: Library could not be opened/loaded
    """
    if __debug__:
      print "%sLoad] Resetting internal variables" % self.__DEBUG_INFO

    if self.__library:
      del self.__library
    self.__library = {}
    if self.rolls:
      del self.rolls
    self.rolls = {}
    if self.albums:
      del self.albums
    self.albums = {}
    if self.images:
      del self.images
    self.images = {}
    if self.properties:
      del self.properties
    self.properties = {}

    if not iphoto_library:
      self.__library_location = os.path.expanduser(
          "~/Pictures/iPhoto Library/AlbumData.xml")
    elif not os.path.exists(iphoto_library):
      raise SyntaxError("AlbumData.xml file cannot be found!\nLibrary Location:"
                        " %s" % iphoto_library)
    else:
      self.__library_location = iphoto_library
    if __debug__:
      print ("%(debug)sLoad] Library Location set to: %(location)s\n"
             "%(debug)sLoad] Loading %(location)s..." % {
             'debug':self.__DEBUG_INFO, 
             'location':self.__library_location})
    try:
      self.__library = plistlib.readPlist(self.__library_location)
    except Exception, e:
      raise EnvironmentError("%sLoad] Could not load Library file!" %
                             self.__DEBUG_INFO)
    if __debug__:
      print "%sLoad] File loaded." % self.__DEBUG_INFO
    if not self.CompareLibraryVersion(self.__library['Application Version']):
      raise EnvironmentError('Incompatable version detected.')
    self.properties['MinorVersion'] = self.__library['Minor Version']
    self.properties['MajorVersion'] = self.__library['Major Version']
    self.properties['Keywords'] = self.__library['List of Keywords']
    self.properties['Path'] = self.__library['Archive Path']
    self.properties['iPhotoVersion'] = self.__library['Application Version']
    self.properties['ArchiveID'] = self.__library['ArchiveId']
    if __debug__:
      print "%sLoad] Loaded album preferences." % self.__DEBUG_INFO
    for roll in self.__library['List of Rolls']:
      self.rolls[roll['RollID']] = roll
      if 'RollDateAsTimerInterval' in roll:
        self.rolls[roll['RollID']]['RollDate'] = (
            self.GetUnixEpochTime(roll['RollDateAsTimerInterval']))
        self.rolls[roll['RollID']]['RollDateAsAppleTimer'] = (
            roll['RollDateAsTimerInterval'])
        del self.rolls[roll['RollID']]['RollDateAsTimerInterval']
      if 'KeyPhotoKey' in roll:
        self.rolls[roll['RollID']]['KeyPhoto'] = roll['KeyPhotoKey']
        del self.rolls[roll['RollID']]['KeyPhotoKey']
    if __debug__:
      print "%sLoad] Loaded rolls." % self.__DEBUG_INFO
    for album in self.__library['List of Albums']:
      self.albums[album['AlbumId']] = album
      if "Filter Mode" in album:
        self.albums[album['AlbumId']]['FilterMode'] = album['Filter Mode']
        del self.albums[album['AlbumId']]['Filter Mode']
      if "Album Type" in album:
        self.albums[album['AlbumId']]['AlbumType'] = album['Album Type']
        del self.albums[album['AlbumId']]['Album Type']
      if "Master" in album:
        self.albums[album['AlbumId']]['Master'] = (
            self.__ConvertBoolean(album['Master']))
      if "PlayMusic" in album:
        self.albums[album['AlbumId']]['PlayMusic'] = (
            self.__ConvertBoolean(album['PlayMusic']))
      if "RepeatSlideShow" in album:
        self.albums[album['AlbumId']]['RepeatSlideShow'] = (
            self.__ConvertBoolean(album['RepeatSlideShow']))
      if "SlideShowUseTitles" in album:
        self.albums[album['AlbumId']]['SlideShowUseTitles'] = (
            self.__ConvertBoolean(album['SlideShowUseTitles']))
      if "PanAndZoom" in album:
        self.albums[album['AlbumId']]['PanAndZoom'] = (
            self.__ConvertBoolean(album['PanAndZoom']))
      if "ShuffleSlides" in album:
        self.albums[album['AlbumId']]['ShuffleSlides'] = (
            self.__ConvertBoolean(album['ShuffleSlides']))
      if "AlbumId" in album:
        self.albums[album['AlbumId']]['AlbumID'] = album['AlbumId']
        del self.albums[album['AlbumId']]['AlbumId']
    if __debug__:
      print "%sLoad] Loaded albums." % self.__DEBUG_INFO
    for image in self.__library['Master Image List']:
      self.images[int(image)] = self.__library['Master Image List'][image]
      if "DateAsTimerInterval" in self.images[int(image)]:
        self.images[int(image)]['OriginalDate'] = self.GetUnixEpochTime(
            self.images[int(image)]['DateAsTimerInterval'])
        self.images[int(image)]['OriginalDateAsAppleTimer'] = (
            self.images[int(image)]['DateAsTimerInterval'])
        del self.images[int(image)]['DateAsTimerInterval']
      if "ModDateAsTimerInterval" in self.images[int(image)]:
        self.images[int(image)]['ModifiedDate'] = self.GetUnixEpochTime(
            self.images[int(image)]['ModDateAsTimerInterval'])
        self.images[int(image)]['ModifiedDateAsAppleTimer'] = (
            self.images[int(image)]['ModDateAsTimerInterval'])
        del self.images[int(image)]['ModDateAsTimerInterval']
      if "MetaModDateAsTimerInterval" in self.images[int(image)]:
        self.images[int(image)]['ImportDate'] = self.GetUnixEpochTime(
            self.images[int(image)]['MetaModDateAsTimerInterval'])
        self.images[int(image)]['ImportDateAsAppleTimer'] = (
            self.images[int(image)]['MetaModDateAsTimerInterval'])
        del self.images[int(image)]['MetaModDateAsTimerInterval']
      if "Roll" in self.images[int(image)]:
        self.images[int(image)]['RollID'] = self.images[int(image)]['Roll']
        del self.images[int(image)]['Roll']
      if "Aspect Ratio" in self.images[int(image)]:
        self.images[int(image)]['AspectRatio'] = (
            self.images[int(image)]['Aspect Ratio'])
        del self.images[int(image)]['Aspect Ratio']
      if "RotationIsOnlyEdit" in self.images[int(image)]:
        self.images[int(image)]['RotationIsOnlyEdit'] = self.__ConvertBoolean(
            self.images[int(image)]['RotationIsOnlyEdit'])
      self.images[int(image)]['ImageID'] = int(image)
    if __debug__:
      print "%sLoad] Loaded images." % self.__DEBUG_INFO
    del self.__library



if __name__ == '__main__':
  print "Testing AlbumData Class...\n"
  print "-->Testing AlbumData class creation:"
  album_test = AlbumData(iphoto_library="AlbumData.xml")
  print "-->PASS!\n"
  print "-->Test Images retrieval:"
  print "Images: %s" % album_test.images
  print "-->PASS!\n"
  print "-->Test Rolls retrieval:"
  print "Rolls: %s" % album_test.rolls
  print "-->PASS!\n"
  print "-->Test Albums retrieval:"
  print "Albums: %s" % album_test.albums
  print "-->PASS!\n"
  print "-->Test Properties retrieval:"
  print "Properties: %s" % album_test.properties
  print "-->PASS!\n"
  print "-->Test AlbumData version/author retrieval:"
  print "AlbumData Version: %s" % album_test.__version__
  print "AlbumData Author: %s" % album_test.__author__
  print "-->Test Version retrieval: PASS!\n"
  print "\n\nTesting completeled successfully!\n\n"
