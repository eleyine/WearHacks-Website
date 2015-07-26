(function($) {
    "use strict"; // Start of use strict

    $( document ).ready(function() {

        ajaxSetup();
        stylisticTweaks();
    
        // $(document).on('click', '#register', function (e) {
        //     prevalidateRegistration('#registration-form');
        //     e.preventDefault();
        //     console.log('Cool');

        // } );

        $(document).on('click', '#id_pay', function (e) {
            prevalidateRegistration('#registration-form');
            e.preventDefault();
            console.log('Cool');

        } );
    });

    function prevalidateRegistration(form) {
        console.log($(form).serialize());
        var formData = new FormData($(form)[0]);
        $.ajax({
            processData: false,
            contentType: false,
            url: "/register/",
            type: "POST",
            data: formData,
            success: function(data) {
                $(form).replaceWith(data['form_html']);
                stylisticTweaks();

                if (!(data['registration_success'])) {
                    $('html, body').stop().animate({
                      scrollTop: ($(form).offset().top - 50)
                      }, 1250, 'easeInOutExpo');
                    $('#error_id_pay').removeClass('hide');
                    $('#register').addClass('disabled');

                    // Here we replace the form, for the
                    $.snackbar({content: 'There were errors.' });
                }
                else {
                    $('#error_id_pay').addClass('hide');
                    checkout(formData);
                    // Here you can show the user a success message or do whatever you need
                    // $.snackbar({content: 'Registration successful.' });
                    // $(form).find('.success-message').show();
                }
            },
            error: function () {
                $('#register').addClass('disabled');
                $(form).find('.error-message').show();
            }
        });
    }

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
    }

    function stylisticTweaks() {
        $(".checkboxinput").bootstrapSwitch();
        $('#div_id_gender select').prepend('<option disabled selected> Select gender </option>');
    }

    function checkout(formData) {


        var handler = StripeCheckout.configure({
            key: 'pk_test_wLynQ6aB7z7gx5vztfV37MVa',
            image: '/static/images/logo.png',
            token: function(token) {
                formData.append('token_id', token.id);
                console.log("Atempting to charge with token id " + token.id);
                $.ajax({
                  url: '/register/',
                  type: 'post',
                  processData: false,
                  contentType: false,
                  data: formData,
                  success: function(data) {
                    if (data["success"]) {
                        console.log("Card successfully charged!");
                        $('#register').removeClass('disabled');
                        $('#error_id_pay').addClass('hide');

                        $('#id_pay').text('Thank you for registering');
                        $('#id_pay').addClass('disabled');

                    }
                    else {
                        console.log(data);
                        $('#id_pay').text('Error processing payment');
                        $('#id_pay').addClass('btn-error').removeClass('btn-success');
                        $('#error_id_pay').removeClass('hide');

                        console.log("Success Error!");
                    }

                  },
                  error: function(data) {
                    console.log("Ajax Error!");
                    console.log(data);
                  }
                }); // end ajax call
            }
        });

        // Open Checkout with further options
        handler.open({
          name: 'WearHacks Montreal 2015',
          description: 'The biggest wearable hackathon in North America',
          amount: 2000,
          email: $('#id_email').val(),
          opened: function() {
            console.log("Checkout has been opened.");
            $('#id_pay').text('Processing...');
          },
          closed: function() {
            console.log("Checkout has been closed.");
          }
        });
        // Close Checkout on page navigation
        $(window).on('popstate', function() {
            handler.close();
        });
    }

})(jQuery); // End of use strict