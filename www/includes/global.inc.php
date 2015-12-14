<?
/*
	Copyright 2006 Robert Pufky
	
	Global functions & variables
	
	Note: ALL global variables / functions start with __

	Global variables:
	$__anon - holds the anonymous user id (will depreciate)
	$__user - holds the user information for a logged in user (will depreciate)
	$__dbc - holds the database connection id for queries to the "website" database
	
	Global functions:
	__query($query,$db,$link)
	__https()
*/

// start unique session for this visitor (or continue if already here
session_start();

// include page functions
include("page.inc.php");

// the anonymous ID
$__anon = ##########;
// holds user account information
$__user = "";
// the default mysql connection link 
if(!$__dbc = mysql_connect("localhost","exhibit","") ) { die(_page_error("Database connection error: " . mysql_error())); }

// Function: __query
// Requries: string - query to preform
//           string - database to query from
//           resource link - variable holding connnection link to database
// Returns: transparent.  Same as mysql_query.*/
Function __query($query,$db,$link) {
	// if the database is not specified, use "exhibit"
	if( $db == "" ) { $db = "exhibit"; }
	// if the link is not specified, use default connection
	if( $link == "" ) {
		global $__dbc;
		$link = $__dbc;
	}
	
  // attempt to select the database on the resource, otherwise error
	if( !mysql_select_db("$db",$link) ) { die(_page_error("Cannot select $db database: " . mysql_error())); }

	// preform the query and return the results
	return mysql_query($query,$link);
}

// Function: __https
// Requires: none
// Returns: none - redirects to an encrypted page
Function __https() {
  // only redirect if we are not encrypted already
	if( $_SERVER['HTTPS'] != "on" ) {
		header("Location: https://www.example.com$_SERVER[PHP_SELF]?$_SERVER[QUERY_STRING]");
		exit;
	}
}
?>
