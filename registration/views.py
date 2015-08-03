from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage

from django.contrib import messages
from django.views import generic
from django.shortcuts import render, get_object_or_404

from django.utils import translation

from registration.models import Registration, ChargeAttempt
from registration.forms import RegistrationForm

from crispy_forms.utils import render_crispy_form
from jsonview.decorators import json_view

from django.conf import settings

import stripe
from datetime import datetime

from django.contrib.sites.shortcuts import get_current_site

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

    @json_view
    def post(self, request, *args, **kwargs):

        language = request.POST.get('lang', settings.LANGUAGE_CODE)
        translation.activate(language)
        request.LANGUAGE_CODE = language
        
        charge_attempt = None
        checkout_success = False
        success_message = ''
        checkout_message = 'Checkout not attempted yet.'
        fraud_attempt = False
        error_message = ''
        email = None
        server_error = False
        server_message_client = ''
        server_messages = []
        is_captured = False

        if settings.DEBUG:
            # auto fill some fields
            defaults = (
                    ('first_name', 'First'),
                    ('last_name', 'Last'),
                    ('email', settings.EMAIL_HOST_USER),
                    ('gender', 'N'),
                    ('tshirt_size', 'M'),
                )
            for k, v in defaults:
                if not request.POST[k]:
                    request.POST[k] = v
            request.POST['has_read_code_of_conduct'] = True

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

        # check amount is valid
        amount = int(request.POST.get('amount', 0))
        is_valid_amount = False
        if amount:
            is_student = request.POST.get('is_student', False)
            _, _, ticket_price = self.get_ticket_info(is_student)
            is_valid_amount = amount == ticket_price
        if amount and not is_valid_amount:
            checkout_message = ''
            checkout_success = False

            error_message = '</br>r u trying to hack us? u wot m8'
            fraud_attempt = True
            server_messages.append("Fraud attempt: amount entered was %.2f$" % (amount * 0.01))

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
                        server_messages.append('Charge object does not exist. ')

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
                        server_message = ' / '.join(server_messages),
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

        new_registration = None
        if registration_success and checkout_success and not server_error:
            try:
                # Save registration
                new_registration = form.save()

                # Add additional fields to form
                new_registration.preferred_language = language

                is_student = request.POST.get('is_student', False)
                is_early_bird, ticket_description, ticket_price = self.get_ticket_info(
                    is_student)

                new_registration.is_early_bird = is_early_bird
                new_registration.ticket_description = ticket_description
                new_registration.ticket_price = ticket_price

                new_registration.order_id = Registration.generate_order_id()
                
                new_registration.charge = charge_attempt
                new_registration.save()
            except Exception, e:
                server_error = True
                checkout_success = False
                server_message_client = self._get_server_error_message('Your registration could not be saved.')
                server_messages.append('Failed while saving registration form.')
                self._save_server_message_to_charge_attempt(charge_attempt, server_messages, e)

            # Charge user
            if not server_error:
                try:
                    charge = stripe.Charge.retrieve(charge.id)
                    charge.capture()
                    is_captured = True
                except Exception, e:
                    server_error = True
                    server_message_client = self._get_server_error_message(
                        'We could not charge you.', 
                        dont_worry=False)
                    server_messages.append('Failed while capturing charge.')
                    charge_attempt.is_captured = is_captured
                    self._save_server_message_to_charge_attempt(charge_attempt, server_messages, e)

            # Send confirmation email
            if not server_error:
                try:
                    self.send_confirmation_email(new_registration)

                except Exception, e:
                    server_error = True
                    checkout_success = False
                    server_message_client = self._get_server_error_message(
                        'Your confirmation email cannot be sent at the moment. '
                        '</strong><small>Everything else went smoothly and your payment went through. '
                        'Admins have been notified and will send you a confirmation email shortly.</small><strong>',
                        dont_worry=False,
                        default_header=False
                        )
                    server_messages.append('Failed while sending confirmation email (order #%s).' % (new_registration.order_id))
                    self._save_server_message_to_charge_attempt(charge_attempt, server_messages, e)

            if not server_error:
                success_message = 'A confirmation email will be sent shortly.'
                try:
                    new_registration.is_email_sent = True
                    new_registration.save()
                except Exception, e:
                    server_messages.append('Failed while setting is_email_sent to True in registration.')
                    self._save_server_message_to_charge_attempt(charge_attempt, server_messages, e)

        elif charge_attempt and len(server_messages) > 0:
            self._save_server_message_to_charge_attempt(charge_attempt, server_messages, None)

        response = {
            'server_message': server_message_client,
            'server_error': server_error,
            'registration_success': registration_success,
            'checkout_success': checkout_success,
            'registration_message': registration_message,
            'checkout_message': checkout_message,
            'success': registration_success and checkout_success,
            'success_message': success_message,
            'stripe_public_key': self.get_stripe_public_key()
        }
        if server_messages:
            print ' / '.join(server_messages)
        response['form_html'] = form_html

        return response

    def _get_server_error_message(self, inner_message, dont_worry=True, default_header=True):
        message = ''
        if default_header:
            message += "Oops, something went wrong on our end.</br>Please refresh and try again. "
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

    def _save_server_message_to_charge_attempt(self, charge_attempt, messages, e):
        try:
            if e:
                server_message = '%s (%s)' % (' / '.join(messages), str(e)[:100])
                print str(e)
            else:
                server_message = ' / '.join(messages)
            charge_attempt.server_message = server_message[:ChargeAttempt.SERVER_MESSAGE_MAX_LENGTH-1]
            charge_attempt.save()
        except Exception, e:
            print 'ERROR: Could not save server message %s to charge attempt %s (%a)' % (
                    server_message,
                    charge_attempt,
                    str(e)
                )

    def get_ticket_info(self, is_student):
        early_bird_deadline = datetime.strptime('Sep 15 2015', '%b %d %Y')
        is_early_bird = datetime.now() < early_bird_deadline

        ticket_description, ticket_price = Registration.get_ticket_info(
                is_student=is_student,
                is_early_bird=is_early_bird
            )
        return (is_early_bird, ticket_description, ticket_price)


    def send_confirmation_email(self, registration):
        from django.core.mail import send_mail, EmailMultiAlternatives
        from django.template import Context
        from django.template.loader import render_to_string

        # create context 
        d = ConfirmationEmailView.get_extra_context(registration)
        c = Context(d)

        # create html/txt
        msg_plaintext = render_to_string('registration/confirmation_email.txt', c)
        msg_html      = render_to_string('registration/confirmation_email.html', c)

        # email settings
        subject = 'Thanks for signing up!'
        from_email = "WearHacks Montreal <%s>" % settings.DEFAULT_FROM_EMAIL
        to = [registration.email]
        headers = {'Reply-To': "WearHacks Montreal Team <montreal@wearhacks.com>"}

        # mandrill settings
        tags = ['registration confirmation']
        if registration.is_early_bird:
            tags.append('early bird')
        else:
            tags.append('student')
        metadata = {'order_id': registration.order_id}

        # with open('tmp/' + registration.order_id + '.txt', 'w') as f:
        #     f.write(msg_plaintext)
        # with open('tmp/' + registration.order_id + '.html', 'w') as f:
        #     f.write(msg_html)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=msg_plaintext,
            from_email=from_email,
            to=to,
            headers=headers # optional extra headers
        )
        msg.attach_alternative(msg_html, "text/html")
        msg.tags = tags
        msg.metadata = metadata
        msg.send()

        # send_mail(
        #     subject,
        #     msg_plaintext,
        #     from_email,
        #     to,
        #     html_message=msg_html,
        # )

    def generate_pdf_ticket(self):
        import cStringIO as StringIO
        import ho.pisa as pisa
        from django.template.loader import get_template
        from django.template import Context
        from django.http import HttpResponse
        from cgi import escape


        def render_to_pdf(template_src, context_dict):
            template = get_template(template_src)
            context = Context(context_dict)
            html  = template.render(context)
            result = StringIO.StringIO()

            pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
            return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

