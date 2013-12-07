from django.conf.urls.defaults import *

urlpatterns = patterns('label.views.api',
    url(r'^get-updates/(?P<host_id>[\w\d_-]+)/$', 'get_updates'),
    url(r'^update-ack/(?P<host_id>[\w\d_-]+)/(?P<label_upc>[\w\d-]+)/$', 'update_ack'),
    url(r'^get-bitmap/(?P<host_id>[\w\d_-]+)/(?P<label_upc>[\w\d-]+)/$', 'get_bitmap', name='get_bitmap'),
    url(r'^get-label-status/$', 'get_label_status', name='get_label_status'),
    url(r'^resend-label/(?P<label_upc>[:\w\d-]+)/$', 'resend_label', name='resend_label'),

    url(r'^pricebook-upload/', 'pricebook_upload', {}, name='pricebook_upload'),
)
