from django.conf.urls.defaults import *

urlpatterns = patterns('label.views.dashboard',
    url(r'^products/', 'product_list', {}, name='products'),
    url(r'^products/', 'product_list', {}, name='dashboard_main'),
    url(r'^add-labels/', 'add_labels', {}, name='add_labels'),
    url(r'^update-labels/', 'update_labels', {}, name='update_labels'),

	url(r'^template_list/', 'template_list', {}, name='template'),
	url(r'^template_add/', 'template_add', {}, name='templateadd'),
	url(r'^template_update/(?P<label_id>[\w\d-]+)/', 'template_edit', {}, name='updatetemplate'),
) 
