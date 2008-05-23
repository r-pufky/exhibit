#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
# Copyright 2008, Robert Pufky
# Exhibit - SQL Database Connector Class Template
#
""" SQL database connector class for Exhibit

This supports all of the SQL operations needed by Exhibit to correctly interact
with a SQL database.  Nuances from generic SQL commands to SQL commands are
dealth with automatically in this class.  Your SQL server MUST SUPPORT UTF8,
otherwise execution will be halted on unsupported characters.

SQL Setup Notes:
  SQL is not included with python, which means you will have to install it on
  your system for this class to work.  If you are receiving SQLdb import 
  errors, read the documentation at docs/SQL_setup.txt for information on how 
  to setup this module.

Warnings:
  SQLdb warnings are disabled, as we are catching them.  Removing this filter
  will make your output *much* more spewy.  This can be done by inserting the
  following line after including the SQL Class:
  
    warnings.resetwarnings()

Testing:
  This module can be tested by running this file from the command line.  This 
  will catch any significant errors with interactions on your particular SQL
  server.  Test cases are setup for a generic SQL database.  Look at the test 
  cases at the bottom of this class, and change the connection information to
  your database to verify the test passes.

Debugging:
  Removing the optimization flag (-OO) from this file will turn debugging on.

Attributes:
  Class SQL: Provides a SQL interface for Exhibit
"""
__author__ = "Robert Pufky (github.com/r-pufky)"
import sys
import SQLdb
import warnings
warnings.filterwarnings("ignore",".*")



