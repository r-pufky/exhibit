<?
include("global.inc.php");
include("exhibit_permissions.inc.php");
__https();

_page_header("Exhibit: Roll Permissions Manager.");
_page_menu("exhibit");

if( $__user['Username'] != 'ADMIN_USER_ACCOUNT' ) {
  _page_section("error.png","Whoops.  Don't know what you are trying to do.");
  _page_footer();
  exit;
}

$action = $_REQUEST['action'];
if( $action == "" ) { $action = "rolls"; }

switch( $action ) {
  case 'groups': {
    $groupid = $_REQUEST['groupid'];
    $name = $_REQUEST['name'];
    $description = $_REQUEST['description'];
    $subaction = $_REQUEST['subaction'];
  
    switch( $subaction ) {
      case ' ADD GROUP ': {
        _page_sechead("exhibit.png","Group Management");
        _set_groups("add",$name,$description,0);
      } break;
      case ' DELETE ': {
        _page_sechead("exhibit.png","Group Management");
        _set_groups("delete",$name,$description,$groupid);
      } break;
      case ' UPDATE ': {
        _page_sechead("exhibit.png","Group Management");  
        _set_groups("update",$name,$description,$groupid);
      } break;
      default: {
        _page_sechead("exhibit.png","Group Management");
        _display_groups();
      } break;
    };
  } break;
  case 'users': {
    $groupid = $_REQUEST['groupid'];
    $userid = $_REQUEST['userid'];
    $subaction = $_REQUEST['subaction'];

    switch( $subaction ) {
      case ' ADD GROUP ': {
        _page_sechead("exhibit.png","User Management");
        _set_users("add",$userid,$groupid);
      } break;
      case ' DELETE ': {
        _page_sechead("exhibit.png","User Management");
        _set_users("delete",$userid,$groupid);
      } break;
      default: {
        _page_sechead("exhibit.png","User Management");
      } break;
    };
    _display_users();
  } break;
  case 'rolls':
  default: {
    $roll = $_REQUEST['roll'];
    $library = $_REQUEST['library'];
    $public = $_REQUEST['public'];
    $group = $_REQUEST['group'];
    if( !isset($roll) and !isset($library) ) {
      _page_sechead("exhibit.png","Roll Management");
      _display_permissions();
    } elseif( isset($public) and isset($group) ) {
      _page_sechead("exhibit.png","Roll Management");
      _set_permissions($roll,$library,$public,$group);
    } else {
      _page_sechead("error.png","An error occurred updating permissions.");
      _display_permissions();
    }
  } break;
};
_page_footer();
?>
