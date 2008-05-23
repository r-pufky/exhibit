#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
# Copyright 2008, Robert Pufky
# Exhibit - Commandline and Configfile parser Class
#
""" Command line options processor class for Exhibit

This handles all of the command line option processing, as well as providing 
basic input verification (such as locations, etc) for Exhibit.

Testing:
  This module can be tested  by running this file from the command line.  This 
  will catch any significant errors processing commad line options, though may 
  not catch the more subtle interactions.  exhibit.config, AlbumData.xml must
  exist in the current directory to test properly

Debugging:
  Removing the optimization flag (-OO) from this file will turn debugging on.

Attributes:
  Class ExhibitOptions: Processes and verifies command line options for Exhibit
"""
__author__ = "Robert Pufky (github.com/r-pufky)"
import os
import sys
import optparse
import ConfigParser



class ExhibitOptions(object):
  """ Processes and validates command line arguments and configuration files 
  
  This will process command line options for Exhibit, as well as the 
  configuration file and verify the specified options.  Command line options
  take precedence over configuration file preferences.
  
  Attributes:
    options: Dictionary containing processed and verified options
  """
  __author__ = "Robert Pufky (github.com/r-pufky)"
  __version__ = "1.0"

  def __init__(self, arguments):
    """ Initalizes ExhibitOptions, and runs verification of data.
    
    This will verify both command line options and config file options.
    
    Args:
      arguments: List of arugments to parse (sys.argv usually)
      
    Kills:
      sys.exit: If a fatal error is encountered
    """
    self.__DEBUG_INFO = "DEBUG:[ExhibitOptions."
    self.__WARNING_INFO = "WARNING:[ExhibitOptions."
    self.options = {}
    self.__parser = optparse.OptionParser()
    self.__config_file = ConfigParser.ConfigParser()    
    self.__ParseArgs(arguments)
    self.__ProcessConfigFile()

  def __ParseArgs(self, arguments):
    """ Builds help command, and processes/verifies arguments.
    
    Args:
      arguments: List of arugments to parse (sys.argv usually)
    
    Kills:
      ConfigParser.exit: Bad configuration options are passed
    """
    usage = """
        ./Exhibit.py [OPTIONS]
        
        Exhibit Version: %(version)s
        
        Processes an iPhoto Library, saving SQL data to a SQL server and then
        exports the encoded files to a local directory.  You should probably
        write a plugin for your favorite Gallery program to import them from
        there, or build your own that uses the resulting SQL  database.
        
        Options are loaded from the default location:
        
          [Exhibit Base Directory]/exhibit.config
          
        Options specified on the commandline override the default/configfile
        options.
        """ % {'version':self.__version__}
    self.__parser.set_usage(usage)
    self.__parser.add_option('-l','--library',metavar='FILE',dest='library',
        help="Specify a file for the iPhoto library.  Default file: "
        "~/Pictures/iPhoto Library/AlbumData.xml")
    self.__parser.add_option('-c','--config',metavar='FILE',dest='config',
        help="Alternate configuration file.  Default file:    [Exhibit Base "
        "Directory]/exhibit.config")
    self.__parser.add_option('-i','--link',action='store_true',dest='link',
        help="Forces export option to use symlinks instead of copying the file."
        "  If the symlink fails, attempts to copy the actual file to local "
        "directory.")
    self.__parser.add_option('-f','--force',action='store_true',dest='force',
        help="Forces the SQL database to be rebuilt.  THIS IS SQL DATA "
        "DESTRUCTIVE")
    self.__parser.add_option('-q','--quiet',action='store_true',dest='quiet',
        help="Disables all output, except ERRORS and WARNINGS.  Useful for "
        "cronjobs.")
    opts, args = self.__parser.parse_args(arguments)
    if __debug__:
      print ("%(debug)s__ParseArgs] options recieved: %(options)s" % 
             {'debug':self.__DEBUG_INFO,'options':opts})
    if not opts.quiet:
      self.options['quiet'] = False
    else:
      self.options['quiet'] = True
    if __debug__:
      print ("%(debug)s__ParseArgs] quiet set to: %(quiet)s" % 
             {'debug':self.__DEBUG_INFO,'quiet':self.options["quiet"]})
    if __debug__:
      print ("%(debug)s__ParseArgs] Upload after processing set to: %(upload)s"
             % {'debug':self.__DEBUG_INFO,'upload':self.options["upload"]})
    if not opts.force:
      self.options['force'] = False
    else:
      self.options['force'] = True
    if __debug__:
      print ("%(debug)s__ParseArgs] Force SQL database to be rebuilt: %(force)s"
             % {'debug':self.__DEBUG_INFO,'force':self.options['force']})
    if not opts.link:
      self.options['link'] = False
    else:
      self.options['link'] = True
    if __debug__:
      print ("%(debug)s__ParseArgs] link image exports: %(link)s" % 
             {'debug':self.__DEBUG_INFO,'link':self.options['link']})
    if not opts.library:
      self.options['library'] = os.path.expanduser(
          "~/Pictures/iPhoto Library/AlbumData.xml")
      self.options['no_library_argument'] = True
    else:
      self.options['library'] = os.path.expanduser(opts.library)
      self.options['no_library_argument'] = False
    if not os.path.exists(self.options['library']): 
      self.__parser.exit("Album data not found! %s" % self.options['library'])
    if __debug__:
      print ("%(debug)s__ParseArgs] library set to: %(library)s" % {
             'debug':self.__DEBUG_INFO,
             'library':self.options['library']})
    if not opts.config:
      self.options['config_file'] = sys.path[0] + "/exhibit.config"
    else:
      self.options['config_file'] = os.path.expanduser(opts.config)
    if not os.path.exists(self.options['config_file']):
      self.__parser.exit("Exhibit configuration file not found! %s" % 
                         self.options['config_file'])

  def __ProcessConfigFile(self):
    """ Processes a given configuration file for validatity.
    
    Kills:
      sys.exit: Error occurs processing the configuration file
    """
    if __debug__:
      print ("%s__ProcessConfigFile] Processing configuration file..." %
             self.__DEBUG_INFO)
    try:
      self.__config_file.read(self.options['config_file'])
    except:
      sys.exit(
          "%(debug)s__ProcessConfigFile] Could not open config file: %(file)s"
          % {'debug':self.__DEBUG_INFO,'file':self.options['config_file']})
    try:
      self.__config_file.options("sql")
      self.__config_file.options("library")
    except ConfigParser.NoSectionError, e:
      sys.exit("%(debug)s__ProcessConfigFile] %(error)s found in config file!" %
               {'debug':self.__DEBUG_INFO,'error':e})
    if self.options['no_library_argument']:
      try:
        if __debug__:
          print ("%s__ProcessConfigFile] switching to config file library..." %
                 self.__DEBUG_INFO)
        self.options['library'] = os.path.expanduser(
            self.__config_file.get("library","location"))
      except ConfigParser.NoOptionError, e:
        sys.exit(
            "%(debug)s__ProcessConfigFile] %(error)s found in config file.\n"
            "%(debug)s__ProcessConfigFile] Library argument not passed!" % {
            'debug':self.__DEBUG_INFO,
            'error':e})
      if not os.path.exists(self.options['library']): 
        self.__parser.exit("Album data not found! %s" % self.options['library'])
      if __debug__:
        print ("%(debug)s__ProcessConfigFile] library set to: %(library)s\n" %
               {'debug':self.__DEBUG_INFO,'library':self.options['library']})
    try:
      self.options['sql_address'] = self.__config_file.get('sql','address')
      self.options['sql_username'] = self.__config_file.get('sql','username')
      self.options['sql_password'] = self.__config_file.get('sql','password')
      self.options['sql_database'] = self.__config_file.get('sql','database')
      self.options['sql_type'] = self.__config_file.get('sql','type')
      self.options['sql_prepend'] = self.__config_file.get('sql','prepend')
      if __debug__:
        print ("%(debug)s__ProcessConfigFile] library set to: %(library)s" %
               {'debug':self.__DEBUG_INFO,'library':self.options['library']})
      self.options['export_path'] = self.__config_file.get('export','path')
      if (len(self.options['export_path']) != 
        self.options['export_path'].rfind(os.sep)+1):
        self.options['export_path'] += os.sep
        print ("%(warn)s__ProcessConfigFile] Export location sepeartor missing."
               "\n%(warn)s__ProcessConfigFile] Set: %(path)s" % {
               'warn':self.__WARNING_INFO,
               'path':self.options['export_path']})
      if not os.path.exists(self.options['export_path']):
        print ("%(warn)s__ProcessConfigFile] Export directory not found.\n"
               "%(warn)s__ProcessConfigFile] Attempting to create %(path)s..." %
               {'warn':self.__WARNING_INFO,'path':self.options['export_path']})
        try:
          os.mkdir(self.options['export_path'],0700)
          print "%s__ProcessConfigfile] Success!" % self.__WARNING_INFO
        except OSError, e:
          print ("%(warn)s__ProcessConfigFile] Failed creating directory.\n"
                 "%(warn)s__ProcessConfigFile] Disabling export.\n"
                 "%(debug)s__ProcessConfigFile] Error: %(error)s\n" % {
                 'debug':self.__DEBUG_INFO,
                 'warn':self.__WARNING_INFO,
                 'error':e})
          self.options['export'] = False
    except ConfigParser.NoOptionError, e:
      sys.exit(
          "%(debug)s__ProcessConfigFile] %(error)s not found in config file." %
          {'debug':self.__DEBUG_INFO,'error':e})
    if __debug__:
      print ("%(debug)s__ProcessConfigFile] Config options: %(option)s" % 
             {'debug':self.__DEBUG_INFO,'option':self.options})



if __name__ == "__main__":
  print "Testing ExhibitOptions Class...\n"
  print "-->Loading test options:"
  options = ExhibitOptions(
      ['./exhibit.py','-c','./exhibit.config','-l','./AlbumData.xml','-f']) 
  options = ExhibitOptions(
      ['./exhibit.py','-c','./exhibit.config','-l','./AlbumData.xml','-r'])       
  print "-->PASS!\n"
  print "\n\nTesting Completed Successfully!\n\n"
