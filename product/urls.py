from django.conf.urls.defaults import *

urlpatterns = patterns('product.views.api',
    url(r'^(?P<upc>[\w\d-]+)/get-info/', 'get_product_info', {}, name='get_product_info'),
) 
