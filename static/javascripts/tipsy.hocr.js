function get_filename() {
    var path_array = window.location.pathname.split("/")
    return path_array[path_array.length - 1]
}

function update_xmldb(element) {
            var data = {};
            data['value'] = $(element).text();
            data['id'] = element.id;
            doc = $('.ocr_page').attr('title')
            data['doc'] = doc
            var n = doc.lastIndexOf('/');
            var fileName = doc.substring(n + 1);
            data['fileName'] = fileName
            var filePath = doc.substring(0,n);
            data['filePath'] = filePath
            $.post('http://heml.mta.ca:8080/exist/apps/laceApp/updateWord.xq',data)
}

$(function() {
    $('.ocr_word').tipsy({
        gravity: 'w',
        title: 'data-spellcheck-mode'
    });

    $('.ocr_word').on('keydown', function(e) {
        if (e.which == 13) {
            e.preventDefault();
            var data = {};
            console.log(this.constructor.name);
            update_xmldb(this);
            /*alert($(this).text());
	    data['value'] = $(this).text();
            data['id'] = this.id;
            doc = $('.ocr_page').attr('title')
            data['doc'] = doc
            $.post('http://heml.mta.ca:8080/exist/apps/laceApp/updateWord.xq',data)
*/
            $(this).attr("data-spellcheck-mode", "Manual");
            var focusables = $(".ocr_word");
            var current = focusables.index(this);
            var path_array = window.location.pathname.split("/")
            next = focusables.eq(current + 1).length ? focusables.eq(current + 1) : focusables.eq(0);
            if (e.shiftKey == true) {
              //First, make sure we don't get into endless loop when all are edited. Next only rip through the ones that are True,
              //Edited (Manual) or TrueLower
              while (focusables.index(next) != 0 && ($(next).attr("data-spellcheck-mode") === "True" || $(next).attr("data-spellcheck-mode") === "Manual" || $(next).attr("data-spellcheck-mode") === "TrueLower")){
                update_xmldb(next);
                console.log(next.constructor.name);
                console.log(next);
                $(next).attr("data-spellcheck-mode", "Manual");
                next_index = focusables.index(next);
		alert(next_index);
                next = focusables.eq(next_index + 1).length ? focusables.eq(next_index + 1) : focusables.eq(0);
                }
            }
            next.focus()
            var all_manually_edited = true;
            $(".ocr_word").each(function(index, element) {
                if ($(element).attr("data-spellcheck-mode") !== "Manual") {
                    all_manually_edited = false;
                }
            });
            if (all_manually_edited) {
                $('#download').attr('style', "display: block;");
            }
            var name = get_filename();
            $('#download').attr('download', name);
        }
    });
});
