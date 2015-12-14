<?
include("global.inc.php");
include("exhibit.inc.php");

$roll = $_REQUEST['roll'];
$library = $_REQUEST['library'];
$search = $_REQUEST['search'];
$keyword1 = $_REQUEST['key1'];
$keyword2 = $_REQUEST['key2'];
$keyword3 = $_REQUEST['key3'];
$restriction = $_REQUEST['restriction'];

_page_header("Exhibit: iPhoto the way you want it.");
_page_menu("exhibit");

if( $search == 1 ) {
  if( $restriction == "ANY" ) {
    $search_table = "Search1";
    $keywords = array();
    if( $keyword1 != "" ) { $keywords[] = $keyword1; }
    if( $keyword2 != "" ) { $keywords[] = $keyword2; }
    if( $keyword3 != "" ) { $keywords[] = $keyword3; }
    if( sizeof($keywords) >= 1 ) {
      _create_search_heap($search_table);
      $search_query = "SELECT * FROM exhibit_".$search_table." WHERE (".
                      "Keyword='".$keywords[0]."'";
      $search_text = "(Any) ".$keywords[0];
      _generate_search_images($search_table,$keywords[0],False);    
      for( $x=1; $x < sizeof($keywords); $x++ ) {
        _generate_search_images($search_table,$keywords[$x],False);
        $search_query .= " OR Keyword='".$keywords[$x]."'";
        $search_text .= ", ".$keywords[$x];
      }
      $search_query .= ") AND ".
                       _user_permissions($__user['Username'],'query').
                       "GROUP BY ImageID, iPhotoLibraryID LIMIT 1000";
    } else {
      $search_query = "SELECT * FROM exhibit_".$search_table.
                      "WHERE ".
                      _user_permissions($__user['Username'],'query').
                      " LIMIT 1000";
    }
    _display_search($search_query,$search_text);
    __query("DROP TABLE exhibit_".$search_table,"","");
  } else {
    $source = "Search1";
    $target = "Search2";
    $temp_table = "";
    _create_search_heap($source);
    _create_search_heap($target);
    $keywords = array();
    if( $keyword1 != "" ) { $keywords[] = $keyword1; }
    if( $keyword2 != "" ) { $keywords[] = $keyword2; }
    if( $keyword3 != "" ) { $keywords[] = $keyword3; }
    if( sizeof($keywords) >= 1 ) {
      _generate_search_images($source,$keywords[0],True);
      $search_text = "(All) ".$keywords[0];
      for( $x=1; $x < sizeof($keywords); $x++ ) {
        __query("TRUNCATE TABLE exhibit_".$target,"","");
        _generate_search_comparison($source,$keywords[$x],$target);
        $temp_table = $target;
        $target = $source;
        $source = $temp_table;
        $search_text .= ", ".$keywords[$x];
      }
    }
    // source will always contain final results due to for loop.
    $search_query = "SELECT * FROM exhibit_".$source." WHERE ".
                    _user_permissions($__user['Username'],'query').
                    " GROUP BY ImageID, iPhotoLibraryID LIMIT 1000";
    _display_search($search_query,$search_text);
    __query("DROP TABLE exhibit_".$source,"","");
    __query("DROP TABLE exhibit_".$target,"","");
  }  
} elseif( $roll and $library ) {
  _display_images($roll, $library, $__user['Username']);
} else {
  _display_rolls($__user['Username']);
}

_page_section("search.png","Search for photos");
_draw_search_key();
_page_footer();
?>
