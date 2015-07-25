from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views import generic
from django.shortcuts import render

from registration.models import Registration
from registration.forms import RegistrationForm

from crispy_forms.utils import render_crispy_form
from jsonview.decorators import json_view

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
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your registration has been saved.')
            form_html = render_crispy_form(form)
            return {'success': True, 'form_html': form_html }
        form_html = render_crispy_form(form)

        return {'success': False, 'form_html': form_html}

    def get_context_data(self, **kwargs):
        context = super(SubmitRegistrationView, self).get_context_data(**kwargs)
        context['form'] = RegistrationForm()
        return context