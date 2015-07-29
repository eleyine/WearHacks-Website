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
from datetime import datetime

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
        full_price = 2000 # in cents

        early_bird_deadline = datetime.strptime('Sep 15 2015', '%b %d %Y')
        is_early_bird = datetime.now() < early_bird_deadline

        ratio_to_pay = 0.5 if is_early_bird else 1
        ratio_to_pay = ratio_to_pay * 0.5 if is_student else ratio_to_pay

        # keep it constant for now
        is_valid = amount == ratio_to_pay * full_price
        return is_valid

    @json_view
    def post(self, request, *args, **kwargs):
        checkout_success = False
        checkout_message = 'Checkout not attempted yet.'
        fraud_attempt = False
        error_message = ''
        email = None
        server_error = False
        server_message_client = ''
        server_message = ''
        is_captured = False

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
            checkout_message = ''
            checkout_success = False

            error_message = '</br>r u trying to hack us? u wot m8'
            fraud_attempt = True
            server_message += "Fraud attempt: amount entered was %.2f$" % (amount * 0.01)

        # attempt charge only if registration information is valid
        if registration_success and amount:
            token_id = request.POST.get('token_id', None)
            charge_attempt = None

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
                e = None

                try:
                    hacker_name = "%s %s" % (
                        form.cleaned_data["first_name"],
                        form.cleaned_data["last_name"])

                    charge_attempt = ChargeAttempt.objects.create(
                        hacker = hacker_name,
                        email = email,
                        charge_id = charge_id,
                        status = status,
                        amount = amount,
                        source_id = token_id
                    )
                    charge_attempt.save()

                    charge_attempt_link = 'http://%s/admin/registration/chargeattempt/%i/' % (
                            'montreal.wearhacks.com',
                            charge_attempt.pk
                        )
                    if not fraud_attempt:
                        stripe.api_key = self.get_stripe_secret_key()
                        charge = stripe.Charge.create(
                          amount=amount,
                          currency="cad",
                          source=token_id, # obtained with Stripe.js
                          description="Charge for %s" % (email),
                          statement_descriptor="WearHacks Mtl 2015",
                          capture=False,
                          metadata = {
                          'Name': hacker_name,
                          'charge_attempt_id': charge_attempt.pk,
                          'charge_attempt_link': charge_attempt_link }
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
                    if not fraud_attempt:
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

                print 'charge_attempt', charge_attempt
                # Log charge attempt
                if charge_attempt:
                    print charge_attempt
                    qs = ChargeAttempt.objects.filter(pk=charge_attempt.pk)
                    qs.update(
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
                    charge_attempt = qs[0]

                if not server_error and not checkout_success:
                    if not fraud_attempt:
                        checkout_message = "Something went wrong on Stripe's end. </br>"
                    if charge and hasattr(charge, 'failure_message') and failure_message is not None:
                        checkout_message += failure_message
                    if error_message:
                        checkout_message += '<strong>%s </strong> </br>' % (error_message)
                    checkout_message += "Please refresh and try again."

                if not checkout_success and not is_captured:
                    checkout_message += "</br><strong>Don't worry, you haven't been charged.</strong>"

        if registration_success and checkout_success and not server_error:
            try:
                new_regisration = form.save()
                new_regisration.charge = charge_attempt
                new_regisration.save()
            except Exception, e:
                server_error = True
                checkout_success = False
                server_message_client = self._get_server_error_message('Your registration could not be saved.')
                server_message += 'Failed while saving registration form. (%s)' % (str(e)[:100])

            if not server_error:
                try:
                    charge = stripe.Charge.retrieve(charge.id)
                    charge.capture()
                    is_captured = True
                except Exception, e:
                    server_error = True
                    server_message_client = self._get_server_error_message('We could not charge you.', 
                        dont_worry=False)

                    server_message += 'Failed while capturing charge. (%s) ' % (str(e)[:100])

                if is_captured:
                    charge_attempt.is_captured = True

            if server_error:
                charge_attempt.server_message = server_message
                charge_attempt.save()

        response = {
            'server_message': server_message_client,
            'server_error': server_error,
            'registration_success': registration_success,
            'checkout_success': checkout_success,
            'registration_message': registration_message,
            'checkout_message': checkout_message,
            'success': registration_success and checkout_success,
            'stripe_public_key': self.get_stripe_public_key()
        }
        if server_message:
            print server_message
        response['form_html'] = form_html

        return response

    def _get_server_error_message(self, inner_message, dont_worry=True):
        message = "Oops, something went wrong on our end.</br>Please refresh and try again. "
        message += "If the problem persists, please contact our support team. </br>"
        message += "<strong>%s</strong>"
        if dont_worry:
            message += "</br><strong>Don't worry, you haven't been charged.</strong>"
        message = message % (inner_message)
        return message

    def get_context_data(self, **kwargs):
        context = super(SubmitRegistrationView, self).get_context_data(**kwargs)
        context['form'] = RegistrationForm()
        return context
