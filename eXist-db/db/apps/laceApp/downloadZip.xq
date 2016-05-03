xquery version "3.0";

import module namespace response = "http://exist-db.org/xquery/response";
declare option exist:serialize "method=html5 media-type=text/html omit-xml-declaration=yes indent=yes";

let $user := "admin"
let $pass := "foo"

let $dbroot := "/db/laceData/"

let $collectionPath := request:get-parameter('collectionPath', '')

(:  logs into the collection :)
let $dbpath := concat($dbroot, $collectionPath)
let $login := xmldb:login($dbpath, $user, $pass)
let $zipName := request:get-parameter('zipName','')

let $compressed-collection := compression:zip(xs:anyURI($dbpath),true(), $dbroot)

return response:stream-binary($compressed-collection, "application/zip", $zipName)

