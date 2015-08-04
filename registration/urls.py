from django.conf.urls import patterns, url
 
from registration import views, forms
 
urlpatterns = patterns('',
    url(r'^$', views.SubmitRegistrationView.as_view(), name='register'),
    url(r'^confirmation/(?P<order_id>[\dx]+)/$', views.ConfirmationEmailView.as_view(), name='confirmation_email'),
    url(r'^ticket/(?P<order_id>[\dx]+)/$', views.TicketView.as_view(), name='ticket'),
    url(r'^qrcode/(?P<order_id>[\dx]+)/$', views.QRCodeView.as_view(), name='qrcode'),
    url(r'^confirm/(?P<order_id>[\dx]+)/$', views.ConfirmRegistrationView.as_view(), name='confirm-registration'),
)