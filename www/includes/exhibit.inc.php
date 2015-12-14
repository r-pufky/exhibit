<?
/*
	Copyright 2008 Robert Pufky
	
    functions to render exhibit pages

	Global Functions:
	_print_row($row, $number_of_columns)
	_find_file_extenstion($filename)
	_display_images($roll, $library)
	_display_rolls()
	_draw_search_keys()
	_display_search($query)
	_create_search_heap($table)
	_generate_search_images($table,$keywords)
	_user_permissions($username,$type)
	
	Global Variables:
	number_of_columns - the number of columns to display on a page
    image_src - the source directory of the image data
    table_format - the html format of the table to use
    star - the html code to display a single rating image
    rating - array containing html code to display ratings based on index (i.e.
             rating[2] - 2 star rating.
    indent - the html table indentation for base table row
*/
$number_of_columns = 3;
$image_src = "http://www.example.com/images/exhibit/";
$table_format = "\n\t\t\t\t\t<table border=\"0\" cellspacing=\"0\" " .
                "cellpadding=\"1\">";
$star = "<img src='inc/ico/custom/rating-10.png' alt='Rating' />";
$rating = array("","$star","$star$star","$star$star$star",
                "$star$star$star$star","$star$star$star$star$star");
$indent = "\n\t\t\t\t\t\t";



// _print_row
// Args:
//   array - data for one row
//   integer - the number of columns to render per row
// Renders a complete row for a display table.
// func_num_args 0 based, number_of_columns 1 based
Function _print_row($row) {
  global $number_of_columns;
  global $indent;
  for( $table_row = 0; $table_row < 4; $table_row++ ) {
    echo $indent."<tr>";
    for( $i = 0; $i < $number_of_columns; $i++ ) {
      if( $row[$i] ) {
        echo $indent."\t<td align=\"center\">".$row[$i][$table_row]."</td>";
      } else {
        echo $indent."\t<td>&nbsp;</td>";
      }
    }
    echo $indent."</tr>";
  }
  
  echo $indent."<tr>";
  for( $i = 0; $i < $number_of_columns; $i++ ) {
    echo $indent."\t<td>&nbsp;</td>";
  }
  echo $indent."</tr>";
}



// _find_file_extenstion
// Args:
//   string - filename to find extension
// Returns:
//   string - the file extension to use, without the dot
Function _find_file_extension($filename) {
  $exts = split("[/\\.]", $filename) ;
  return $exts[count($exts)-1];
}



// _draw_search_key
// Draw a dropdown containing all keywords in exhibit.
function _draw_search_key() {
    global $__dbc;
    $query = "SELECT KeywordID, Keyword FROM exhibit_Keywords ORDER BY Keyword".
             " ASC";
	$keys = __query($query,"","");
    $search_options = "<option value=\"ANY\">Any Keyword</option>".
                      "<option value=\"ALL\">All Keywords</option>";
    $key_list = "<option value=\"\">&nbsp;</option>";
    while( $row = mysql_fetch_array($keys) ) {
	    $key_list .= "<option value=\"".$row['Keyword']."\">".
	                  $row['Keyword']."</option>";
	}
    echo "\n<table border=\"0\" cellspacing=\"2\" cellpadding=\"0\">\n<tr>".
         "<td valign=\"top\"><form action=\"".$_SERVER[PHP_SELF]."\"".
         " method=\"post\">".
         "<input type=\"hidden\" name=\"search\" value=\"1\">".
         "<select name=\"key1\" size=\"1\">".$key_list."</select>".
         "</td><td valign=\"top\">".
         "<select name=\"key2\" size=\"1\">".$key_list."</select>".
         "</td><td valign=\"top\">".
         "<select name=\"key3\" size=\"1\">".$key_list."</select>".
         "</td><td valign=\"top\">".
         "<select name=\"restriction\" size=\"1\">".$search_options."</select>".
         "</td><td valign=\"top\"><input type=\"submit\" value=\" Search \">".
         "</form></td></tr></table><br>\n".
         "<span class=\"exhibitcontent\">&nbsp;&nbsp;&nbsp;Blank boxes do not".
         " affect search.  Not all keywords will return images because of".
         " access restrictions.  Get an account.</span>";
}



