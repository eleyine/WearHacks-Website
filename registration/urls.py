from django.conf.urls import patterns, url
 
from registration import views, forms
 
urlpatterns = patterns('',
    url(r'^$', views.SubmitRegistrationView.as_view(), name='register'),
    url(r'^confirmation/(?P<order_id>[\dx]+)/$', views.ConfirmationEmailView.as_view(), name='confirmation_email'),
)