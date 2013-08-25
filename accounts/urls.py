from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views

from registration.views import register

from accounts.forms import UserAuthenticationForm


urlpatterns = patterns('accounts.views',
    url(r'^register/$', register,
        { 'backend': 'accounts.backends.custom.RegistrationBackend' },
        name='registration_register'),
    url(r'^login/modal/$',
        auth_views.login,
        {'template_name': 'registration/fragments/login_modal.html', 'authentication_form': UserAuthenticationForm},
        name='auth_login_modal'),
    url(r'^activate/(?P<activation_key>\w+)/$',
        'user_activate',
        name='registration_activate'),

    url(r'^login/$', auth_views.login,
        {'template_name': 'registration/login.html', 'authentication_form': UserAuthenticationForm},
        name='auth_login'),
    (r'^logout/$', auth_views.logout,
        {'next_page': '/'}),

    (r'', include('registration.backends.default.urls')),

    url(r'^company/(?P<client_id>[\w\d-]+)/profile/$', 'profile_page', name='profile_page'),
    url(r'^company/(?P<client_id>[\w\d-]+)/profile/edit/$', 'profile_edit', name='profile_edit'),
    url(r'^company/(?P<client_id>[\w\d-]+)/user-create$', 'user_create', name='user_create'),
    url(r'^company/(?P<client_id>[\w\d-]+)/userprofile/(?P<userprofile_id>[\w\d-]+)/delete$', 'user_delete', name='user_delete'),
    url(r'^company/(?P<client_id>[\w\d-]+)/userprofile/(?P<userprofile_id>[\w\d-]+)/resend$', 'user_email_resend', name='user_email_resend'),
    url(r'^company/(?P<client_id>[\w\d-]+)/users$', 'users_list', name='users_list'),
)
