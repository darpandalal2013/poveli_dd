from django.conf.urls.defaults import *

urlpatterns = patterns('label.views.dashboard',
    url(r'^products/', 'product_list', {}, name='products'),
    url(r'^products/', 'product_list', {}, name='dashboard_main'),
    url(r'^add-labels/', 'add_labels', {}, name='add_labels'),
    url(r'^update-labels/', 'update_labels', {}, name='update_labels'),
) 
