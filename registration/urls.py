from django.conf.urls import patterns, url
 
from registration import forms
from registration.views import register, email, confirm, stats

urlpatterns = patterns('',
    url(r'^$', register.RegistraionClosed.as_view(), name='register'),
    url(r'waitlist/^$', register.SubmitRegistrationView.as_view(), name='waitlist'),
    url(r'^confirmation/(?P<order_id>[\dx]+)/$', email.ConfirmationEmailView.as_view(), name='confirmation_email'),
    url(r'^ticket/(?P<order_id>[\dx]+)/$', email.TicketView.as_view(), name='ticket'),
    url(r'^qrcode/(?P<order_id>[\dx]+)/$', email.QRCodeView.as_view(), name='qrcode'),
    url(r'^confirm/(?P<order_id>[\dx]+)/$', confirm.ConfirmRegistrationView.as_view(), name='confirm-registration'),
    url(r'^stats/$', stats.EventStats.as_view(), name='stats'),
    url(r'^stats/registrations-by-date/$', stats.get_registration_timeseries, name='registration-timeseries'),
)