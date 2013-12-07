from django.conf.urls.defaults import *

urlpatterns = patterns('product.views.api',
    url(r'^get-info/(?P<upc>[\w\d-]+)/', 'get_product_info', {}, name='get_product_info'),
) 
