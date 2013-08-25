from django.conf.urls.defaults import *


api_urlpatterns = patterns('label.views.api',
    url(r'^get-updates/$', 'get_updates'),
    url(r'^update-ack/(?P<label_upc>[\w\d-]+)/$', 'update_ack'),
    url(r'^get-bitmap/(?P<label_upc>[\w\d-]+)/$', 'get_bitmap'),
    url(r'^get-label-status/$', 'get_label_status', name='get_label_status'),
)

urlpatterns = patterns('label.views.dashboard',
    url(r'^products/', 'product_list', {}, name='products'),
    url(r'^products/', 'product_list', {}, name='dashboard_main'),
    url(r'^add-labels/', 'add_labels', {}, name='add_labels'),
    url(r'^update/(?P<client_id>[\w\d-]+)/', 'update_labels'),
) + api_urlpatterns