// _create_search_heap
// Args:
//   string - the temporary table name to use
// Creates a temporary heap table to use for searching
Function _create_search_heap($table) {
  global $__dbc;
  $create_search_heap = "CREATE TEMPORARY TABLE exhibit_".$table." ".
                        "(iPhotoLibraryID INT NOT NULL,".
                        "GUID VARCHAR(36) NOT NULL,".
                        "RollID INT DEFAULT 0,".
                        "ImageID INT NOT NULL,".
                        "RollName VARCHAR(255) DEFAULT '',".
                        "Rating TINYINT DEFAULT 0,".
                        "Comment VARCHAR(255) DEFAULT '',".
                        "Caption VARCHAR(255) DEFAULT '',".
                        "MediaType VARCHAR(20) DEFAULT '',".
                        "OriginalDate DATETIME DEFAULT 0,".
                        "ThumbPath VARCHAR(255),".
                        "ImagePath VARCHAR(255),".
                        "KeywordID INT NOT NULL,".
                        "Keyword VARCHAR(255) DEFAULT '',".
                        "Public BOOL DEFAULT 0,".
                        "GroupID INT DEFAULT 0) TYPE=HEAP DEFAULT CHARSET UTF8";
  __query($create_search_heap,"","");
}



// _generate_search_images($table,$keywords)
// Args:
//   string - the temporary table name to use
//   string - the keyword to search for and insert (no quotes)
//   boolean - true if the table should be cleared (truncated) before filling
// Searches for and inserts searched images into temporary table
Function _generate_search_images($table, $keyword, $drop) {
  global $__dbc;
  if( $drop ) { __query("truncate table exhibit_".$table,"",""); }
  $gather_search_images = "INSERT INTO exhibit_".$table." SELECT ".
      "exhibit_Images.iPhotoLibraryID AS iPhotoLibraryID,".
      "exhibit_Images.GUID AS GUID,".
      "exhibit_Images.RollID AS RollID,".
      "exhibit_Images.ImageID AS ImageID,".
      "exhibit_Rolls.RollName AS RollName,".
      "exhibit_Images.Rating AS Rating,".
      "exhibit_Images.Comment AS Comment,".
      "exhibit_Images.Caption AS Caption,".
      "exhibit_Images.MediaType AS MediaType,".
      "exhibit_Images.OriginalDate AS OriginalDate,".
      "exhibit_Images.ThumbPath AS ThumbPath,".
      "exhibit_Images.ImagePath AS ImagePath,".
      "exhibit_Keywords.KeywordID AS KeywordID,".
      "exhibit_Keywords.Keyword AS Keyword,".
      "exhibit_Permissions.Public AS Public,".
      "exhibit_Permissions.GroupID AS GroupID".
      " FROM exhibit_Images LEFT JOIN exhibit_ImageKeywords ON ".
      "(exhibit_Images.ImageID=exhibit_ImageKeywords.ImageID AND ".
      "exhibit_Images.iPhotoLibraryID=exhibit_ImageKeywords.iPhotoLibraryID)".
      "LEFT JOIN exhibit_Keywords ON ".
      "(exhibit_ImageKeywords.KeywordID=exhibit_Keywords.KeywordID) ".
      "LEFT JOIN exhibit_Rolls ON ".
      "(exhibit_Images.RollID=exhibit_Rolls.RollID AND ". 
      "exhibit_Images.iPhotoLibraryID=exhibit_Rolls.iPhotoLibraryID) ".
      "LEFT JOIN exhibit_Permissions ON ". 
      "(exhibit_Images.iPhotoLibraryID=exhibit_Permissions.iPhotoLibraryID ".
      "AND exhibit_Images.RollID=exhibit_Permissions.RollID) ".
      "WHERE exhibit_Keywords.Keyword='".$keyword."'";
  __query($gather_search_images,"","");
}



