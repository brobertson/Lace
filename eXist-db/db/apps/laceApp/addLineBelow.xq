xquery version "3.0";
declare namespace html="http://www.w3.org/1999/xhtml";

import module namespace response = "http://exist-db.org/xquery/response";

let $user := "admin"
let $pass := "foo"
let $dbroot := "/db/laceData/"
let $id := request:get-parameter('id', '')
let $new := request:get-parameter('value', '')
let $fileName := request:get-parameter('fileName', '')
let $filePath := request:get-parameter('filePath', '')
let $uniq :=  request:get-parameter('uniq','')

(:  logs into the collection :)
let $dbpath := concat($dbroot, $filePath)
let $login := xmldb:login($dbpath, $user, $pass)


let $foo1 := response:set-header("Access-Control-Allow-Origin", "*")
let $word := doc(concat($dbpath, '/', $fileName))//html:span[@id = $id]

let $line := $word/..
let $foo3 := update  insert <html:span id='{$uniq}' class='inserted_line' data-manually-confirmed='false' contenteditable='true'/> following $line

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