class SQL(object):
  """ Provides a SQL interface for Exhibit.
  
  This provides basically SQL functionality to be used on a SQL server.  The
  SQL interface is generic, where the specific nuances for SQL are taken care
  of by this module before issuing the SQL statement.
  
  Attributes:
    Close(): Closes the SQL connection if opened
    CheckTableExists(): Checks if a given table exists in the database
    ResetTable(): Clears out all table rows
    CreateTable(): Creates a SQL table in the database
    EncodeString(): Escapes special DB characters, and encodes string to UTF8
    DatabaseCheck(): Checks to see if Exhibit tables exist in the database
    Insert(): Inserts a new row into a database table
    Update(): Updates (or creates) a row in a database table
    Select(): Selects row(s) from a database table
    Delete(): Deletes a matched row from a database table
  """
  __author__ = "Robert Pufky (github.com/r-pufky)"
  __version__ = "1.0"
  
  def __init__(self, connection=None):
    """ Initializes and stores SQL database connection to a server.
    
    Information passed to initalize the connection is not stored in the object 
    except for the table prepend information.  The database specified is 
    automatically populated with the exhibit database schema - it is not 
    over-written if it already exists.
    
    Args:
      connection: Dictionary with connection information:
          {'address'  - address of server (IP or DNS)
           'username' - username to connect to SQL server with
           'password' - password to connect to SQL server with
           'database' - database to connect on SQL server
           'prepend'} - prepend string to use for all tables created

    Kills:
      sys.exit: Bad connection attempts
    """
    self.__db = None
    self.__prepend = None
    self.__DEBUG_INFO = "DEBUG:[SQL."
    self.__WARNING_INFO = "WARNING:[SQL."
    self.__RETURN_ALL_ROWS = 0
    self.__RETURN_DICT_FORMAT = 1
    self.__DB_ESCAPE_CHARS = ['"','%']
    if not connection:
      sys.exit("%(debug)s__init__] SQL connection information not provided!" %
               {'debug':self.__DEBUG_INFO})
    if __debug__:
      print ("%(debug)s__init__] SQL connection information: %(connection)s" %
             {'debug':self.__DEBUG_INFO,'connection':connection})
    try:
      self.__db = SQLdb.connect(host=connection['address'],
                                  user=connection['username'],
                                  passwd=connection['password'],
                                  db=connection['database'])
      self.__db.query("SET NAMES UTF8")
      self.__prepend = connection['prepend']
      del connection
      if __debug__:
        print ("%(debug)s__init__] SQL connection created successfully!" % 
               {'debug':self.__DEBUG_INFO})
    except SQLdb.Error, e:
      sys.exit("%(debug)s__init__] SQL ERROR: %(error)s\n"
               "%(debug)s__init__] SQL database connection error." %
               {'debug':self.__DEBUG_INFO,'error':e})
    self.DatabaseCheck(force=False)
  
  def __del__(self):
    """ Runs any cleanup needed when object is deleted. """
    self.Close()
  
  def Close(self):
    """ Closes the SQL connection if opened. """
    if self.__db:
      self.__db.commit()
      if __debug__:
        print ("%(debug)sClose] Committed database changes." % 
               {'debug':self.__DEBUG_INFO})
      self.__db.close()
      if __debug__:
        print ("%(debug)sClose] Closed database connection." % 
               {'debug':self.__DEBUG_INFO})

  def CheckTableExists(self, table=None):
    """ Checks to see if a table exists in the database.
    
    Restricts query to only tables matching the prepend string.
    
    Args:
      table: String table to check (without prepend characters)
      
    Returns:
      A boolean True if table exists, False otherwise
    """
    if not table:
      return False
    self.__db.query("SHOW TABLES LIKE '%s%%'" % self.__prepend)
    rows = self.__db.store_result()
    for row in rows.fetch_row(maxrows=self.__RETURN_ALL_ROWS):
      if row[0] == "%s%s" % (self.__prepend, table):
        return True
    else:
      return False

  def ResetTable(self, table=None):
    """ Clears out all rows of a table, if it the table exists.
    
    This automatically runs CheckTableExists, and will clear the table if it
    exists; does not change the column labels (if they are outdated).
    
    Args:
      table: String table to check (without prepend characters)
    
    Returns:
      A boolean True if successful, False otherwise
    """
    if not table or not self.CheckTableExists(table):
      return False
    self.__db.query("TRUNCATE TABLE %s%s" % (self.__prepend, table))
    return True

  def CreateTable(self, query=None, readable_name=None):
    """ Creates a SQL table in the database.
    
    Args:
      query: String SQL query to use to create the table
      readable_name: String human readable name to use if debugging
    
    Raises:
      SQLdb.Error: Table creation failed
    """
    self.__db.query(query)
    if __debug__:
      print ("%(debug)sDatabaseCheck] Created table %(pre)s%(name)s" % {
            'debug':self.__DEBUG_INFO,
            'pre':self.__prepend,
            'name':readable_name})
            
  def EncodeString(self, string_data=None):
    """ Escapes special DB characters, and encodes string to UTF8.
    
    This is automatically run before executing any SQL command.
    
    Args:
      string_data: String data to escape

    Raises:
      UnicodeEncodeError: UTF8 encoding is not supported

    Returns:
      String escaped string, or original value if not a string
    """
    if string_data:
      # check to see if the data passed is a string that can be worked on, then
      # escape SQL characters, and convert string to UTF8
      if isinstance(string_data, str) or isinstance(string_data, unicode):
        for escapee in self.__DB_ESCAPE_CHARS:
          string_data = string_data.replace(escapee,"\%s" % escapee)
        string_data = string_data.encode("UTF8")
        if __debug__:
          print ("%(debug)sEncodeString] converted: %(string)s" % 
                 {'debug':self.__DEBUG_INFO,'string':string_data})
    return string_data
  
  def DatabaseCheck(self, force=False):
    """ Checks to see if the database tables for Exhibit exist already.
    
    If they don't exist, they are created.  If the force option is specified, it
    will drop the tables that exist before re-creating them.
    
    Args:
      force: Boolean True if forcing re-creation of tables (DATA DESTRUCTIVE)
      
    Kills:
      sys.exit: Table creation fails on the database
    """
    if force:
      try:
        if __debug__:
          print ("%(debug)sDatabaseCheck] Force option specified, dropping "
                 "tables..." % {'debug':self.__DEBUG_INFO})
        self.__db.query("SHOW TABLES LIKE '%s%%'" % self.__prepend)
        rows = self.__db.store_result()
        for row in rows.fetch_row(maxrows=self.__RETURN_ALL_ROWS):
          self.__db.query("DROP TABLE IF EXISTS %s" % row[0])
          print ("%(warn)sDatabaseCheck] Dropped table %(table)s" % 
                 {'warn':self.__WARNING_INFO,'table':row[0]})
      except SQLdb.Error, e:
        sys.exit("%(debug)sDatabaseCheck] SQL ERROR: %(error)s\n"
                 "%(debug)sDatabaseCheck] SQL database error: cannot drop "
                 "tables." % {'debug':self.__DEBUG_INFO,'error':e})
    try:
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %siPhotoLibrary "
          "(ID INT NOT NULL AUTO_INCREMENT, "
          "ArchiveID INT NOT NULL, "
          "Path TEXT NOT NULL, "
          "iPhotoVersion VARCHAR(255) DEFAULT '', "
          "MajorVersion INT DEFAULT 0, "
          "MinorVersion INT DEFAULT 0, "
          "PRIMARY KEY(ID, ArchiveID, Path(255))) "
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='iPhotoLibrary')
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %sAlbums "
          "(iPhotoLibraryID INT NOT NULL, "
          "AlbumID INT NOT NULL, "
          "AlbumName VARCHAR(255) DEFAULT '', "
          "AlbumType VARCHAR(255) DEFAULT '', "
          "FilterMode VARCHAR(255) DEFAULT '', "
          "Master BOOL DEFAULT 0, "
          "GUID VARCHAR(36) DEFAULT '', "
          "PhotoCount INT DEFAULT 0, "
          "PlayMusic BOOL DEFAULT 0, "
          "RepeatSlideShow BOOL DEFAULT 0, "
          "SecondsPerSlide INT DEFAULT 0, "
          "SlideShowUseTitles BOOL DEFAULT 0, "
          "SongPath TEXT, "
          "TransitionDirection TINYINT DEFAULT 0, "
          "TransitionName VARCHAR(255) DEFAULT 'Dissolve', "
          "TransitionSpeed FLOAT DEFAULT 0.0, "
          "PanAndZoom BOOL DEFAULT 0, "
          "ShuffleSlides BOOL DEFAULT 0, "
          "PRIMARY KEY(iPhotoLibraryID, AlbumID)) "
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='Albums')
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %sRolls "
          "(iPhotoLibraryID INT NOT NULL, "          
          "RollID INT NOT NULL, "
          "RollName VARCHAR(255) DEFAULT '', "
          "PhotoCount INT DEFAULT 0, "
          "KeyPhoto INT DEFAULT 0, "
          "RollDate DATETIME DEFAULT 0, "
          "RollDateAsAppleTimer FLOAT DEFAULT 0.0, "
          "PRIMARY KEY(iPhotoLibraryID, RollID)) "          
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='Rolls')
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %sImages "
          "(iPhotoLibraryID INT NOT NULL, "
          "GUID VARCHAR(36) NOT NULL, "
          "RollID INT DEFAULT 0, "
          "ImageID INT NOT NULL, "
          "Rating TINYINT DEFAULT 0, "
          "Comment VARCHAR(255) DEFAULT '', "
          "Caption VARCHAR(255) DEFAULT '', "
          "MediaType VARCHAR(20) DEFAULT '', "
          "AspectRatio FLOAT DEFAULT 0.0, "
          "RotationIsOnlyEdit BOOL DEFAULT 0, "
          "OriginalDate DATETIME DEFAULT 0, "
          "OriginalDateAsAppleTimer FLOAT DEFAULT 0.0, "
          "ModifiedDate DATETIME DEFAULT 0, "
          "ModifiedDateAsAppleTimer FLOAT DEFAULT 0.0, "
          "ImportDate DATETIME DEFAULT 0, "
          "ImportDateAsAppleTimer FLOAT DEFAULT 0.0, "
          "ThumbPath TEXT, "
          "ImagePath TEXT, "
          "OriginalPath TEXT, "
          "PRIMARY KEY(iPhotoLibraryID, ImageID)) "
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='Images')
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %sFilters "
          "(iPhotoLibraryID INT NOT NULL, "
          "AlbumID INT NOT NULL, "
          "Count INT DEFAULT 0, "
          "Operation VARCHAR(255) DEFAULT '', "
          "Type VARCHAR(255) DEFAULT '') "
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='Filters')
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %sKeywords "
          "(KeywordID INT NOT NULL, "
          "iPhotoLibraryID INT NOT NULL, "
          "Keyword VARCHAR(255) DEFAULT '', "
          "PRIMARY KEY(KeywordID, iPhotoLibraryID)) "
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='Keywords')
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %sImageKeywords "
          "(iPhotoLibraryID INT NOT NULL, "
          "ImageID INT NOT NULL, "
          "KeywordID INT NOT NULL) "
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='ImageKeywords')
      self.CreateTable(query=
          "CREATE TABLE IF NOT EXISTS %sAlbumImages "
          "(iPhotoLibraryID INT NOT NULL, "
          "AlbumID INT NOT NULL, "
          "ImageID INT NOT NULL) "
          "DEFAULT CHARSET UTF8"
          % self.__prepend,
          readable_name='AlbumImages')
    except SQLdb.Error, e:
      sys.exit("%(debug)sDatabaseCheck] SQL ERROR: %(error)s\n"
               "%(debug)sDatabaseCheck] Could not add table to database." %
               {'debug':self.__DEBUG_INFO,'error':e})

  def Insert(self, table=None, values=None):
    """ Inserts a new entry into an existing database table.
    
    Args:
      table: String table to use, without prepend string
      values: Dictionary key/value pairs to be inserted
          {'MyKey':253,
          'SomeData':"data for column 'SomeData'",
          'MoreData':"data for column 'MoreData'"}
      
    Kills:
      sys.exit: Insert fails on the database
    """
    if not table or not values:
      sys.exit("%(debug)sInsert] SQL database insert failed.\n"
               "%(debug)sInsert] Cannot insert empty values or tables into "
               "database." % {'debug':self.__DEBUG_INFO})
    # build sql insert command, wrapping data in quotes and ()
    # i.e. INSERT INTO db_test (key1, key2) VALUES("23", "hello")
    sql = ["INSERT INTO %s%s (" % (self.__prepend, table)]
    for key in values.keys():
      sql.append("%s, " % key)
    sql[-1] = sql[-1][:-2]
    sql.append(") VALUES(")
    for value in values.values():
      sql.append("\"%s\", " % self.EncodeString(value))
    sql[-1] = sql[-1][:-2]
    sql.append(")")
    if __debug__:
      print ("%(debug)sInsert] SQL statement to use: %(sql)s" % 
             {'debug':self.__DEBUG_INFO,'sql':''.join(sql)})
    try:
      self.__db.query(''.join(sql))
    except SQLdb.Error, e:
      sys.exit("%(debug)sInsert] SQL ERROR: %(error)s\n"
               "%(debug)sInsert] SQL insert failed: Could not insert "
               "values.\n"
               "%(debug)sInsert] ==> SQL statement: %(sql)s" % {
               'debug':self.__DEBUG_INFO,
               'error':e,
               'sql':''.join(sql)})
          
  def Update(self, table=None, match_keys=None, update_values=None):
    """ Updates an existing database entry with given information.
    
    A query limit of 1 record change is automatically imposed on the query.  
    Keys passed must exist in the database as columns.
    
    Args:
      table: String table to use, without prepend string
      match_keys: Dictionary key/value pairs that are used to match updates
          {'MyKey':253,
          'SomeData':"data for column 'SomeData'"}
      update_values: Dictionarykey/value pairs to insert into the database
          {'MoreData':"new data for column 'MoreData'",
          'EvenMoreData':"new data for column 'EvenMoreData'"}
      
    Kills:
      sys.exit: Update fails on the database
    """
    if not table or not match_keys or not update_values:
      sys.exit("%(debug)sUpdate] SQL database update failed.  Cannot update "
               "rows.\n"
               "%(debug)sUpdate] Empty values, tables or match keys were "
               "provided." % {'debug':self.__DEBUG_INFO})
    # build SQL update command, wrapping data in quotes
    # i.e. UPDATE db_test SET key1="23", key2="hello" WHERE 
    #      key3="1" AND key4="2" LIMIT 1
    sql = ["UPDATE %s%s SET " % (self.__prepend, table)]
    for value_key in update_values:
      sql.append("%s=\"%s\", " % (value_key, 
                 self.EncodeString(update_values[value_key])))
    sql[-1] = sql[-1][:-2]
    sql.append(" WHERE ")
    for key in match_keys:
      sql.append("%s=\"%s\" AND " % (key, self.EncodeString(match_keys[key])))
    sql[-1] = sql[-1][:-4]
    sql.append("LIMIT 1")
    if __debug__:
      print ("%(debug)sUpdate] SQL statement to use: %(sql)s" % 
             {'debug':self.__DEBUG_INFO,'sql':''.join(sql)})
    try:
      self.__db.query(''.join(sql))
    except SQLdb.Error, e:
      sys.exit("%(debug)sUpdate] SQL ERROR: %(error)s\n"
               "%(debug)sUpdate] SQL update failed: Could not update "
               "values.\n"
               "%(debug)sUpdate] ==> SQL statement: %(sql)s" % 
               {'debug':self.__DEBUG_INFO,'error':e,'sql':''.join(sql)})
    
  def Select(self, table=None, match_keys=None, limit=None):
    """ Selects information from the database.
    
    This is a very basic select interface for Exhibit, there is no need to 
    support the more advanced select attributes as they are not used here.
    
    Args:
      table: String table to use, without prepend string
      keys: Dictionary key/value pairs that will be used to match selection
          {'MyKey':253,
          'SomeData':"data for column 'SomeData'"}
      limit: Integer maximum number of results to retrieve
      
    Kills:
      sys.exit: Select fails on the database

    Returns:
      A list of dict's containing result values; None if no results
    """
    if not table or not match_keys:
      sys.exit("%(debug)sSelect] SQL database select failed.\n"
               "%(debug)sSelect] Cannot select with empty table or match "
               "keys." % {'debug':self.__DEBUG_INFO})
    # build sql select command, wrapping data in quotes
    # i.e. SELECT * FROM db_test WHERE key1="23" AND key2="hello" LIMIT 1 
    sql = ["SELECT * FROM %s%s WHERE " % (self.__prepend, table)]
    for key in match_keys:
      sql.append("%s=\"%s\" AND " % (key, self.EncodeString(match_keys[key])))
    sql[-1] = sql[-1][:-4]    
    if limit and isinstance(limit, int):
      sql.append("LIMIT %s" % limit)
    if __debug__:
      print ("%(debug)sSelect] SQL statement to use: %(sql)s" % 
             {'debug':self.__DEBUG_INFO,'sql':''.join(sql)})
    try:
      self.__db.query(''.join(sql))
      rows = self.__db.store_result()
    except SQLdb.Error, e:
      sys.exit("%(debug)sSelect] SQL ERROR: %(error)s\n"
               "%(debug)sSelect] SQL Select failed: could not select\n"
               "%(dbeug)sSelect] ==> SQL statment: %(sql)s" % {
               'debug':self.__DEBUG_INFO, 
               'error':e, 
               'sql':''.join(sql)})
    results = []
    for row in rows.fetch_row(maxrows=self.__RETURN_ALL_ROWS, 
                              how=self.__RETURN_DICT_FORMAT):
      results.append(row)
      if __debug__:
        print ("%(debug)sSelect] Added to SQL result list: %(row)s" % 
               {'debug':self.__DEBUG_INFO,'row':row})
    if results:
      return results
    else:
      return None

  def Delete(self, table=None, match_keys=None):
    """ Deletes a specified database entry with the given information.
    
    A query limit of 1 record change is automatically imposed on the query.  
    Keys passed must exist in the database as columns.
    
    Args:
      table: String table to use, without prepend string
      match_keys: Dictionary key/value pairs used to match row to delete
          {'MyKey':253,
          'SomeData':"data for column 'SomeData'"}
          
    Kills:
      sys.exit: Delete fails on the database
    """
    if not table or not match_keys:
      sys.exit("%(debug)sDelete] SQL database delete failed.\n"
               "%(debug)sDelete] Cannot delete with empty table or match keys."
               % {'debug':self.__DEBUG_INFO})
    # build sql delete command, wrapping data in quotes
    # i.e. DELETE FROM db_test WHERE key1="23" AND key2="hello" LIMIT 1
    sql = ["DELETE FROM %s%s WHERE " % (self.__prepend, table)]
    for key in match_keys:
      sql.append("%s=\"%s\" AND " % (key, self.EncodeString(match_keys[key])))
    sql[-1] = sql[-1][:-4]
    sql.append("LIMIT 1")
    if __debug__:
      print ("%(debug)sDelete] SQL statement to use: %(sql)s" % 
             {'debug':self.__DEBUG_INFO,'sql':''.join(sql)})
    try:
      self.__db.query(''.join(sql))
    except SQLdb.Error, e:
      sys.exit("%(debug)sDelete] SQL ERROR: %(error)s\n"
               "%(debug)sDelete] SQL delete failed: Could not update "
               "values.\n"
               "%(debug)sDelete] ==> SQL statement: %(sql)s" % 
               {'debug':self.__DEBUG_INFO,'error':e,'sql':''.join(sql)})
          


