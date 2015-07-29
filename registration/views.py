from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views import generic
from django.shortcuts import render

from registration.models import Registration, ChargeAttempt
from registration.forms import RegistrationForm

from crispy_forms.utils import render_crispy_form
from jsonview.decorators import json_view

from django.conf import settings

import stripe

class SubmitRegistrationView(generic.View):
    template_name = 'registration/form.html'
    form_class = RegistrationForm

    def get_stripe_secret_key(self):
        if settings.IS_STRIPE_LIVE:
            stripe_sk = settings.LIVE_STRIPE_SECRET_KEY
        else:
            stripe_sk = settings.TEST_STRIPE_SECRET_KEY
        return stripe_sk

    def get_stripe_public_key(self):
        if settings.IS_STRIPE_LIVE:
            stripe_pk = settings.LIVE_STRIPE_PUBLIC_KEY
        else:
            stripe_pk = settings.TEST_STRIPE_PUBLIC_KEY
        return stripe_pk

    def get(self, request, *args, **kwargs):
        context = {
            'form': RegistrationForm(),
            'stripe_public_key': self.get_stripe_public_key()
        }
        return render(request, self.template_name, context)

    # hard-coded for now
    # TODO: GET amount by is_student and created_at (for early birds)
    def is_valid_amount(self, is_student, amount):
        # keep it constant for now
        is_valid = (is_student and amount == 200) or amount == 200
        return is_valid

    @json_view
    def post(self, request, *args, **kwargs):
        checkout_success = False
        checkout_message = 'Checkout not attempted yet.'
        email = None
        server_error = False
        server_message = ''

        # check registration information
        registration_success= False
        registration_message = ''
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            registration_success = True
            email = form.cleaned_data['email']
        else:
            registration_message= ('Please correct your registration information'
                ' before proceeding.')

        form_html = render_crispy_form(form)

        amount = int(request.POST.get('amount', 0))
        if amount and not self.is_valid_amount(form.cleaned_data['is_student'], amount):
            registration_success = False
            registration_message = 'r u trying to hack us? u wot m8'

        # attempt charge only if registration information is valid
        if registration_success and amount:
            token_id = request.POST.get('token_id', None)

            if not token_id:
                # no token id is sent during form prevalidation
                # this is normal
                registration_message = 'Registration Information Valid'
                checkout_message = ''
            else:
                # Default charge attempt fields
                charge = None
                charge_id = 'xxx'
                is_livemode = False
                is_paid = False
                status = 'Unknown'
                source_id = 'xxx'
                is_captured = False
                failure_message = 'Unknown'
                failure_code = 'Unknown'
                error_http_status = '200'
                error_type = 'None'
                error_code = 'None'
                error_param = 'None'
                error_message = ''
                e = None

                try:
                    stripe.api_key = self.get_stripe_secret_key()
                    charge = stripe.Charge.create(
                      amount=amount,
                      currency="cad",
                      source=token_id, # obtained with Stripe.js
                      description="Charge for %s" % (email),
                      statement_descriptor="WearHacks Mtl 2015",
                      capture=False,
                    )
                    failure_message = charge.failure_message
                    failure_code = charge.failure_code
                    checkout_success = True

                except stripe.error.CardError, e:
                    # Since it's a decline, stripe.error.CardError will be caught
                    body = e.json_body
                    err  = body['error']
                    error_http_status = e.http_status
                    checkout_message = err["message"]
                    checkout_success = False

                except (stripe.error.InvalidRequestError,
                    stripe.error.AuthenticationError,
                    stripe.error.StripeError), e:
                    # invalid_request: Invalid parameters were supplied to Stripe's API OR
                    # authetication_error: Authentication with Stripe's API failed
                    # (maybe you changed API keys recently) OR
                    checkout_message = ''
                    server_error = True
                    checkout_success = False

                except stripe.error.APIConnectionError, e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    checkout_message = 'Network communication with Stripe failed. Please reload the page.'
                    checkout_success = False

                except stripe.error.StripeError, e:
                    checkout_message = "Something went wrong on Stripe's end."
                    checkout_success = False

                except Exception, e:
                    checkout_message = ''
                    server_error = True
                    checkout_success = False

                if charge:
                    charge_id = charge.id
                    is_livemode = charge.livemode,
                    is_paid = charge.paid
                    status = charge.status
                    amount = charge.amount
                    source_id = charge.source.id
                    is_captured = charge.captured
                    failure_message = charge.failure_message
                    failure_code = charge.failure_code
                else:
                    checkout_success = False
                    server_message += 'Charge object does not exist. '

                if e and hasattr(e, 'json_body') and 'error' in e.json_body:
                    err = e.json_body['error']
                    error_type = err["type"]
                    if 'code' in err:
                        error_code = err["code"]
                    if 'param' in err:
                        error_param = err["param"]
                    if 'message' in err:
                        error_message = err["message"]

                if e and hasattr(e, 'http_status'):
                    error_http_status = e.http_status

                # Log charge attempt
                charge_attempt = ChargeAttempt.objects.create(
                        email = email,
                        charge_id = charge_id,
                        is_livemode = is_livemode,
                        is_paid = is_paid,
                        status = status,
                        amount = amount,
                        source_id = source_id,
                        is_captured = is_captured,
                        failure_message = failure_message or '',
                        failure_code = failure_code or '',
                        server_message = server_message,
                        error_type = error_type or '',
                        error_code = error_code or '',
                        error_param = error_param or '',
                        error_message = error_message or '',
                    )
                charge_attempt.save()

                if not server_error and not checkout_success:
                    checkout_message = "Something went wrong on Stripe's end.\n"
                    if charge and hasattr(charge, 'failure_message') and failure_message is not None:
                        checkout_message += failure_message
                    if error_message:
                        checkout_message += '<strong>%s </strong> ' % (error_message)
                    checkout_message += "Please refresh and try again."
                    checkout_message += "</br><strong>Don't worry, we did not capture your payment.</strong>"

        if registration_success and checkout_success and not server_error:
            try:
                charge = stripe.Charge.retrieve(charge.id)
                charge.capture()
                is_captured = True
            except Error, e:
                server_error = True
                server_message += 'Failed while capturing charge_attempt. (%s) ' % (str(e)[:100])

            if is_captured:
                charge_attempt.is_captured = True
                charge_attempt.save()
            
            try:
                new_regisration = form.save()
                new_regisration.charge = charge_attempt
                new_regisration.save()
            except Error, e:
                server_error = True
                server_message += 'Failed while saving registration form. (%s)' % (str(e)[:100])

        response = {
            'server_error': server_error,
            'registration_success': registration_success,
            'checkout_success': checkout_success,
            'registration_message': registration_message,
            'checkout_message': checkout_message,
            'success': registration_success and checkout_success,
            'stripe_public_key': self.get_stripe_public_key()
        }
        print response
        if server_message:
            print server_message
        response['form_html'] = form_html

        return response

    def get_context_data(self, **kwargs):
        context = super(SubmitRegistrationView, self).get_context_data(**kwargs)
        context['form'] = RegistrationForm()
        return context
