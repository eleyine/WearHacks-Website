from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns

from wearhacks_website import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += i18n_patterns(
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^register/', include('registration.urls')),

)

# Javascript Internationalization Support
from django.views.i18n import javascript_catalog

js_info_dict = {
    'packages': (
            'registration',
            'static.javascripts',
        ),
}
from django.views.i18n import javascript_catalog


urlpatterns = i18n_patterns(
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
    url(r'^i18n/', include('django.conf.urls.i18n')),
) + urlpatterns

# Debug 
from django.conf import settings
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))