// _generate_search_comparison
// Args:
//   string - the source temporary table name
//   string - the keyword to look for in the table (no quotes)
//   string - the destination table name
// Searchs for a given keyword in a table of search results, and inserts them
// into the new table
Function _generate_search_comparison($source_table,$keyword,$target_table) {
  $comparsion_search = "INSERT INTO exhibit_".$target_table." SELECT ".
      "exhibit_".$source_table.".iPhotoLibraryID AS iPhotoLibraryID,".
      "exhibit_".$source_table.".GUID AS GUID,".
      "exhibit_".$source_table.".RollID AS RollID,".
      "exhibit_".$source_table.".ImageID AS ImageID,".
      "exhibit_".$source_table.".RollName AS RollName,".
      "exhibit_".$source_table.".Rating AS Rating,".
      "exhibit_".$source_table.".Comment AS Comment,".
      "exhibit_".$source_table.".Caption AS Caption,".
      "exhibit_".$source_table.".MediaType AS MediaType,".
      "exhibit_".$source_table.".OriginalDate AS OriginalDate,".
      "exhibit_".$source_table.".ThumbPath AS ThumbPath,".
      "exhibit_".$source_table.".ImagePath AS ImagePath,".
      "exhibit_".$source_table.".KeywordID AS KeywordID,".
      "exhibit_".$source_table.".Keyword AS Keyword,".
      "exhibit_".$source_table.".Public AS Public,".
      "exhibit_".$source_table.".GroupID AS GroupID".
      " FROM exhibit_".$source_table." LEFT JOIN exhibit_ImageKeywords ON ".
      "(exhibit_".$source_table.".iPhotoLibraryID=".
      "exhibit_ImageKeywords.iPhotoLibraryID AND ".
      "exhibit_".$source_table.".ImageID=exhibit_ImageKeywords.ImageID) ".
      "LEFT JOIN exhibit_Keywords ON ".
      "(exhibit_ImageKeywords.KeywordID=exhibit_Keywords.KeywordID) ".
      "WHERE exhibit_Keywords.Keyword='".$keyword."'";
  __query($comparsion_search,"","");
}



// _display_images
// Args:
//   integer - the roll to display
//   integer - the library to display
//   string - the username to use for permissions
// Renders a table with images contained in a row
Function _display_images($roll, $library, $username) {
  global $__dbc;
  global $number_of_columns;
  global $image_src;
  global $rating;
  global $table_format;
  $image_query = "SELECT exhibit_Images.iPhotoLibraryID AS iPhotoLibraryID, ".
      "GUID, ThumbPath, ImagePath, Comment, OriginalDate, MediaType, ImageID,".
      " Rating FROM exhibit_Images LEFT JOIN exhibit_Permissions ON ".
      "(exhibit_Images.iPhotoLibraryID=exhibit_Permissions.iPhotoLibraryID ".
      "AND exhibit_Images.RollID=exhibit_Permissions.RollID) WHERE ".
      "exhibit_Images.iPhotoLibraryID=".$library." AND ".
      "exhibit_Images.RollID=".$roll." ORDER BY OriginalDate ASC";
  $roll_query = "SELECT exhibit_Rolls.RollName AS RollName, ".
      "exhibit_Permissions.GroupID AS GroupID, ".
      "exhibit_Permissions.Public AS Public ".
      "FROM exhibit_Rolls LEFT JOIN exhibit_Permissions ON ".
      "(exhibit_Rolls.iPhotoLibraryID=exhibit_Permissions.iPhotoLibraryID AND".
      " exhibit_Rolls.RollID=exhibit_Permissions.RollID) WHERE ".
      "exhibit_Rolls.RollID=".$roll." AND ".
      _user_permissions($username,'query').
      " ORDER BY RollDate DESC";
  $images = __query($image_query,"","");

  if( $roll_name = mysql_fetch_array(__query($roll_query,"","")) ) {
    _page_sechead("exhibit.png",$roll_name['RollName']);
    echo $table_format;

    while($row = mysql_fetch_array($images)) {
      $image_thumb = $row['iPhotoLibraryID'].$row["GUID"].'T.'.
                     _find_file_extension($row["ThumbPath"]);
      $image_full = $row['iPhotoLibraryID'].$row["GUID"]."." .
                    _find_file_extension($row["ImagePath"]);

      $image_slimbox_caption = "Keywords: ";
      $keyword_query = "SELECT exhibit_Keywords.Keyword AS Keyword FROM ".
          "exhibit_Keywords LEFT JOIN ".
          "exhibit_ImageKeywords ON (exhibit_Keywords.iPhotoLibraryID = ".
          "exhibit_ImageKeywords.iPhotoLibraryID AND exhibit_Keywords.KeywordID".
          "=exhibit_ImageKeywords.KeywordID) WHERE ".
          "exhibit_ImageKeywords.iPhotoLibraryID=".$row["iPhotoLibraryID"].
          " AND exhibit_ImageKeywords.ImageID=".$row["ImageID"];
      $image_keywords = __query($keyword_query,"","");
      while($keyword_row = mysql_fetch_array($image_keywords)) {
        $image_slimbox_caption .= $keyword_row["Keyword"].", ";
      }
      $image_slimbox_caption = rtrim($image_slimbox_caption,", ")."<br />";
    
      if( $row["Comment"] != "" ) {
        $image_slimbox_caption .= "Comments: ".$row["Comment"]."<br />";
      }
      $image_slimbox_caption .= "Date: ".$row["OriginalDate"]."<br />";
      $image_slimbox_caption .= $rating[$row["Rating"]]."<br />";                              
      $image_slimbox_caption .= "&lt;a href=&quot;".$image_src.$image_full.
                                "&quot;&gt;";
      if( $row["MediaType"] == "Image" ) {
        $image_slimbox_caption .= "(See Full-sized Image)&lt;/a&gt;";
      } else {
        $image_slimbox_caption .= "(See Video)&lt;/a&gt;";
      }

      $process_results[] = array("<a href=\"".$image_src.$image_thumb.
          "\" rel=\"lightbox[".$roll_name[0]."]\" title=\"".
          $image_slimbox_caption."\"><img border=\"0\" class=\"exhibit\" ".
          "src=\"".$image_src.$image_thumb."\" /></a>",
          "<span class=\"exhibitcontent\">".$row["Comment"]."</span>", 
          "<span class=\"exhibitcontent\">".$row["OriginalDate"]."</span>",
          "<span class=\"exhibitcontent\">".$rating[$row["Rating"]]."</span>");

      if( count($process_results) == $number_of_columns ) {
        _print_row($process_results);
        unset($process_results);
        $process_results = array();
      }
    }
    if( count($process_results) != 0 ) {
      _print_row($process_results);
    }
    echo "\n\t\t\t\t\t</table>\n";
  }
}



