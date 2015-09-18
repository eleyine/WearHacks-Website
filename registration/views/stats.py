from django.views import generic

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from crispy_forms.utils import render_crispy_form
from jsonview.decorators import json_view

from django.template.loader import render_to_string

from django.utils.translation import ugettext as _
from django.utils.translation import pgettext as __

from collections import defaultdict
from registration.models import ChargeAttempt, Registration

class EventStats(generic.TemplateView):
    template_name = 'registration/stats.html'

    def get_context_data(self, **kwargs):
        context = super(EventStats, self).get_context_data(**kwargs)

        context['revenue'] = sum([c.amount for c in ChargeAttempt.objects.all()])
        context['paid_tickets_num'] = sum([1 for r in Registration.objects.all() if r.charge is not None])

        context['food_restrictions'] = [r.food_restrictions for r in \
            Registration.objects.all() if r.food_restrictions != 'None']

        context['tshirt_sizes'] = []
        for tshirt_size in Registration.TSHIRT_SIZE_CHOICES:
            context['tshirt_sizes'].append({
                'category': tshirt_size[1],
                'number': Registration.objects.filter(tshirt_size=tshirt_size[0]).count()
            })
        return context

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EventStats, self).dispatch(request, *args, **kwargs)
