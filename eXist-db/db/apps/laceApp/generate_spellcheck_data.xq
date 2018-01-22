xquery version "3.0";

declare namespace util="http://exist-db.org/xquery/util";
declare namespace xh="http://www.w3.org/1999/xhtml";
import module namespace response = "http://exist-db.org/xquery/response";

let $user := "admin"
let $pass := "foo"

let $dbroot := "/db/laceData/"
(:
let $filePath := request:get-parameter('filePath', '')
:)
let $filePath := "liveswithenglish06plutuoft/2016-04-19-07-46_loeb_2016-03-20-14-17-00128200.pyrnn.gz_selected_hocr_output"
(:  let $filePath := "alciphronisrhet01schegoog/2016-04-03-16-14_teubner-serif-2013-12-16-11-26-00067000.pyrnn.gz_selected_hocr_output"
:)
(:  logs into the collection :)
let $dbpath := concat($dbroot, $filePath)
let $login := xmldb:login($dbpath, $user, $pass)

(: Test code for sanity checks
return doc("/db/laceData/historiaerecogno02thucuoft/2016-01-16-13-14_porson-2013-10-23-16-14-00100000.pyrnn.gz_selected_hocr_output/historiaerecogno02thucuoft_0023.html")
return doc($dbpath)
return collection($dbpath)//xh:span[@data-manually-confirmed = 'true']
:)
let $blocks := collection($dbpath)//xh:span[@class="ocr_line" and not(contains(util:collection-name(.), "raw_hocr_output")) and not(xh:span/@data-manually-confirmed="false")]
(: 
return count($blocks)
:)
for $select_block in $blocks
(:[position() >= 100 and not(position() > 105)]:)
return
    <lines>
    <line>
        <image>
            {$select_block/ancestor::xh:body/xh:div[@class="ocr_page"]/@title}
        </image>
        <bbox>
            {$select_block/@title}
        </bbox>
        <path>
            {util:collection-name($select_block)}
        </path>
        <verifiedText>
{let $select_words := $select_block/xh:span[@class="ocr_word"]
        for $select_word in $select_words
          return $select_word/string()}
        </verifiedText>
        <spellcheckedText>
        {let $select_words := $select_block/xh:span[@class="ocr_word"]
        for $select_word in $select_words
            return 
                
                if ($select_word/@data-selected-form) then
                    $select_word/@data-selected-form/string()
                else($select_word/string())
        }
        </spellcheckedText>
        <rawText>
            {let $select_words := doc(concat(replace(util:collection-name($select_block),'selected_hocr_output','raw_hocr_output'),'/',util:document-name($select_block)))//xh:span[@title=$select_block/@title]/xh:span[@class="ocr_word"]
                for $select_word in $select_words
                return
                    $select_word/string()
                    }
        </rawText>
    </line>
    </lines>
