#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
# Copyright 2008, Robert Pufky
# Exhibit - command line interface module
#
""" Commandline interface for Exhibit

Processes a iPhoto Library, uploading the resulting SQL database to a SQL
server, and optionally uploads resulting images VIA rsync over SSH to a
server, or optionally exports them to a directory for manual transfer.  You 
should probably write a plugin for your favorite Gallery program to import them 
from there, or build your own that uses the resulting SQL database.

Options are loaded from the default location:
[Exhibit Base Directory]/exhibit.config

Options specified on the commandline override the default/configfile options.

Run with a -h or --help for commandline options

Debugging:
  Removing the optimization flag (-OO) from this file will turn debugging on.

Attributes:
  Class Exhibit: Processes AlbumData according to commandline options
"""
__author__ = "Robert Pufky (github.com/r-pufky)"
import sys
sys.path.append(sys.path[0] + "/includes")
import album_data
import Export
import ProcessData
import ExhibitOptions



class Exhibit(object):
  """ Command line interface for Exhibit.
  
  Attributes:
    Run(): Runs Exhibit with given commandline options
  """
  __author__ = "Robert Pufky (github.com/r-pufky)"
  __version__ = "1.1"
  
  def __init__(self):
    """ Initalizes the command line interface object. """
    self.__DEBUG_INFO = "DEBUG:[Exhibit."
    self.__WARNING_INFO = "WARNING:[Exhibit."
    self.__TESTED_ALBUM_DATA_VERSION = "1.1"  
    self.__options = ExhibitOptions.ExhibitOptions(sys.argv).options

    if not self.__options['quiet']:
      print ("Checking configuration options, loading AlbumData, and connecting"
             " to SQL server...")
    if __debug__:
      print ("%(debug)s__init__] Loading SQL Module [%(sql)s] and connecting to"
             " database." % {
             'debug':self.__DEBUG_INFO,
             'sql':self.__options["sql_type"]})
    sql_connection = {'address':self.__options['sql_address'],
                      'username':self.__options['sql_username'], 
                      'password':self.__options['sql_password'], 
                      'database':self.__options['sql_database'],
                      'prepend':self.__options['sql_prepend']}
    # load the sql module, and initialize it with our connection information
    self.__sql_connector = (
        self.__ClassLoader(self.__options['sql_type'])(
            connection=sql_connection))
    if __debug__:
      print ("%(debug)s__init__] Loaded and connected to SQL server!\n"
             "%(debug)s__init__] Loading AlbumData..." % 
             {'debug':self.__DEBUG_INFO})
    self.__album_data = album_data.AlbumData(
        iphoto_library=self.__options['library'])
    if self.__album_data.__version__ != self.__TESTED_ALBUM_DATA_VERSION:
      print ("%(warn)s AlbumData version not tested!\n"
             "%(warn)s Possible data lost may occur!" % {
             'warn':self.__WARNING_INFO,
             'warn':self.__WARNING_INFO})
    if __debug__:
      print "%s__init__] Albumdata loaded!" % self.__DEBUG_INFO
    if self.__options['force']:
      print ("%s__init__] Forcing SQL database to be rebuilt." % 
             self.__WARNING_INFO)
      self.__sql_connector.DatabaseCheck(force=True)
      print "%s__init__] SQL database rebuilt." % self.__WARNING_INFO
    if __debug__:
      print "%s__init__] Loading data processor..." % self.__DEBUG_INFO
    self.__processor = ProcessData.ProcessData(album_data=self.__album_data, 
                                               db=self.__sql_connector,
                                               quiet=self.__options['quiet'])
    if __debug__:
      print "%s__init__] Loaded data processor!" % self.__DEBUG_INFO
    if not self.__options['quiet']:
      print "Options checked and loaded; SQL connection established."

  def __ClassLoader(self, file_name=None):
    """ Loads a given python file VIA the file basename.
    
    Returns a reference to the module's class, which can be used to then create
    a class instantiation.
    
    Args:
      module_name: String base filename (i.e. "MySql")
      
    Kills:
      sys.exit: file_name specified is not defined (not found)
      
    Returns:
      A reference to the class object, which then can be instantiated by normal
          pythonic means
    """
    if not file_name:
      sys.exit("%s__ClassLoader] file_name is not defined!" % self.__DEBUG_INFO)
    else:
      try:
        # imports the module manually, similiar to from module import *
        module_import = __import__(file_name, globals(), locals(), ['*'], -1)
      except Exception, e:
        print ("%(debug)s__ClassLoader] Module import error!\n %(error)s" % {
               'debug':self.__DEBUG_INFO,
               'error':e})
      class_reference = getattr(module_import, file_name)
      return class_reference

  def Run(self):
    """ Runs the command line interface options.
    
    Kills:
      sys.exit: Critical module errors
    """
    self.__processor.FullImport()
    self.__exporter = Export.Export(
        album_data=self.__album_data, 
        db=self.__sql_connector, 
        export_options={'export_path':self.__options['export_path'],
                        'link':self.__options['link']},
                        quiet=self.__options['quiet'])
    self.__exporter.Run()
    print "\n\nDone!"



if __name__ == "__main__":
  exhibit = Exhibit()
  exhibit.Run()
