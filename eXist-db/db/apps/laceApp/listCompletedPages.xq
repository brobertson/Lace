xquery version "3.0";
declare namespace xhtml="http://www.w3.org/1999/xhtml";
<texts>{
for $p in collection('/db/laceData')
where every $w in $p//xhtml:span[@class='ocr_word'] satisfies ($w/@data-spellcheck-mode='Manual' or $w/@data-manually-confirmed='true')
order by util:document-name($p)

return 
    <completedtext>{util:collection-name($p)}/{util:document-name($p)}</completedtext>
}
</texts>
