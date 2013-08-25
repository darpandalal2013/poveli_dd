from django.db import models
from django.contrib.auth.models import User

from common.models import BaseModel
from client.models import Client


class UserProfile(BaseModel):
    """
    The standard Django user profile
    """

    user = models.OneToOneField(User)

    # clients this user has access to
    clients = models.ManyToManyField('client.Client', related_name='profiles_of_users_with_access')

    class Meta:
        db_table = u'user_profile'
        
    @property
    def authorized_clients(self):
        """
        Returns a list of authorized clients for the user.
        """
        if self.user.is_superuser or self.user.is_staff:
            return Client.active_objects.all()
        else:
            return self.clients.filter(active=True)

    def save(self, *args, **kwargs):
        # Ensure that UserProfile always has the same primary key as its User.
        if not self.pk:
            self.pk = self.user.pk

        super(UserProfile, self).save(*args, **kwargs)
