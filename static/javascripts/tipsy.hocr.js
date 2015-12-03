function get_filename() {
    var path_array = window.location.pathname.split("/")
    return path_array[path_array.length - 1]
}

$(function() {
    $('.ocr_word').tipsy({
        gravity: 'w',
        title: 'data-spellcheck-mode'
    });

    $('.ocr_word').on('keydown', function(e) {
        if (e.which == 13) {
            e.preventDefault();
            $(this).attr("data-spellcheck-mode", "Manual");
            var focusables = $(".ocr_word");
            var current = focusables.index(this);
            console.log(window.location);
            var path_array = window.location.pathname.split("/")
            console.log(path_array[path_array.length - 1])
            next = focusables.eq(current + 1).length ? focusables.eq(current + 1) : focusables.eq(0);
            next.focus();
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