(function($, Date, _, pgettext, interpolate) {
    "use strict"; // Start of use strict

    $( document ).ready(function() {

        // ajaxSetup();
        displayCorrectButtons();
        $("#div_id_is_student .controls").append('<div class="controls col-lg-6 hide" id="hint_id_is_student"><p class="help-block message-success"><i class="fa fa-check"></i><strong> Great! You have a 50% discount.</strong></p></div>');
        stylisticTweaks();

        $(document).on('click', '.register-action', function (e) {
            register();
            e.preventDefault();
        } );
    });

    // Strings that need to be translated
    var strCheckout = _('Checkout');
    var strCheckoutInProgress = _('Checking out');
    var strCheckoutProceed = _('Proceed to checkout');
    var strGotcha = pgettext('Appears when user has form validation error and needs to resubmit', 'Gotcha');
        console.log(strGotcha);
    var strValidatingInfo = _('Validating your info');
    var strValidRegistration = _('Valid Registration');
    var strSorry = _('Sorry');
    var strThankYou = _('Thank you');
    var strServerError = pgettext( 
            "AJAX error",
           "There is a temporary problem with our server. Please refresh.</br>" +
           "If the problem persists, contact our support team.</br>"+
           "<strong>Don't  worry, we haven't charged you.</strong>");
    var strCheckintOut = _('Checking out');
    var strEarlyBird = pgettext("Make sure you keep the trailing space", 'Early Bird Ticket ');
    var strStudent = pgettext("Make sure you keep the trailing space", "Student ");
    var strRegular = pgettext('Regular ticket, make sure to keep trailing space', 'Ticket ');
    var strDiscount = pgettext('Discount text', '%i%% Off');
    var strOrgName = pgettext('Name that appears on Stripe popout', 'WearHacks Montreal 2015');
    var strStripeInAction = _('Stripe doing its magic');
    var strCompletingRegistration = _('Completing registration');
    var strPlsWait = _('This may take a while...');
    var strSmallTalk = pgettext('Appears to entertain user when registration validation takes too long', 'So you want to be a hacker eh?');
    var strTicketDescription = pgettext('Ticket Description', 'Ticket');
    var strTicketEarlyBirdDescription = pgettext('Ticket Description', 'Early Bird Ticket');
    var strTicketStudentDescription = pgettext('Ticket Description', 'Student Ticket');
    var strTicketStudentEarlyBirdDescription = pgettext('Ticket Description', 'Early Bird Student Ticket');

    function enabledFormControls(isEnabled) {
      $('input').attr('readOnly', !isEnabled);
      $('textarea').attr('readOnly', !isEnabled);
      $('input').attr('disabled', !isEnabled);
      $('select').attr('disabled', !isEnabled);
      $('textarea').attr('disabled', !isEnabled);
      $("#about-you .checkboxinput").bootstrapSwitch('disabled', !isEnabled);
      $("#about-you .checkboxinput").bootstrapSwitch('readonly', !isEnabled);
    }

    function displayCorrectButtons(isMobile, isRegistrationValidated) {
      if (isMobile === undefined)
        var isMobile = checkIfMobileOrTablet();

      if (isMobile) {
        $('.desktop').remove();
        $('.mobile').removeClass('hide');
        if (isRegistrationValidated) {
          enabledFormControls(false);
          $('#checkout.mobile').removeClass('hide').removeClass('disabled');
          $('#register.mobile').addClass('disabled btn-success').removeClass('btn-primary');
          $('#register.mobile .fa').addClass('hide');
          $('#register.mobile .fa-check').removeClass('hide');
          $('#register.mobile .text').text(strValidRegistration);
          $('#hint_checkout').removeClass('hide');
        } else {
          enabledFormControls(true);
          $('#checkout.mobile').addClass('hide');
          $('#register.mobile').removeClass('disabled btn-success').addClass('btn-primary');
          $('#register.mobile .fa').addClass('hide');
          $('#register.mobile .fa-paper-plane').removeClass('hide');
          $('#hint_checkout').addClass('hide');
        }
      } else {
        $('.desktop').removeClass('hide');
        $('.mobile').remove();
      }
    }

    function register() {
      var isMobile = checkIfMobileOrTablet();
      displayCorrectButtons(isMobile, false);
      
      // code for desktop
      if (!isMobile) {
        validateRegistration('#registration-form', isMobile, {
          success: function(checkoutHandler, formData, amount) {
            displayCorrectButtons(isMobile, true);
            enabledFormControls(false);
            desktopCheckout(checkoutHandler, formData, amount);
          },
          error: function(formData, amount){
            displayCorrectButtons(isMobile, false);
          }
        });
      } else {
        validateRegistration('#registration-form', isMobile, {
          success: function(checkoutHandler, formData, amount) {
            enabledFormControls(false);
            displayCorrectButtons(isMobile, true);
            mobileCheckout(checkoutHandler, formData, amount);
          },
          error: function(formData, amount){
            displayCorrectButtons(isMobile, false);
          }
        });
      }

    }

    function checkIfMobileOrTablet() {
      var check = false;
      (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
      // Set to !check to test on browser
      return check;
    }

    function validateRegistration(form, isMobile, options) {
        displayCorrectButtons(isMobile, false);
        $('.checkout-wrapper .fa').addClass('hide');
        $('.checkout-wrapper .fa-spinner').removeClass('hide');
        $('.register-action .text').text(strValidatingInfo);

        var formData = new FormData($(form)[0]);
        var lang = document.documentElement.lang;
        formData.append("lang", lang);
        $.ajax({
            processData: false,
            contentType: false,
            url: "/" + lang + "/register/",
            type: "POST",
            data: formData,
            success: function(data) {
                $(form).replaceWith(data['form_html']);
                stylisticTweaks();
                var amount = getChargeAmount();

                if (!data['registration_success']) {
                    options.error(formData, amount);
                    registrationError(data["registration_message"]);
                } else {
                    var handler = getCheckoutHandler(formData, amount);
                    options.success(handler, formData, amount);
                    $(window).on('popstate', function() {
                        handler.close();
                    });
                }
            },
            error: function (data) {
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
        $(".conduct ~ a")
          .attr("href", window.code_of_conduct)
          .attr("target", "_blank");
        $("#about-you .checkboxinput").bootstrapSwitch();
        $("#div_id_is_student .checkboxinput").on('switchChange.bootstrapSwitch', function(event, state) {
          if (state) {
            $("#hint_id_is_student").removeClass("hide");
          } else {
            $("#hint_id_is_student").addClass("hide");            
          }
        });     
        $("#div_id_is_first_time_hacker .checkboxinput").on('switchChange.bootstrapSwitch', function(event, state) {
          var is_returning = "#div_id_is_returning .checkboxinput";
          if (state && $(is_returning).val()) {
            $(is_returning).bootstrapSwitch('state', false);
          }
        }); 
        $("#div_id_is_returning .checkboxinput").on('switchChange.bootstrapSwitch', function(event, state) {
          var is_first_time_hacker = "#div_id_is_first_time_hacker .checkboxinput";
          if (state && $(is_first_time_hacker).val()) {
            $(is_first_time_hacker).bootstrapSwitch('state', false);
          }
        });     
    }

    function displaySorryButton() {
      $('.fa').addClass('hide');
      $('#checkout .text').text('Sorry');
      $('.checkout-action').removeClass('waiting btn-primary');
      $('.checkout-action').addClass('disabled btn-danger');
    }

    function displayThankYouButton(message) {
      $('.checkout-wrapper .fa').addClass('hide');
      $('.checkout-wrapper .fa-check').removeClass('hide');
      $('.checkout-action').removeClass('waiting');
      $('#checkout .text').text(strThankYou);
      $('.checkout-action').removeClass('btn-primary').addClass('disabled btn-success');
      setTimeout(function(){ 
        if (message) {
          $('#success-message').removeClass('hide').text(message);
        }
      }, 2000);
    }
    function displayServerError(message) {
      displaySorryButton();
      $('.message').addClass('hide');
      $('#server-error').removeClass('hide');
      if (message) {
        $('#server-error').html(message);
      } else {
        $('#server-error').html(strServerError);
      }
    }

    function registrationError(message) {
      stylisticTweaks();
      restoreCheckoutButton();
      $('#registration-error').removeClass('hide');
      $('#registration-error').text(message);
      $('.register-action .text').text(strGotcha);
      $('html, body').stop().animate({
        scrollTop: ($('#registration-form').offset().top - 50)
      }, 1250, 'easeInOutExpo');
    }

    function displayIsCheckingOut() {
      $('.message').addClass('hide');
      $('.checkout-action .fa').addClass('hide');
      $('.checkout-action .fa-spinner').removeClass('hide');
      $('#checkout .text').text(strCheckoutInProgress);
    }

    function mobileCheckout(handler, formData, amount) {
      $('#checkout.mobile .text').text(strCheckoutProceed);
      $('#checkout.mobile .fa').addClass('hide');
      $('#checkout.mobile .fa-lock').removeClass('hide');
      var handler = getCheckoutHandler(formData, amount);
      $('#checkout.mobile').one("click", function() {
        openCheckhoutHandler(handler, amount, formData["email"]);
      });
    }

    function getCheckoutHandler(formData, amount){
      var handler = StripeCheckout.configure({
            key: window.stripe_pk,
            image: '/static/images/logo.png',
            token: function(token) {
                if (token.id) {
                  $('.checkout-action').addClass('token-was-obtained');
                }
                formData.append('token_id', token.id);
                formData.append('amount', amount);
                // formData.append("lang", lang);
                var lang = document.documentElement.lang;
                $.ajax({
                  url: '/' + lang + '/register/',
                  type: 'post',
                  processData: false,
                  contentType: false,
                  data: formData,
                  success: function(data) {
                    if (data['server_error']) {
                      displayServerError(data['server_message']);
                    } else if(!data["registration_success"]) {
                      registrationError(data["registration_message"]);
                    } else {
                      // Prevalidation has succeeded, user will proceed to checkout
                      if(!data["checkout_success"]) {
                        if (data["checkout_message"]) {
                          $('#checkout-error').removeClass('hide');
                          $('#checkout-error').html(data["checkout_message"]);
                          displaySorryButton();
                        }
                      } else {
                        // both registration and checkout have succeeded
                        if (data["success_message"]) {
                          displayThankYouButton(data["success_message"]);
                        } else {
                          displayThankYouButton();                          
                        }
                      }
                    }
                  },
                  error: function(data) {
                    displayServerError();
                  }
                }); // end ajax call
            }
        });
      return handler;
    }

    function isStudent() {
      return $("#div_id_is_student .checkboxinput").prop("checked");
    }

    function isEarlyBird() {
      return Date.today() < new Date("9/15/2015");
    }

    function getChargeAmount() {
      var amount = isStudent()? 10: 20;
      amount = isEarlyBird()? amount * 0.5: amount;
      // in cents
      return amount * 100;
    }

    function getPercentDiscount() {
      var percent = isEarlyBird()? 0.5: 1;
      percent = isStudent()? percent * 0.5: percent;
      return (1 - percent) * 100;
    }

    function openCheckhoutHandler(handler, amount, email) {
      var isBird = isEarlyBird();
      var description = "";
      if (!isStudent()) {
        description = isBird? strTicketEarlyBirdDescription: strTicketDescription;
      } else {
        description = isBird? strTicketStudentEarlyBirdDescription: strTicketStudentDescription;
      } 
      var p = getPercentDiscount();
      var description = (p > 0)? description + interpolate(strDiscount, p): description;
      handler.open({
        name: strOrgName,
        description: description,
        amount: amount,
        email: email,
        currency: "cad",
        opened: function() {
          $('.checkout-action .fa').addClass('hide');
          $('.checkout-action .fa-paper-plane').removeClass('hide');
          $('.checkout-action .text').text(strStripeInAction);
        },
        closed: function() {
          if ($('.checkout-action').hasClass('token-was-obtained')) {
            $('.checkout-action .fa').addClass('hide');
            $('.checkout-action .fa-spinner').removeClass('hide');
            $('.checkout-action').addClass('waiting');
            $('.checkout-action .text').text(strCompletingRegistration);
            setTimeout(function(){ 
              if ($('.checkout-action').hasClass('waiting')) {
                $('.checkout-action .text').text(strPlsWait);
                setTimeout(function(){ 
                  if ($('.checkout-action').hasClass('waiting')) {
                    $('.checkout-action .text').text(strSmallTalk);
                  }
                }, 20000);
              }
            }, 5000);
          } else {
            enabledFormControls(true);
            restoreCheckoutButton();
          }
        }
      });
    }

    function desktopCheckout(handler, formData, amount) {
        displayIsCheckingOut();
        openCheckhoutHandler(handler, amount, formData['email']);
    }

    function restoreCheckoutButton() {
      $('.checkout-wrapper .fa').addClass('hide');
      $('.checkout-wrapper .fa-lock').removeClass('hide');
      $('.checkout-action').removeClass('waiting token-was-obtained disabled btn-danger btn-success').addClass('btn-primary');
      $('#checkout .text').text(strCheckout);
      $('.message').addClass('hide');
    }
})(jQuery, Date, gettext, pgettext, interpolate); // End of use strict