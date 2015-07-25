(function($) {
    "use strict"; // Start of use strict

    // Protect against CSRF using a csrf_token
    // For more information: https://docs.djangoproject.com/en/dev/ref/csrf/
    // var csrftoken = $.cookie('csrftoken');
    // function csrfSafeMethod(method) {
    //   // these HTTP methods do not require CSRF protection
    //   return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    // }

    // // Setup ajax 
    // $.ajaxSetup({
    //   beforeSend: function(xhr, settings) {
    //       if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
    //           xhr.setRequestHeader("X-CSRFToken", csrftoken);
    //       }
    //   },
    // });

    $( document ).ready(function() {

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

    
        $(document).on('click', '#register', function () {
            console.log('click!');
            var form = '#registration-form';
            console.log($(form).serialize());
            $.ajax({
                url: "/register/",
                type: "POST",
                data: $(form).serialize(),
                success: function(data) {
                    $(form).replaceWith(data['form_html']);
                    if (!(data['success'])) {
                        // Here we replace the form, for the
                        $.snackbar({content: 'There were errors.' });
                    }
                    else {
                        // Here you can show the user a success message or do whatever you need
                        $.snackbar({content: 'Registration successful.' });
                        $(form).find('.success-message').show();
                    }
                },
                error: function () {
                    $(form).find('.error-message').show();
                }
            });

            console.log('Cool');

        } );
    });

})(jQuery); // End of use strict