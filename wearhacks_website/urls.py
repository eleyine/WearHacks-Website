from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns

from wearhacks_website import views

from django.contrib import admin
from registration.views import register

# from djrill import DjrillAdminSite

# admin.site = DjrillAdminSite()
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns(
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^waitlist/$', register.SubmitRegistrationView.as_view(), name='register'),
    url(r'^register/', include('registration.urls')),
)
# Javascript Internationalization Support
from django.views.i18n import javascript_catalog

js_info_dict = {
    'packages': (
            'registration',
            # 'static.javascripts',
        ),
}

print javascript_catalog

urlpatterns = i18n_patterns(
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='django.views.i18n.javascript_catalog'),
) + urlpatterns

# Debug 
from django.conf import settings
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}),
    )
    urlpatterns += patterns(
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT}),
        )