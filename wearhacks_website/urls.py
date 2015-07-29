from django.conf.urls import patterns, include, url

from wearhacks_website import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^register/', include('registration.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.IndexView.as_view(), name='index'),
)
