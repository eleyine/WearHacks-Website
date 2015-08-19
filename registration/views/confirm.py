from django.views import generic

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from registration.models import Registration
from registration.forms import ConfirmRegistrationForm

from crispy_forms.utils import render_crispy_form
from jsonview.decorators import json_view

from django.template.loader import render_to_string

from django.utils.translation import ugettext as _
from django.utils.translation import pgettext as __

class ConfirmRegistrationView(generic.DetailView):
    template_name = 'registration/confirm-form.html'
    model = Registration
    form_class = ConfirmRegistrationForm

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ConfirmRegistrationView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # obj = get_object_or_404(Registration, order_id=self.kwargs['order_id'])
        obj = Registration.objects.filter(order_id=self.kwargs['order_id']).first()
        return obj

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(generic.DetailView, self).get_context_data(**kwargs)
        context['form'] = ConfirmRegistrationForm(instance=context['registration'])
        d = ConfirmRegistrationView.get_extra_context(context["registration"])
        context.update(d)
        return context

    @staticmethod
    def get_extra_context(registration):
        if registration:
            d = {
                 # 'has_submitted_waiver': registration.has_submitted_waiver,
                 'order_id': registration.order_id,
                 'has_attended': registration.has_attended
            }
        else:
            d = {}
        return d

    def _save_server_message_to_charge_attempt(self, registration, messages, e):
        print e
        if registration and registration.charge:
            registration.charge.save_server_message(messages, exception=e)

    # @staff_member_required
    @json_view
    def post(self, request, *args, **kwargs):
        checkin_success = False
        checkin_message = ''
        server_error = False
        server_message_client = ''

        instance = None
        try:
            order_id = request.POST.get("order_id", None)
            instance = Registration.objects.filter(order_id=order_id).first()
        except Exception, e:
            server_error = True
            server_message_client = "Invalid POST request"
            if order_id:
                message = "Missing params in post request"
            else:
                message = "Invalid order_id %s" % (order_id)
            self._save_server_message_to_charge_attempt(instance, [message], e)
        
        form = self.form_class(request.POST, request.FILES, instance=instance)

        if not server_error:
            if form.is_valid():
                checkin_success = True
            else:
                checkin_message = _("Could not validate form")

        registration = None
        if checkin_success:
            try:
                registration = form.save()
                registration.save()
            except Exception, e:
                server_error = True
                server_message_client = _("We had trouble saving your new information")
                self._save_server_message_to_charge_attempt(registration, 
                    [server_message_client], e)

        form_html = render_crispy_form(form)

        response = {
            'server_message': server_message_client,
            'server_error': server_error,
            'checkin_success': checkin_success,
            'checkin_message': checkin_message,
            'success': checkin_success and not server_error,
            "success_message": _("Confirmed attendee details")
        }

        d = ConfirmRegistrationView.get_extra_context(registration)
        response.update(d)

        response['form_html'] = form_html
        return response