xquery version "3.0";
declare namespace xhtml="http://www.w3.org/1999/xhtml";
let $words := collection('/db/laceData/830740755brucerob')//xhtml:span[@class='ocr_word']
for $word in $words
let $foo3 := update  insert attribute data-selected-form  {$word/text()} into $word
return 
    $word

