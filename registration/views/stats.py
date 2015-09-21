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

from jsonview.decorators import json_view
from collections import defaultdict

class EventStats(generic.TemplateView):
    template_name = 'registration/stats.html'

    def get_context_data(self, **kwargs):
        context = super(EventStats, self).get_context_data(**kwargs)

        context['number_of_registrations'] = Registration.objects.count()

        context['first_time_hackers'] = Registration.objects.filter(is_first_time_hacker=True).count()
        context['returning_wearhackers'] = Registration.objects.filter(is_returning=True).count()

        context['female'] = Registration.objects.filter(gender='F').count()
        context['male'] = Registration.objects.filter(gender='M').count()
        context['other'] = Registration.objects.filter(gender='N').count()

        school_dict = defaultdict(dict)
        for r in Registration.objects.all():
            if r.school:
                school_dict[r.school] += 1
        schools = [{'name': n, 'count': c} for n, c in sorted(school_dict.iteritems())]

        context['schools'] = schools


        context['revenue'] = sum([c.amount for c in ChargeAttempt.objects.all()]) / 100.0

        context['net_revenue'] = sum([c.amount * 0.97 - 30 for c in ChargeAttempt.objects.all()]) / 100.0

        context['revenue'] = sum([c.amount for c in ChargeAttempt.objects.all()]) / 100.0
        context['paid_tickets_num'] = sum([1 for r in Registration.objects.all() if r.charge is not None])
        if context['paid_tickets_num'] > 0:
            context['avg_ticket_price'] = context['revenue'] / float(context['paid_tickets_num'])
        else:
            context['avg_ticket_price'] = 0

        context['food_restrictions'] = [r.food_restrictions for r in \
            Registration.objects.all() if r.food_restrictions != 'None']


        context['tshirt_sizes'] = []
        for gender in ['F', 'M', 'N']:
            gender_tshirt_sizes = {
                'gender': dict(Registration.GENDER_CHOICES)[gender],
                'categories': []
            }
            for tshirt_size in Registration.TSHIRT_SIZE_CHOICES:
                gender_tshirt_sizes['categories'].append({
                    'category': tshirt_size[1],
                    'number': Registration.objects.filter(tshirt_size=tshirt_size[0], gender=gender).count()
                })
            context['tshirt_sizes'].append(gender_tshirt_sizes)
        return context

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EventStats, self).dispatch(request, *args, **kwargs)

@json_view
def get_registration_timeseries(request, *args, **kwargs):
    import datetime, time
    date_objects = [r.created_at.date() for r in Registration.objects.all()]
    date_objects.append(datetime.datetime.now().date())
    date_objects.append(datetime.datetime.now().date() + datetime.timedelta(-3, 0))
    dates = sorted(list(set(date_objects)))
    data = []
    for date in dates:
        data.append((
            # datetiem in milliseconds
            int(time.mktime(date.timetuple())) * 1000, 
            Registration.objects.filter(created_at__contains=date).count(),
            ))
    cumdata = []
    cumcount = 0
    for date, count in data:
        cumcount += count
        cumdata.append((date, cumcount))
    response = {
        'cumdata': cumdata,
        'data': data
    }
    return response
