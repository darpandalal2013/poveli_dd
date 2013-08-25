from django.conf.urls.defaults import *


urlpatterns = patterns('administration.views',
    url(r'^$',  'home', name='administration_home'),
    url(r'^create-client/$',  'create_client', name='administration_create_client'),
    url(r'^clients-status/$',  'clients_status', name='administration_clients_status'),
    url(r'^clients-status-toggle/$',  'client_status_toggle',
        name='administration_client_status_toggle'),
)