class ConfirmationEmailView(generic.DetailView):
    template_name = 'registration/confirmation_email.html'
    model = Registration
    context_object_name = 'r'

    @staticmethod
    def get_extra_context(registration):
        ticket_price = registration.ticket_price / float(100) if registration.ticket_price else 0
        tshirt_size_choices = dict(Registration.TSHIRT_SIZE_CHOICES)
        tshirt_size = tshirt_size_choices[registration.tshirt_size]
        site_root = settings.HOSTS[0]
        http = settings.HTTP_PREFIX
        d = {
            'ticket_price_in_dollars': ticket_price,
            'tshirt_size': tshirt_size,
            'site_root': site_root,
            'r': registration,
            'http': http
        }
        return d

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(generic.DetailView, self).get_context_data(**kwargs)
        d = ConfirmationEmailView.get_extra_context(context['object'])
        context.update(d)
        return context

    def get_object(self, queryset=None):
        # obj = get_object_or_404(Registration, order_id=self.kwargs['order_id'])
        obj = Registration.objects.filter(order_id=self.kwargs['order_id']).first()
        return obj

# # Internationalization support
# from django.views.decorators.http import last_modified
# from django.views.i18n import javascript_catalog

# last_modified_date = timezone.now()

# @last_modified(lambda req, **kw: last_modified_date)
# def cached_javascript_catalog(request, domain='djangojs', packages=None):
#     return javascript_catalog(request, domain, packages)