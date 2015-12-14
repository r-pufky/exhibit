<?
/*
	Copyright 2008 Robert Pufky
	
    functions to render exhibit pages

	Global Functions:
	_print_rows($rows)
	_find_file_extenstion($filename)
	_display_permissions()
	_set_permissions($roll,$library,$public,$group)
	_display_groups()
	_set_groups($action,$name,$description,$groupid)
	_display_users()
	_set_users($action,$userid,$groupid)
	
	Global Variables:
    image_src - the source directory of the image data
    table_format - the html format of the table to use
    indent - the html table indentation for base table row
*/
$image_src = "http://www.example.com/images/exhibit/";
$table_format = "\n\t\t\t\t\t<table border=\"0\" cellspacing=\"0\" " .
                "cellpadding=\"1\">";
$indent = "\n\t\t\t\t\t\t";



// _print_rows
// Args:
//   array - array of arrays containing data for one row
//   integer - number of columns in the row
// Renders all rows in an two dimensional array; must contain <td> and </td>
Function _print_rows($rows) {
  global $indent;
  for( $row = 0; $row < count($rows); $row++ ) {
    echo $indent."<tr>";
    $i = 0;
    while( $rows[$row][$i] ) {
      echo $indent."\t".$rows[$row][$i];
      $i++;
    }
    echo $indent."</tr>";
  }
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



// _set_groups
// Args:
//   string - action to perform
//   string - User ID
//   integer - Group ID
// Updates a given user, then displays all users
Function _set_users($action, $userid, $groupid) {
  switch( $action ) {
    case 'add': {
      if( isset($userid) and isset($groupid) ) {
        $add_query = "INSERT INTO exhibit_UserGroups ".
                     "(UserID,GroupID) ".
                     "VALUES ('".$userid."', '".$groupid."')";
        __query($add_query,"","");
      } else {
        _page_section("error.png","Could not add group, invalid data.");
      }      
    } break;
    case 'delete': {
      if( isset($groupid) ) {
        $delete_query = "DELETE FROM exhibit_UserGroups WHERE UserID=".$userid.
                        " AND GroupID=".$groupid;
        __query($delete_query,"","");
      } else {
        _page_section("error.png","Could not delete group, no groupid given");
      }
    } break;
    default: {
      _page_section("error.png","Whoops.  Did not understand what to do");
    } break;
  };
  _display_users();
}



// _display_users
// Renders a table with all users and their groups in database
Function _display_users() {
  global $__dbc;
  global $table_format; 

  $user_query = "SELECT ".
                 "website_users.Username AS username, ".
                 "website_users.Actualname AS actualname, ".
                 "website_users.ID AS userid, ".
                 "exhibit_Groups.ID AS groupid, ".
                 "exhibit_Groups.GroupName AS groupname ".
                 "FROM website_users LEFT JOIN exhibit_UserGroups ".
                 "ON (website_users.ID=exhibit_UserGroups.UserID) ".
                 "LEFT JOIN exhibit_Groups ON ".
                 "(exhibit_UserGroups.GroupID=exhibit_Groups.ID)";
  $user_results = __query($user_query,"","");

  $group_query = "SELECT * FROM exhibit_Groups";
  $group_results = __query($group_query,"","");
  $groups = array();
  while($row = mysql_fetch_array($group_results)) {
    $groups[$row['ID']] = array('GroupName'=>$row['GroupName'],
                                'GroupDescription'=>$row['GroupDescription']);
  }  
  $group_list = "<td><select name=\"groupid\" size=\"1\">";
  foreach( $groups as $key => $value ) {
    $group_list .= "<option value=\"".$key."\">".$value['GroupName'].
                   "</option>";
  }
  $group_list .= "</select></td>";

  $last_user = NULL;
  while($row = mysql_fetch_array($user_results)) {
    if( $last_user != $row['userid'] ) {
      if( isset($last_user) ) {
        $user = "<td><form action=\"".$_SERVER[PHP_SELF]."\" ".
                "method=\"post\"><input type=\"hidden\" name=\"action\" ".
                "value=\"users\"><input type=\"hidden\" name=\"userid\" ".
                "value=\"".$last_user."\"></td>";
        $add = "<td><input type=\"submit\" name=\"subaction\" ".
               "value=\" ADD GROUP \"></form></td>";
        _print_rows(array(array($user,$group_list,"<td>&nbsp;</td>",$add)));
        echo "\n\t\t\t\t\t</table>\n";
      }
      _page_section("login.png",
                    $row['actualname']." (".$row['username'].")");
      _page_section("","Current Group Memeberships");
      echo $table_format;
    }
    if( isset($row['groupid']) ) {
      $group = "<td><form action=\"".$_SERVER[PHP_SELF]."\" ".
               "method=\"post\"><input type=\"hidden\" name=\"action\" ".
               "value=\"users\"><input type=\"hidden\" name=\"userid\" ".
               "value=\"".$row['userid']."\">".
               "<input type=\"hidden\" name=\"groupid\" ".
               "value=\"".$row['groupid']."\">".$row['groupname']."</td>";
      $delete = "<td><input type=\"submit\" name=\"subaction\" ".
                "value=\" DELETE \"></form></td>";
      _print_rows(array(array("<td>&nbsp;</td>",$group,
                              "<td>&nbsp;</td>",$delete)));
    }
    $last_user = $row['userid'];
  }
  $user = "<td><form action=\"".$_SERVER[PHP_SELF]."\" ".
          "method=\"post\"><input type=\"hidden\" name=\"action\" ".
          "value=\"users\"><input type=\"hidden\" name=\"userid\" ".
          "value=\"".$last_user."\"></td>";
  $add = "<td><input type=\"submit\" name=\"subaction\" ".
         "value=\" ADD GROUP \"></form></td>";
  _print_rows(array(array($user,$group_list,"<td>&nbsp;</td>",$add)));
  echo "\n\t\t\t\t\t</table>\n";
}



// _set_groups
// Args:
//   string - action to perform
//   string - Group name to use
//   string - Group description to use
//   integer - Group ID to update, or 0 if new group
// Updates a given group, then displays all groups
Function _set_groups($action, $name, $description, $groupid) {  
  switch( $action ) {
    case 'add': {
      if( isset($name) and isset($description) ) {
        $add_query = "INSERT INTO exhibit_Groups (GroupName,GroupDescription) ".
                     "VALUES ('".$name."', '".$description."')";
        __query($add_query,"","");
      } else {
        _page_section("error.png","Could not add group, invalid data.");
      }      
    } break;
    case 'delete': {
      if( isset($groupid) ) {
        $delete_query = "DELETE FROM exhibit_Groups WHERE ID=".$groupid.
                        " LIMIT 1";
        __query($delete_query,"","");
        $delete_others = "UPDATE exhibit_Permissions SET GroupID='0' WHERE ".
                         "GroupID='".$groupid."'";
      } else {
        _page_section("error.png","Could not delete group, no groupid given");
      }
    } break;
    case 'update': {
      if( isset($groupid) and isset($name) and isset($description) ) {
        $update_query = "UPDATE exhibit_Groups SET GroupName='".$name."',".
                        "GroupDescription='".$description."' WHERE ID='".
                        $groupid."'";                 
        __query($update_query,"","");
      } else {
        _page_section("error.png","Could not update group, invalid data");
      }
    } break;
    default: {
      _page_section("error.png","Whoops.  Did not understand what to do");
    } break;
  };
  _display_groups();
}



// _display_groups
// Renders a table with all groups in database
Function _display_groups() {
  global $__dbc;
  global $table_format; 

  $group_query = "SELECT * FROM exhibit_Groups";
  $group_results = __query($group_query,"","");
  
  echo $table_format . "<td>Group Name</td><td>Description</td><td>&nbsp;</td>".
                       "<td>&nbsp;</td>";
  $table = array();
  while($row = mysql_fetch_array($group_results)) {
    $name = "<td><form action=\"".$_SERVER[PHP_SELF]."\" method=\"post\">".
            "<input type=\"hidden\" name=\"action\" value=\"groups\">".
            "<input type=\"hidden\" name=\"groupid\" ".
            "value=\"".$row['ID']."\">".
            "<input type=\"text\" size=\"10\" name=\"name\" ".
            "value=\"".$row['GroupName']."\"></td>";
    $description = "<td><input type=\"text\" size=\"50\" name=\"description\" ".
                   "value=\"".$row['GroupDescription']."\"></td>";
    $edit = "<td><input type=\"submit\" name=\"subaction\" value=\" UPDATE \">".
            "</td>";
    $delete = "<td><input type=\"submit\" name=\"subaction\" ".
              "value=\" DELETE \"></form></td>";
    $table[] = array($name,$description,$edit,$delete);    
  }
  _print_rows($table);
  echo "\n\t\t\t\t\t</table>\n";
  _page_section("exhibit.png","Add A New Group");
  echo $table_format . "<td>Group Name</td><td>Description</td><td>&nbsp;</td>";  
  $name = "<td><form action=\"".$_SERVER[PHP_SELF]."\" method=\"post\">".
          "<input type=\"hidden\" name=\"action\" value=\"groups\">".
          "<input type=\"text\" size=\"10\" name=\"name\" value=\"\"></td>";
  $description = "<td><input type=\"text\" size=\"50\" name=\"description\" ".
                 "value=\"\"></td>";
  $blank = "<td>&nbsp;</td>";
  $add = "<td><input type=\"submit\" name=\"subaction\" value=\" ADD GROUP \">".
         "</form></td>";
  _print_rows(array(array($name,$description,$blank,$add)));    
  echo "\n\t\t\t\t\t</table>\n";
}



// _set_permissions
// Args:
//   integer - Roll ID to use
//   integer - Library ID to use
//   integer - Public boolean to update
//   integer - Group ID to update
// Updates a given Roll, then displays roll permissions
Function _set_permissions($roll, $library, $public, $group) {
  $update_query = "UPDATE exhibit_Permissions SET Public='".$public."',".
                  "GroupID='".$group."' WHERE iPhotoLibraryID='".$library.
                  "' AND RollID='".$roll."'";
  __query($update_query,"","");
  _display_permissions();
}



// _display_permissions
// Renders a table with all Rolls in database, their current permissions,
// and a button to edit them.
Function _display_permissions() {
  global $__dbc;
  global $image_src;
  global $table_format; 
  $roll_query = 
      "SELECT exhibit_Rolls.*, exhibit_Permissions.GroupID AS GroupID, ".
      "exhibit_Permissions.Public AS Public FROM exhibit_Rolls LEFT JOIN ".
      "exhibit_Permissions ON ".
      "(exhibit_Rolls.iPhotoLibraryID=exhibit_Permissions.iPhotoLibraryID AND".
      " exhibit_Rolls.RollID=exhibit_Permissions.RollID) ".
      "ORDER BY RollDate DESC";
  $roll_results = __query($roll_query,"","");

  $group_query = "SELECT * FROM exhibit_Groups";
  $group_results = __query($group_query,"","");
  $groups = array();
  while($row = mysql_fetch_array($group_results)) {
    $groups[$row['ID']] = array('GroupName'=>$row['GroupName'],
                                'GroupDescription'=>$row['GroupDescription']);
  }
  
  echo $table_format . "<td>Cover </td><td>Roll Name</td><td>Roll Date</td>".
                       "<td># of Photos&nbsp;&nbsp;</td>".
                       "<td>Public?&nbsp;&nbsp;</td>".
                       "<td>Group&nbsp;&nbsp;</td><td>&nbsp;</td>";
  $table = array();
  while($row = mysql_fetch_array($roll_results)) {
    $query = "select GUID, ThumbPath from exhibit_Images where ".
             "iPhotoLibraryID = ".$row['iPhotoLibraryID']." AND ".
             "ImageID = ".$row['KeyPhoto'];
    $image = mysql_fetch_array(__query($query,"",""));
    $image_thumb = "<td width=\"40px\"><a href=\"http://www.example.com".
                   $_SERVER[PHP_SELF]."?library=".$row["iPhotoLibraryID"].
                   "&roll=".$row['RollID']."\"><img border=\"0\" ".
                   " class=\"exhibitpermissions\" ".
                   "src=\"".$image_src.
                   $row['iPhotoLibraryID'].$image['GUID'].'T.'.
                   _find_file_extension($image['ThumbPath'])."\" /></a></td>";
    $photo_count = "<td><span class=\"exhibitcontent\">".$row["PhotoCount"];
    if( $row["PhotoCount"] == 1 ) {
      $photo_count .= " photo</span></td>";
    } else {
      $photo_count .= " photos</span></td>";
    }
    $roll_name = "<td><span class=\"exhibitcontent\">".$row['RollName'].
                 "</span></td>";
    $roll_date = "<td><span class=\"exhibitcontent\">".$row['RollDate'].
                 "</span></td>";
    $public = "<td><form action=\"".$_SERVER[PHP_SELF]."\" method=\"post\">".
              "<input type=\"hidden\" name=\"library\" ".
              "value=\"".$row['iPhotoLibraryID']."\">".
              "<input type=\"hidden\" name=\"roll\" ".
              "value=\"".$row['RollID']."\">".
              "<select name=\"public\" size=\"1\">";
    if( $row['Public'] == 1 ) {
      $public .= "<option value=\"0\">False</option>".
                 "<option selected value=\"1\">True</option></select></td>";
    } else {
      $public .= "<option selected value=\"0\">False</option>".
                 "<option value=\"1\">True</option></select></td>";
    }
    $group_list = "<td><select name=\"group\" size=\"1\">";
    if( !array_key_exists($row['GroupID'],$groups) ) {
      $group_list .= "<option selected value=\"0\">None.</option>";
    } else {
      $group_list .= "<option value=\"0\">None.</option>";
    }
    foreach( $groups as $key => $value ) {
      if( $row['GroupID'] == $key ) {
        $group_list .= "<option selected value=\"".$key."\">".
                       $value['GroupName']."</option>";
      } else {
        $group_list .= "<option value=\"".$key."\">".
                       $value['GroupName']."</option>";
      }
    }
	  $group_list .= "</select></td>";
	  $edit = "<td><input type=\"submit\" value=\" UPDATE \"></form></td>";

    $table[] = array($image_thumb,$roll_name,$roll_date,
                     $photo_count,$public,$group_list,$edit);
  }
  _print_rows($table);
  echo "\n\t\t\t\t\t</table>\n";
}
?>
