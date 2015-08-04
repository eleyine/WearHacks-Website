(function($, Date, _, pgettext, interpolate) {
    "use strict"; // Start of use strict

    $( document ).ready(function() {

        // ajaxSetup();
        stylisticTweaks();

        $(document).on('click', '.confirm-action', function (e) {
            checkin();
            e.preventDefault();
        } );
    });

    var strSorry = _('Sorry');
    var strThankYou = _('Thank you');
    var strConfirm = _('Confirm');
    var strServerError = pgettext( 
            "AJAX error",
           'There is a temporary problem with our server. Please refresh.');
    var strConfirmInProgress = _('Confirming details');

    function stylisticTweaks() {
        $(".conduct ~ a")
          .attr("href", window.code_of_conduct)
          .attr("target", "_blank");
        $(".checkboxinput").bootstrapSwitch();  
        if (window.has_submitted_waiver == "True") {
          $("fieldset.attendee-info").prepend('<div class="waiver message-success"><i class="fa fa-check"></i> Attendee submitted waiver.</div>');
        } else {
          $("fieldset.attendee-info").prepend('<div class="waiver message-error"><i class="fa fa-remove"></i> Attendee didn\'t submit a waiver.</div>');
        }
    }

    function checkin() {
        console.log("click!");
        var form = 'form';
        var formData = new FormData($(form)[0]);
        var lang = document.documentElement.lang;
        var order_id = window.order_id;
        formData.append("lang", lang);
        formData.append("order_id", order_id);
        $.ajax({
            processData: false,
            contentType: false,
            url: "/" + lang + "/register/confirm/" + window.order_id + "/",
            type: "POST",
            data: formData,
            success: function(data) {
                $(form).replaceWith(data['form_html']);
                stylisticTweaks();
                if(!data["server_error"]) {
                  if (!data['checkin_success']) {
                      displaySorryButton(data["checkin_message"]);
                  } else {
                      displayThankYouButton(data["success_message"]);
                  }
                } else {
                  displayServerError(data["server_message"]);
                }
                enabledFormControls(false);
            },
            error: function (data) {
                console.log(data);
                enabledFormControls(false);
                displayServerError();
            }
        });
    }

    function displaySorryButton() {
      $('.fa').addClass('hide');
      $('#confirm .text').text('Sorry');
      $('.confirm-action').removeClass('waiting btn-primary');
      $('.confirm-action').addClass('disabled btn-danger');
    }

    function displayThankYouButton(message) {
      $('.confirm-wrapper .fa').addClass('hide');
      $('.confirm-wrapper .fa-check').removeClass('hide');
      $('.confirm-action').removeClass('waiting');
      $('#confirm .text').text(strThankYou);
      $('.confirm-action').removeClass('btn-primary').addClass('disabled btn-success');
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

    function enabledFormControls(isEnabled) {
      $('input').attr('readOnly', !isEnabled);
      $('textarea').attr('readOnly', !isEnabled);
      $('input').attr('disabled', !isEnabled);
      $('select').attr('disabled', !isEnabled);
      $('textarea').attr('disabled', !isEnabled);
      $(".checkboxinput").bootstrapSwitch('disabled', !isEnabled);
      $(".checkboxinput").bootstrapSwitch('readonly', !isEnabled);
    }

    function displayIsCheckingOut() {
      $('.message').addClass('hide');
      $('.confirm-action .fa').addClass('hide');
      $('.confirm-action .fa-spinner').removeClass('hide');
      $('#confirm .text').text(strConfirmInProgress);
    }

    function restoreConfirmButton() {
      $('.confirm-wrapper .fa').addClass('hide');
      $('.confirm-wrapper .fa-lock').removeClass('hide');
      $('.confirm-action').removeClass('waiting token-was-obtained disabled btn-danger btn-success').addClass('btn-primary');
      $('#confirm .text').text(strConfirm);
      $('.message').addClass('hide');
    }
})(jQuery, Date, gettext, pgettext, interpolate); // End of use strict