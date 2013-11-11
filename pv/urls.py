from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pv.views.home', name='home'),
    # url(r'^pv/', include('pv.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^', include('common.urls')),
    (r'^company/(?P<client_id>[\w\d-]+)/', include('label.urls')),

    (r'^accounts/', include('accounts.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^administration/', include('administration.urls')),

    url(r'^api/(?P<client_id>[\w\d-]+)/', include('label.api_urls')),

)
