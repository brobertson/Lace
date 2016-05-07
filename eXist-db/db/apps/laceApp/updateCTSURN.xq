xquery version "3.0";
declare namespace html="http://www.w3.org/1999/xhtml";

import module namespace response = "http://exist-db.org/xquery/response";

let $user := "admin"
let $pass := "foo"
let $dbroot := "/db/laceData/"
let $id := request:get-parameter('id', '')
let $label := request:get-parameter('label', '')
let $next_sibling_id := request:get-parameter('next_sibling_id','')
let $fileName := request:get-parameter('fileName', '')
let $filePath := request:get-parameter('filePath', '')
let $value :=  request:get-parameter('value','')

(:  logs into the collection :)
let $dbpath := concat($dbroot, $filePath)
let $login := xmldb:login($dbpath, $user, $pass)

  
let $foo1 := response:set-header("Access-Control-Allow-Origin", "*")

let $next_sibling := doc(concat($dbpath, '/', $fileName))//html:span[@id = $next_sibling_id]

let $foo3 := update  insert <html:span><html:label for="{$id}">New Work:</html:label><html:input  id="{$id}" data-cts-urn="{$value}" value="{$label}"
class="ui-autocomplete-input" autocomplete="off" readonly="readonly"/></html:span> preceding $next_sibling

return
    <html>
        <body>
            <p>
    login: {$login}
    </p>
    <p>
    filePath: {$filePath}
    </p>
    <p>
    fileName: {$fileName}
    </p>
    <p>
        ID: {$id}
        </p>
        <p>Foo3: {$foo3}
        </p>
    </body>
    </html>

