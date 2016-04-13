xquery version "3.0";
declare namespace xh="http://www.w3.org/1999/xhtml";
declare base-uri "http://www.w3.org/1999/xhtml";

declare option exist:serialize "method=xhtml media-type=text/html indent=yes";
import module namespace response = "http://exist-db.org/xquery/response";
let $user := "laceUser"
let $dbroot := "/db/laceTest/"

let $collectionPath := request:get-parameter('collectionPath', '')
let $query := request:get-parameter('query', '')
let $correctedForm := request:get-parameter('correctedForm','')
let $filtered-query := replace($query, "[&amp;&quot;-*;-`~!@#$%^*()_+-=\[\]\{\}\|';:/.,?(:]", "")
let $data-collection := '/db/laceTest/830740755brucerob/2016-03-22-19-31_loeb_2016-03-20-14-17-00128200.pyrnn.gz_selected_hocr_output'


(:  logs into the collection :)
let $dbPath := concat($dbroot, $collectionPath)
let $login := xmldb:login($dbPath, $user, $user)
let $foo1 := response:set-header("Access-Control-Allow-Origin", "*")
(: put the search results into memory using the eXist any keyword ampersand equals comparison
:)
let $search-results := collection($dbPath)//xh:span[@class='ocr_word'][text()=$query]
let $count := count($search-results)

let $processed-results := 
    for $result in $search-results
    let $foo3 := update  value $result/@data-manually-confirmed with 'true'
(:  ::)
    let $foo4 := update value $result with $correctedForm
    return
        <p/>
return
<html>
<body>
    <p>'{$query}' corrected to '{$correctedForm}' {$count} times.</p>
</body>
</html>

