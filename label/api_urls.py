from django.conf.urls.defaults import *

urlpatterns = patterns('label.views.api',
    url(r'^get-updates/$', 'get_updates'),
    url(r'^update-ack/(?P<label_upc>[\w\d-]+)/$', 'update_ack'),
    url(r'^get-bitmap/(?P<label_upc>[\w\d-]+)/$', 'get_bitmap', name='get_bitmap'),
    url(r'^get-label-status/$', 'get_label_status', name='get_label_status'),
)
