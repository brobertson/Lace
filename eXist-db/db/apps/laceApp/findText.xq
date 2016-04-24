xquery version "3.0";
declare namespace xh="http://www.w3.org/1999/xhtml";
declare base-uri "http://www.w3.org/1999/xhtml";
(:  
import module namespace kwic="http://exist-db.org/xquery/kwic" at "xmldb:exist:///db/test/kwic.xql";
:)
declare option exist:serialize "method=xhtml media-type=text/html indent=yes";
import module namespace response = "http://exist-db.org/xquery/response";
let $user := "admin"
let $pass := "foo"
let $dbroot := "/db/laceTest/"

let $collectionPath := request:get-parameter('collectionPath', '')
let $query := request:get-parameter('query', '')
let $filtered-query := replace($query, "[&amp;&quot;-*;-`~!@#$%^*()_+-=\[\]\{\}\|';:/.,?(:]", "")
let $data-collection := '/db/laceTest/830740755brucerob/2016-03-22-19-31_loeb_2016-03-20-14-17-00128200.pyrnn.gz_selected_hocr_output'


(:  logs into the collection :)
let $dbPath := concat($dbroot, $collectionPath)
let $login := xmldb:login($dbPath, $user, $pass)

(: put the search results into memory using the eXist any keyword ampersand equals comparison
:)
let $search-results := collection($dbPath)//xh:span[@class='ocr_word'][text()=$query]
let $count := count($search-results)

let $processed-results := 
    for $result in $search-results
    let $bbox := $result/@title
    let $book_name := util:collection-name(util:collection-name($result))
    let $page_file :=util:document-name($result)
    let $spellchecked-form := $result/@data-spellchecked-form/string()
    let $word := $result/text()
    return
        <div><span>{$spellchecked-form}</span> <span>{$word}</span>
            
            <img src="http://heml.mta.ca/secretlace/image_test?book={xmldb:encode-uri($book_name)}&amp;file={xmldb:encode-uri($page_file)}&amp;bbox={xmldb:encode-uri($bbox)}" alt='a word image'/>
        </div>
return
<html>
<head>
    <title>Keyword Search</title>
    <style>
        body {{ 
            font-family: arial, helvetica, sans-serif; 
            font-size: small 
            }}
        div.result {{ 
            margin-top: 1em;
            margin-bottom: 1em;
            border-top: 1px solid #dddde8;
            border-bottom: 1px solid #dddde8;
            background-color: #f6f6f8; 
            }}
        #search-pagination {{ 
            display: block;
            float: left;
            text-align: center;
            width: 100%;
            margin: 0 5px 20px 0; 
            padding: 0;
            overflow: hidden;
            }}
        #search-pagination li {{
            display: inline-block;
            float: left;
            list-style: none;
            padding: 4px;
            text-align: center;
            background-color: #f6f6fa;
            border: 1px solid #dddde8;
            color: #181a31;
            }}
        span.hi {{ 
            font-weight: bold; 
            }}
        span.title {{ font-size: medium; }}
        span.url {{ color: green; }}
    </style>
</head>
<body>
    <h1>Keyword Search</h1>
    <!--div id="searchform">
        <form method="GET">
            <p>
                <strong>Keyword Search:</strong>
                <input name="query" type="text" value="{$query}"/>
                <input name="collectionPath" type="text" value="{$collectionPath}"/>
            </p>
            <p>
                <input type="submit" value="Search"/>
            </p>
        </form>
    </div-->
    <h2>Results for keyword search &quot;{$query}&quot;</h2>
    {
    if (empty($search-results)) then ()
    else
        (
        <div id="searchresults">{$processed-results}</div>
        )
    }
</body>
</html>
