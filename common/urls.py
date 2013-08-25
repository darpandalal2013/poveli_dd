from django.conf.urls.defaults import *


urlpatterns = patterns('common.views',
    url(r'^$', 'home_redirector', {}, name='home_redirector'),
    url(r'^choose-company/$', 'choose_client', {}, name='choose_client'),
)
