xquery version "3.0";
declare namespace xhtml="http://www.w3.org/1999/xhtml";
let $words := collection('/db/laceData/porphyriiphilos03naucgoog')//xhtml:span[@class='ocr_word'][not(@data-manually-confirmed)]
for $word in $words
return
update  insert attribute data-manually-confirmed  {'false'} into $word
