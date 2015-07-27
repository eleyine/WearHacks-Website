(function($) {
    "use strict"; // Start of use strict

    $( document ).ready(function() {

        ajaxSetup();
        stylisticTweaks();

        $(document).on('click', '#checkout', function (e) {
            prevalidateRegistration('#registration-form');
            e.preventDefault();

        } );
    });

    function prevalidateRegistration(form) {
        $('.checkout-wrapper .fa').addClass('hide');
        $('.checkout-wrapper .fa-paper-plane').removeClass('hide');
        $('#checkout .text').text('Validating your info');

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
                    registrationError(data["registration_message"]);
                } else {
                    checkout(formData, 200);
                }
            },
            error: function () {
                console.log('Server error');
                console.log(data);  
                displayServerError();
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

    function disableButtonError() {
      $('.fa').addClass('hide');
      $('#checkout .text').text('Sorry');
      $('#checkout').removeClass('waiting btn-primary');
      $('#checkout').addClass('disabled btn-danger');
    }

    function displayServerError() {
      disableButtonError();
      $('.message').addClass('hide');
      $('#server-error').removeClass('hide');
      $('#server-error').html("There is a temporary problem with " +
         "our server. Please refresh.</br>If the problem " +
         "persists, contact our support team.</br><strong>Don't  worry, we haven't captured your payment.</strong>");
    }

    function registrationError(message) {
      $('.message').addClass('hide');
      $('#registration-error').removeClass('hide');
      $('#registration-error').text(message);
      $('#checkout text').text("Gotcha, check me out.");
      $('html, body').stop().animate({
        scrollTop: ($('#registration-form').offset().top - 50)
      }, 1250, 'easeInOutExpo');
    }

    function checkout(formData, amount) {
        console.log("Amount: " + amount);
        $('.message').addClass('hide');
        $('.checkout-wrapper .fa').addClass('hide');
        $('.checkout-wrapper .fa-spinner').removeClass('hide');
        $('#checkout .text').text('Checking out...');
        var handler = StripeCheckout.configure({
            key: 'pk_test_wLynQ6aB7z7gx5vztfV37MVa',
            image: '/static/images/logo.png',
            token: function(token) {
                if (token.id) {
                  $('#checkout').addClass('token-was-obtained');
                }
                formData.append('token_id', token.id);
                formData.append('amount', amount);

                console.log("Atempting to charge with token id " + token.id);
                $.ajax({
                  url: '/register/',
                  type: 'post',
                  processData: false,
                  contentType: false,
                  data: formData,
                  success: function(data) {
                    if (data['server_error']) {
                      displayServerError();
                    } else if(!data["registration_success"]) {
                      registrationError(data["registration_message"]);
                    } else {
                      // Prevalidation has succeeded, user will proceed to checkout

                      if(!data["checkout_success"]) {
                        if (data["checkout_message"]) {
                          $('#checkout-error').removeClass('hide');
                          $('#checkout-error').html(data["checkout_message"]);
                          disableButtonError();
                        }
                      } else {
                        // both registration and checkout have succeeded
                        $('.checkout-wrapper .fa').addClass('hide');
                        $('.checkout-wrapper .fa-check').removeClass('hide');
                        $('#checkout').removeClass('waiting');
                        $('#checkout .text').text('Thank you');
                        $('#checkout').removeClass('btn-primary').addClass('disabled btn-success');
                        setTimeout(function(){ 
                          $('#success-message').removeClass('hide').text("Eventually send a confirmation email");
                        }, 2000);
                      }
                    }
                  },
                  error: function(data) {
                    console.log('Server error');
                    console.log(data);
                    displayServerError();
                  }
                }); // end ajax call
            }
        });

        // Open Checkout with further options
        handler.open({
          name: 'WearHacks Montreal 2015',
          description: 'The biggest wearable hackathon in North America',
          amount: amount,
          email: $('#id_email').val(),
          opened: function() {
            $('.checkout-wrapper .fa').addClass('hide');
            $('.checkout-wrapper .fa-paper-plane').removeClass('hide');
            $('#checkout .text').text('Stripe is now in charge...');
          },
          closed: function() {
            if ($('#checkout').hasClass('token-was-obtained')) {
              $('.checkout-wrapper .fa').addClass('hide');
              $('.checkout-wrapper .fa-spinner').removeClass('hide');
              $('#checkout').addClass('waiting');
              $('#checkout .text').text('Completing registration...');
              setTimeout(function(){ 
                if ($('#checkout').hasClass('waiting')) {
                  $('#checkout .text').text('This may take a while...');
                  setTimeout(function(){ 
                    if ($('#checkout').hasClass('waiting')) {
                      $('#checkout .text').text("So you want to be a hacker eh?");
                    }
                  }, 20000);
                }
              }, 5000);
            } else {
              restoreCheckoutButton();
            }
          }
        });
        // Close Checkout on page navigation
        $(window).on('popstate', function() {
            handler.close();
        });
    }

    function restoreCheckoutButton() {
      $('.checkout-wrapper .fa').addClass('hide');
      $('.checkout-wrapper .fa-lock').removeClass('hide');
      $('#checkout').removeClass('waiting token-was-obtained disabled btn-danger btn-success').addClass('btn-primary');
      $('#checkout .text').text('Checkout');
      $('.message').addClass('hide');
    }
})(jQuery); // End of use strict