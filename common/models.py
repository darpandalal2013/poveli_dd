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

    def _trim_char_field(self, field_name):
        if getattr(self, field_name, ''):
            setattr(self, field_name, getattr(self, field_name, '')[:self._meta.get_field_by_name(field_name)[0].max_length])

    ### Managers
    #objects = models.Manager()
    objects = ActiveObjectsManager()
    active_objects = ActiveObjectsFilterManager()

class DBNow(object):
    """
    DBNow offers a way to update or query by the database timestamp.

        drafts = DraftVideo.objects.filter(created_on__gt=DBNow())

        or:

        draft.created_on = DBNow()
        draft.save()
        
        NOTE: Currently doesn't work on new object creations (inserts). Alternatively you can
        save the row with a datetime.now() first and then assign DBNow() and save to perform 
        an update instead.
    """
    def __str__(self):
        return 'DATABASE NOW()'
    def as_sql(self, qn, val):
        return 'NOW()', {}
    @classmethod
    def patch(cls, field):
        orig_prep_db = field.get_db_prep_value
        orig_prep_lookup = field.get_prep_lookup
        orig_db_prep_lookup = field.get_db_prep_lookup

        def prep_db_value(self, value, connection, prepared=False):
            return value if isinstance(value, cls) else orig_prep_db(self, value, connection, prepared)

        def prep_lookup(self, lookup_type, value):
            return value if isinstance(value, cls) else orig_prep_lookup(self, lookup_type, value)

        def prep_db_lookup(self, lookup_type, value, connection, prepared=True):
            return value if isinstance(value, cls) else orig_db_prep_lookup(self, lookup_type, value, connection=connection, prepared=True)

        field.get_db_prep_value = prep_db_value
        field.get_prep_lookup = prep_lookup
        field.get_db_prep_lookup = prep_db_lookup

# DBNow Activator
DBNow.patch(models.DateTimeField)
