xquery version "3.0";
declare namespace xh="http://www.w3.org/1999/xhtml";
import module namespace response = "http://exist-db.org/xquery/response";

let $user := "admin"
let $pass := "foo"

let $dbroot := "/db/laceData/"

let $collectionPath := request:get-parameter('collectionPath', '')
(:  
let $collectionPath := "alciphronisrhet01schegoog/2016-04-03-16-14_teubner-serif-2013-12-16-11-26-00067000.pyrnn.gz_selected_hocr_output"
:)
(:  logs into the collection :)
let $dbpath := concat($dbroot, $collectionPath)
let $login := xmldb:login($dbpath, $user, $pass)
(: 
return doc("/db/laceData/alciphronisrhet01schegoog/2016-04-03-16-14_teubner-serif-2013-12-16-11-26-00067000.pyrnn.gz_selected_hocr_output")
:)

let $count := count(collection($dbpath)//xh:span[@data-manually-confirmed = 'true'])
let $total := count(collection($dbpath)//xh:span[@class="ocr_word"])
return ($count*100) div $total


