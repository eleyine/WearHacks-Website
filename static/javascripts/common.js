(function($) {
    "use strict"; // Start of use strict

    $( document ).ready(function() {
        ajaxSetup();
        langSetup();
    });
    function ajaxSetup() {
        // Protect against CSRF using a csrf_token
        // For more information: https://docs.djangoproject.com/en/dev/ref/csrf/
        var csrftoken = $.cookie('csrftoken');
        function csrfSafeMethod(method) {
          // these HTTP methods do not require CSRF protection
          return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        // Setup ajax 
        $.ajaxSetup({
          beforeSend: function(xhr, settings) {
              if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                  xhr.setRequestHeader("X-CSRFToken", csrftoken);
              }
          },
        });
        console.log("Ajax properly setup");
    }
    function langSetup() {
        $("a.lang").on("click", function(e){
            var lang = $(this).attr('id')
            $.ajax({
                url: "/i18n/setlang/",
                type: "POST",
                data: {
                    language: lang
                },
                success: function () {
                    console.log("Language properly set");

                },
                error: function (data) {
                    console.log("Could not set language");
                    console.log(data);
                }
            });
        });
        
    }
})(jQuery); // End of use strict    