if __name__ == "__main__":
  print "Testing SQL Connector Class...\n"
  print "-->Test database connection:"
  sql_connection = {'address':'localhost',
                    'username':'exhibit', 
                    'password':'exhibit',
                    'database':'website_database',
                    'prepend':'exhibit_test_'}
  sql = SQL(connection=sql_connection)
  print "-->PASS!\n"
  print "-->Test forced database reset:"
  sql.DatabaseCheck(force=True)
  print "-->PASS!\n"
  print "-->Test Insert:"
  sql.Insert("Albums",{'iPhotoLibraryID':'1',
                       'GUID':'asdf-asdf-asdf-asdf',
                       'AlbumID':'2'})
  print "-->PASS!\n"
  print "-->Test CheckTableExists:"
  if sql.CheckTableExists("Albums"):
    print "-->PASS!\n"
  else:
    print "-->FAIL!\n"
  print "-->Test EncodeString:"
  if (sql.EncodeString('"') == '\\"' and sql.EncodeString('%') == '\\%'):
    print "-->PASS!\n"
  else:
    print "-->FAIL!\n"
  print "-->Test Update:"
  sql.Update("Albums",{'AlbumID':'2'},{'iPhotoLibraryID':'123123'})
  print "-->PASS!\n"
  print "-->Test Select:"
  print sql.Select("Albums",{'iPhotoLibraryID':'123123'},limit=1)
  select_results = sql.Select("Albums",{'iPhotoLibraryID':'555555'})
  if select_results:
    print "-->FAIL!\n"
  else:
    print "-->PASS!\n"
  print "-->Test Delete:"
  sql.Delete("Albums",{'AlbumID':'2'})
  print "-->PASS!\n"
  print "\n\nTesting completeled successfully!\n\n"
