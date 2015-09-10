from django.views import generic
from django.http import HttpResponse
from django.template import Context, loader
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from tempfile import TemporaryFile

from django.conf import settings

from registration.models import Registration

# TODO: use this instead of settings.HOSTS[0]
# from django.contrib.sites.shortcuts import get_current_site


class ConfirmationEmailView(generic.DetailView):
    template_name = 'registration/confirmation_email.html'
    model = Registration
    context_object_name = 'r'

    @staticmethod
    def get_extra_context(registration):
        ticket_price = registration.ticket_price / float(100) if registration.ticket_price else 0
        tshirt_size_choices = dict(Registration.TSHIRT_SIZE_CHOICES)
        if registration.tshirt_size:
            tshirt_size = tshirt_size_choices[registration.tshirt_size]
        else:
            tshirt_size = _('Unknown')

        if registration.qrcode_file:
            qrcode_file = registration.qrcode_file.url
        else:
            qrcode_file = ''

        site_root = settings.HOSTS[0]
        http = settings.HTTP_PREFIX
        d = {
            'ticket_price_in_dollars': ticket_price,
            'tshirt_size': tshirt_size,
            'site_root': site_root,
            'r': registration,
            'http': http,
            'qrcode_file': qrcode_file
        }
        return d

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(generic.DetailView, self).get_context_data(**kwargs)
        d = ConfirmationEmailView.get_extra_context(context['object'])
        context.update(d)
        # Regenerate ticket
        TicketView.generate_pdf_ticket(registration=context['object'], context=context)
        return context

    def get_object(self, queryset=None):
        # obj = get_object_or_404(Registration, order_id=self.kwargs['order_id'])
        obj = Registration.objects.filter(order_id=self.kwargs['order_id']).first()
        return obj

class TicketView(ConfirmationEmailView):
    template_name = 'registration/ticket.html'

    def get_object(self, queryset=None):
        obj = super(TicketView, self).get_object(queryset=queryset) 
        return obj

    def render_to_response(self, context, **response_kwargs):
        from cgi import escape
        QRCodeView.generate_qr_code(registration=context["r"])
        pdf, result, html = TicketView.generate_pdf_ticket(context=context)
        if not pdf.err:
            return HttpResponse(result, content_type='application/pdf')
        return HttpResponse(_('We had some errors<pre>%s</pre>') % escape(html))

    @staticmethod
    def generate_pdf_ticket(registration=None, context=None, encoding='utf-8'):
        import ho.pisa as pisa
        import cStringIO as StringIO
        from django.utils.six import BytesIO

        if not registration and not context:
            raise Http404(_("Invalid arguments"))

        if not context:
            d = ConfirmationEmailView.get_extra_context(registration)
            context = Context(d)
        template = loader.get_template('registration/ticket.html')
        html  = template.render(context)

        if not registration:
            registration = context['r']

        result = StringIO.StringIO()
        pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
        result = result.getvalue()

        try:
            file = TemporaryFile()
            file.write(result)
            registration.ticket_file = File(file)
            registration.save()
            file.close()
        except Exception, e:
            charge = registration.charge
            if charge:
                charge.save_server_message(
                    ['Failed while saving ticket file'], exception=e)

        return (pdf, result, html)

class QRCodeView(ConfirmationEmailView):
    template_name = 'registration/qrcode.html'

    def get_object(self, queryset=None):
        obj = super(QRCodeView, self).get_object(queryset=queryset) 
        return obj

    def render_to_response(self, context, **response_kwargs):
        registration = context["r"]
        QRCodeView.generate_qr_code(registration=registration)
        if 'qrcode_file' in context.keys() and not context['qrcode_file'] \
            and registration.qrcode_file:
            context["qrcode_file"] = registration.qrcode_file.url
        return super(QRCodeView, self).render_to_response(context, **response_kwargs)

    @staticmethod
    def generate_qr_code(registration=None, context=None):
        import StringIO
        import qrcode

        if not registration and not context:
            raise Http404(_("Invalid arguments"))

        if not context:
            d = ConfirmationEmailView.get_extra_context(registration)
            context = Context(d)
        if not registration:
            registration = context['r']

        img = qrcode.make(data=registration.get_confirmation_url(), version=3)
        img_io = StringIO.StringIO()
        img.save(img_io)

        img_file = InMemoryUploadedFile(img_io, None, 'tmp.png','image/png',img_io.len, None)
        registration.qrcode_file = img_file
        registration.save()