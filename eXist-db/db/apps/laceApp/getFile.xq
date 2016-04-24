xquery version "3.0";
declare namespace xh="http://www.w3.org/1999/xhtml";
import module namespace response = "http://exist-db.org/xquery/response";

let $user := "admin"
let $pass := "foo"

let $dbroot := "/db/laceTest/"
let $filePath := request:get-parameter('filePath', '')


(:  logs into the collection :)
let $dbpath := concat($dbroot, $filePath)
let $login := xmldb:login($dbpath, $user, $pass)
(: 
return doc("/db/laceTest/historiaerecogno02thucuoft/2016-01-16-13-14_porson-2013-10-23-16-14-00100000.pyrnn.gz_selected_hocr_output/historiaerecogno02thucuoft_0023.html")
:)

return doc($dbpath)
