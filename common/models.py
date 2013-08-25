from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

class ActiveObjectsManager(models.Manager):
    """
    This is a model manager which will return all objects with active=True. They will be order by creation_date too.
    """
    use_for_related_fields = True

    def all_active(self):
        return self.filter(active=True)

class ActiveObjectsFilterManager(models.Manager):
    """
    This is a model manager which will return all objects with active=True. They will be order by creation_date too.
    """
    def get_query_set(self):
        return super(ActiveObjectsFilterManager, self).get_query_set().filter(active=True).order_by('-created_on')

class BaseModel(models.Model):
    """
    Model for data objects that are not supposed to be modified after creation.
    Also this is a parent class for BaseModel.
    """
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(default=datetime.now, editable=False,
        blank=True, db_index=True)

    active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

    ### Managers
    #objects = models.Manager()
    objects = ActiveObjectsManager()
    active_objects = ActiveObjectsFilterManager()