// _display_rolls
// Args:
//   string - the username to use for permissions
// Renders a table with rolls contained in a row
Function _display_rolls($username) {
  global $__dbc;
  global $number_of_columns;
  global $image_src;
  global $rating;
  global $table_format;  
  $query = "SELECT exhibit_Rolls.*, exhibit_Permissions.GroupID AS GroupID, ".
      "exhibit_Permissions.Public AS Public ".
      "FROM exhibit_Rolls LEFT JOIN exhibit_Permissions ON ".
      "(exhibit_Rolls.iPhotoLibraryID=exhibit_Permissions.iPhotoLibraryID AND".
      " exhibit_Rolls.RollID=exhibit_Permissions.RollID) WHERE ".
      _user_permissions($username,'query').
      " ORDER BY RollDate DESC";
  $sql_results = __query($query,"","");
  $process_results = array();
  
  echo $table_format;
  
  while($row = mysql_fetch_array($sql_results)) {
    $query = "select GUID, ThumbPath from exhibit_Images where ".
        "iPhotoLibraryID = ".$row['iPhotoLibraryID']." AND ".
        "ImageID = ".$row['KeyPhoto'];
    $image = mysql_fetch_array(__query($query,"",""));
    $image_thumb = $row['iPhotoLibraryID'].$image["GUID"].'T.'._find_file_extension($image["ThumbPath"]);

    $photo_count = "<span class=\"exhibitcontent\">".$row["PhotoCount"];
    if( $row["PhotoCount"] == 1 ) {
      $photo_count .= " photo</span>";
    } else {
      $photo_count .= " photos</span>";
    }

    $process_results[] = array("<a href=\"http://www.example.com".
        $_SERVER[PHP_SELF]."?library=".$row["iPhotoLibraryID"]."&roll=".
        $row["RollID"]."\">".
        "<img border=\"0\" class=\"exhibit\" src=\"".$image_src.$image_thumb."\" /></a>",
        "<span class=\"exhibitcontent\">".$row["RollName"]."</span>", 
        "<span class=\"exhibitcontent\">".$row["RollDate"]."</span>",
        $photo_count);

    if( count($process_results) == $number_of_columns ) {
      _print_row($process_results);
      unset($process_results);
      $process_results = array();
    }
  }
  if( count($process_results) != 0 ) {
    _print_row($process_results);
  }
  echo "\n\t\t\t\t\t</table>\n";
}



