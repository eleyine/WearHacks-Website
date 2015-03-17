var UXModule = (function ($) {
    $( document ).ready(function() {

        // Search bar
        $('.search-icon').click(function () {
            $('.searchbox').toggleClass('expanded');
            $('.searchbox input').focus();
        });
        $('.searchbox input').on('blur', function () {
            $('.searchbox').removeClass('expanded');
            var that = this;
            setTimeout(function() {
                $(that).val('');
            }, 800);
        });

        // Masonry Responsive Grid
        var container = document.querySelector('#container');
        if (container) {
            var msnry = new Masonry( container, {
                columnWidth: '.note-container',
                itemSelector: '.note-container',
                gutter: 0,
                containerStyle: null
            });
        }

        // Initialize all tooltips
        $('[data-toggle="tooltip"]').tooltip();

        console.log("hi")

        var my = {
            'msnry': msnry
        }
        return my;
    });
})($);