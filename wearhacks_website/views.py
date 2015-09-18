from django.views import generic
from event.models import Person, Sponsor

from collections import defaultdict

class IndexView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all persons
        context['judges'] = Person.objects.filter(category='J').all()
        context['mentors'] = Person.objects.filter(category='M').all()
        
        # Add sponsors
        context['sponsors'] = defaultdict(list)
        for sponsor in Sponsor.objects.all():
            category = sponsor.get_category_display().lower().replace(' ', '_')
            context['sponsors'][category].append(sponsor)
        return context