// _display_images
// Args:
//   string - the query to use
//   string - the text to display on the search title
// Renders a table with images contained in a row
Function _display_search($image_query,$search_text) {
  global $__dbc;
  global $number_of_columns;
  global $image_src;
  global $rating;
  global $table_format;
  
  $images = __query($image_query,"","");
  echo mysql_info($__dbc);
  _page_sechead("search.png","Search Results For: ".$search_text.
                ".  ".mysql_num_rows($images)." images found.");
  echo $table_format;
  
  while($row = mysql_fetch_array($images)) {
    $image_thumb = $row['iPhotoLibraryID'].$row["GUID"].'T.'.
                   _find_file_extension($row["ThumbPath"]);
    $image_full = $row['iPhotoLibraryID'].$row["GUID"]."." .
                  _find_file_extension($row["ImagePath"]);

    $image_slimbox_caption = "Keywords: ";
    $keyword_query = "SELECT exhibit_Keywords.Keyword AS Keyword FROM ".
        "exhibit_Keywords LEFT JOIN ".
        "exhibit_ImageKeywords ON (exhibit_Keywords.iPhotoLibraryID = ".
        "exhibit_ImageKeywords.iPhotoLibraryID AND exhibit_Keywords.KeywordID".
        "=exhibit_ImageKeywords.KeywordID) WHERE ".
        "exhibit_ImageKeywords.iPhotoLibraryID=".$row["iPhotoLibraryID"].
        " AND exhibit_ImageKeywords.ImageID=".$row["ImageID"];
    $image_keywords = __query($keyword_query,"","");
    while($keyword_row = mysql_fetch_array($image_keywords)) {
      $image_slimbox_caption .= $keyword_row["Keyword"].", ";
    }
    $image_slimbox_caption = rtrim($image_slimbox_caption,", ")."<br />";
    
    if( $row["Comment"] != "" ) {
      $image_slimbox_caption .= "Comments: ".$row["Comment"]."<br />";
    }
    $image_slimbox_caption .= "Date: ".$row["OriginalDate"]."<br />";
    $image_slimbox_caption .= $rating[$row["Rating"]]."<br />";                              
    $image_slimbox_caption .= "&lt;a href=&quot;".$image_src.$image_full.
                              "&quot;&gt;";
    if( $row["MediaType"] == "Image" ) {
      $image_slimbox_caption .= "(See Full-sized Image)&lt;/a&gt;";
    } else {
      $image_slimbox_caption .= "(See Video)&lt;/a&gt;";
    }

    $process_results[] = array("<a href=\"".$image_src.$image_thumb.
        "\" rel=\"lightbox[".$roll_name[0]."]\" title=\"".
        $image_slimbox_caption."\"><img border=\"0\" class=\"exhibit\" ".
        "src=\"".$image_src.$image_thumb."\" /></a>",
        "<span class=\"exhibitcontent\">".$row["Comment"]."</span>", 
        "<span class=\"exhibitcontent\">".$row["OriginalDate"]."</span>",
        "<span class=\"exhibitcontent\">".$rating[$row["Rating"]]."</span>");

    if( count($process_results) == $number_of_columns ) {
      _print_row($process_results);
      unset($process_results);
      $process_results = array();
    }
  }
  if( count($process_results) != 0 ) {
    _print_row($process_results);
  }
  echo "\n\t\t\t\t\t</table>\n";
}



// _user_permissions
// Args:
//   string - username to lookup permissions for
//   string - type of results to return (array or query)
// Returns:
//   Array containing groupid's this user belongs to
// Returns a MySQL safe string for querying usergroups (group1 OR group2 ...)
Function _user_permissions($username, $type) {
  $user_query = "SELECT ".
                "exhibit_UserGroups.GroupID AS groupid ".
                "FROM website_users LEFT JOIN exhibit_UserGroups ".
                "ON (website_users.ID=exhibit_UserGroups.UserID) ".
                "WHERE website_users.Username='".$username."'";
                 "(exhibit_UserGroups.GroupID=exhibit_Groups.ID)";
  $user_results = __query($user_query,"","");
  
  switch( $type ) {
    case 'query': {
      $user_groups = "Public=TRUE OR";
      while($row = mysql_fetch_array($user_results)) {
        $user_groups .= " GroupID=".$row['groupid']." OR";
      }
      if( $username == 'Anonymous' ) { $user_groups = "Public=TRUE "; }
      $user_groups = rtrim($user_groups,"OR");
    } break;
    case 'array': {
      $user_groups = array();
      while($row = mysql_fetch_array($user_results)) {
        $user_groups[] = $row['groupid'];
      }
    } break;
  };
  return $user_groups;
}
?>
