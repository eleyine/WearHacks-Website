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
        print 'Eureka!!'
        # do_update = 'registration_id' in self.kwargs

        # if do_update:
        #     messages.error(request, 'You are already registered!')

        #     # registration_instance = get_object_or_404(Registration, 
        #     #     id=self.kwargs['registration_id'])
        #     # form = self.form_class(request.POST, instance=registration_instance)

        #     # I should really make a validation/thanks page
        #     return HttpResponseRedirect(reverse('index'))
        # else:
        #     form = self.form_class(request.POST)
        form = self.form_class(request.POST, request.FILES)
        print request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Your registration has been saved.')
            form_html = render_crispy_form(form)
            return {'success': True, 'form_html': form_html }
        print 'Error'
        form_html = render_crispy_form(form)
        print form_html

        return {'success': False, 'form_html': form_html}

    def get_context_data(self, **kwargs):
        context = super(SubmitRegistrationView, self).get_context_data(**kwargs)
        context['form'] = RegistrationForm()
        return context