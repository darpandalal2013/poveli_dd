from django.contrib.auth import authenticate, login

from registration import signals
from registration.backends.default import DefaultBackend

from accounts.forms import RegistrationForm
from accounts.models import UserProfile


class RegistrationBackend(DefaultBackend):
    """A custom registration backend that stores users details and other profile info"""
    def get_form_class(self, request):
        return RegistrationForm
    
    def register(self, request, **kwargs):
        """Register the new user."""
        
        # create user and store the first/last name
        new_user = super(RegistrationBackend, self).register(request, **kwargs)
        new_user.first_name = kwargs['first_name']
        new_user.last_name = kwargs['last_name']
        new_user.is_active = True   # make them active right away
        new_user.save()
        
        # store the common profile data
        UserProfile.objects.create(user=new_user, newsletter_subscribe=kwargs['newsletter_subscribe'])
        
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        
        # login this user....
        authenticated_user = authenticate(username=kwargs['username'], password=kwargs['password1'])
        if authenticated_user is not None:
            login(request, authenticated_user)
        
        return new_user
