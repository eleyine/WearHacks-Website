from django.views import generic
from event.models import Person

class IndexView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['judges'] = Person.objects.filter(category='J').all()
        context['mentors'] = Person.objects.filter(category='M').all()
        return context