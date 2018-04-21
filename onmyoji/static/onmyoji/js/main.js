(function($) {
    var sl = {
        search: '.search',
        main: '.main', result: '.main',
        map_result: '.result .map'
    };

    function show(element) {
        element.removeClass('d-none');
    }

    function hide(element) {
        element.addClass('d-none');
    }

    function csrf_token(obj) {
        var key = 'csrfmiddlewaretoken';
        var value = $('input[name="' + key + '"]').val();
        obj[key] = value;
        return obj;
    }

    function randomBackground() {
        var $target = $('#main_content');
        var available = [1, 2, 3];
        var img = available[Math.floor(Math.random() * available.length)];
        var img_path = $('#img_path').val();

        var old_bg = $target.css('background-image'),
            new_bg_source = 'url("' + img_path + img + '.jpg")'

        $target.css('background-image', old_bg.replace(/url\(.*\)/i, new_bg_source));
    }

    $(document).ready(function() {
        $(sl.search).dropdown({
            fullTextSearch: true,
            maxSelections: 3,
        });

        $('#find').submit(function(e) {
            e.preventDefault();
            var $submit = $(this).find('button[type="submit"]');
            if ($submit.hasClass('spinner')) {
                return;
            }

            var wanted = $('#wanted_search').dropdown('get value');
                var hint   = $('#hint_search').dropdown('get value');
            for (i in hint) {
                var wanted_id = $('#hint_search option[value=' + hint[i] + ']').data('wanted-id');
                if (wanted_id && wanted.indexOf(wanted_id) === -1) {
                    wanted.push(wanted_id);
                }
            }
            wanted = wanted.slice(0, 3);

            if (wanted.length > 0) {
                $.ajax({
                    url: '/find',
                    dataType: 'json',
                    method: 'POST',
                    data: csrf_token({data: wanted}),
                    beforeSend: function() {
                        $submit.addClass('spinner');
                    },
                    success: function(result) {
                        console.log(result);
                        if (result.success) {
                            if (result.html) {
                                $('#found_result').html(result.html);
                            }
                        } else {
                            alert(result.msg);
                        }
                    },
                    complete: function() {
                        $submit.removeClass('spinner');
                    }
                });
            }
        });

        $(document).on('click', 'a.location, a.hint_item', function(e) {
            e.preventDefault();
        });

        randomBackground();
    });
})(jQuery)