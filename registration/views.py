from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views import generic
from django.shortcuts import render

from registration.models import Registration, ChargeAttempt
from registration.forms import RegistrationForm

from crispy_forms.utils import render_crispy_form
from jsonview.decorators import json_view

import stripe

class SubmitRegistrationView(generic.View):
    template_name = 'registration/form.html'
    form_class = RegistrationForm

    def get(self, request, *args, **kwargs):
        context = {
            'form': RegistrationForm()
        }
        return render(request, self.template_name, context)

    # hard-coded for now
    # TODO: GET amount by is_student and created_at (for early birds)
    def is_valid_amount(self, is_student, amount):
        is_valid = (is_student and amount == 100) or amount == 200
        return is_valid

    @json_view
    def post(self, request, *args, **kwargs):
        stripe.api_key = "sk_test_HJFprvoBQQcFpHMcJ4fcP4Nb"
        checkout_success = False
        checkout_message = 'Checkout not attempted yet.'
        message = "Oops! There were some errors in your registration."
        email = None

        # check registration information
        registration_success= False
        registration_message = ''
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            registration_success = True
            email = form.cleaned_data['email']
        else:
            registration_message= ('Please correct your registration information'
                ' before proceeding to checkout.')

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
                charge = stripe.Charge.create(
                  amount=amount,
                  currency="cad",
                  source=token_id, # obtained with Stripe.js
                  description="Charge for %s" % (email),
                  statement_descriptor="WearHacks Mtl 2015",
                  capture=False,
                )

                # Log charge attempt
                charge_attempt = ChargeAttempt.objects.create(
                        email = email,
                        charge_id = charge.id,
                        is_livemode = charge.livemode,
                        is_paid = charge.paid,
                        status = charge.status,
                        amount = charge.amount,
                        source_id = charge.source.id,
                        is_captured = charge.captured,
                        failure_message = charge.failure_message or '',
                        failure_code = charge.failure_code or ''
                    )
                charge_attempt.save()

                # Two checks because API upgraded and too lazy to check my version
                checkout_success = (charge.status == 'paid' or charge.status == 'succeeded')

                if not checkout_success:
                    checkout_message = "Something went wrong on Stripe's end.\n"
                    checkout_message += charge.failure_message
                    checkout_message += "Please try again."
                else:
                    checkout_message = 'Valid card information'

        if registration_success and checkout_success:
            charge = stripe.Charge.retrieve(charge.id) # not sure if necessary
            charge.capture()
            charge_attempt.is_captured = True
            charge_attempt.save()
            new_regisration = form.save()
            new_regisration.charge = charge_attempt
            new_regisration.save()
            message = 'Payment complete. We hope to see you there!'

        response = {
            'registration_success': registration_success,
            'checkout_success': checkout_success,
            'registration_message': registration_message,
            'checkout_message': checkout_message,
            'message': message,
            'success': registration_success and checkout_success,
        }
        print response
        response['form_html'] = form_html

        return response

    def get_context_data(self, **kwargs):
        context = super(SubmitRegistrationView, self).get_context_data(**kwargs)
        context['form'] = RegistrationForm()
        return context

