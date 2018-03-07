(function($) {
    var sl = {
        search: '#search',
        main: '.main', result: '.main',
        map_result: '.result .map'
    };

    function show(element) {
        element.removeClass('d-none');
    }

    function hide(element) {
        element.addClass('d-none');
    }

    $(document).ready(function() {
        $(sl.search).dropdown({
            maxSelections: 3,
            onChange: function(value, text, $selection) {
                var length = value.length;
                hide($(sl.result));
                if (length > 0 && length <= 3) {
                    show($('#result-' + length));
                }
            }
        });

        $(sl.map_result).on('document', 'click', function() {

        });
    });
})(jQuery)