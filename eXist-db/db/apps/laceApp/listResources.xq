xquery version "3.0";

declare option exist:serialize "method=xhtml media-type=text/html indent=yes";

let $data-collection := '/db/lace/490021999brucerob/2015-12-23-07-46_porson-2013-10-23-16-14-00100000/'
let $q := 'the'

(: put the search results into memory using the eXist any keyword ampersand equals comparison :)
let $search-results := collection($data-collection)//*[ft:query(*, $q)]
let $count := count($search-results)

return
<html>
    <head>
       <title>Term Search Results</title>
     </head>
     <body>
        <h3>Term Search Results</h3>
        <p><b>Search results for:</b>&quot;{$q}&quot; <b> In Collection: </b>{$data-collection}</p>
        <p><b>Terms Found: </b>{$count}</p>
     <ol>{
           for $term in $search-results
              let $id := $term/id
              let $term-name := $term/term-name/text()
              order by upper-case($term-name)
          return
            <li>
               <a href="../views/view-item.xq?id={$id}">{$term-name}</a>
            </li>
      }</ol>
      <a href="search-form.html">New Search</a>
      <a href="../index.html">App Home</a>
   </body>
</html>
