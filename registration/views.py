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


    @json_view
    def post(self, request, *args, **kwargs):
        stripe.api_key = "sk_test_HJFprvoBQQcFpHMcJ4fcP4Nb"
        checkout_success = False
        checkout_message = 'Checkout not attempted yet.'
        message = "Oops! There were some errors in your registration."
        email = None

        # check registration information
        registration_success= False
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            registration_success = True
            email = form.cleaned_data['email']

        form_html = render_crispy_form(form)

        # attempt charge
        token_id = request.POST.get('token_id', None)
        if email is None and token_id:
            checkout_message = ('You need a valid email for checkout.',
                'Please enter your card information again.')

        elif email and token_id:

            charge = stripe.Charge.create(
              amount=200,
              currency="cad",
              source=token_id, # obtained with Stripe.js
              description="Charge for %s" % (email),
              statement_descriptor="WearHacks Mtl 2015",
              capture=False,
            )
            print 'CHARGE STATUS:', charge.status

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
                    failure_code = charge.failure_code or 0
                )
            charge_attempt.save()
            print 'ChargeAttempt: %s' % (charge_attempt)

            # two checks because API upgraded
            checkout_success = (charge.status == 'paid' or charge.status == 'succeeded')
            print checkout_success
            if not checkout_success:
                checkout_message = charge.failure_message
                print 'status:', charge.status
                print 'charge code:', charge.failure_code
                print 'charge message:', charge.failure_message
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
            # 'registration_message': registration_message,
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

