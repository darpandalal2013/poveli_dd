from django.db.models import CharField, ForeignKey, signals
from django.forms.models import ModelChoiceField
from django.forms.widgets import Select
from django.utils.safestring import mark_safe

#from common.widgets import ClientAssetFieldWidget, ClientAssetFormField

try:
    import uuid
except ImportError:
    from django.utils import uuid

from south.modelsinspector import add_introspection_rules


_UUID_LEN = 36  # Length of UUID like 5a5e0e7d-eff3-4f74-bd74-d651f3f05453.

class UUID4Field(CharField):
    """ UUID4 field. Supports auto-generation.
        Allows to transform a generated value before saving.
    """

    def __init__(self, auto=True, transform_value=None, **kwargs):
        if auto:
            if transform_value:
                if not callable(transform_value):
                    raise TypeError('"transform_value" argument must be a callable.')
                elif 'max_length' not in kwargs:
                    raise ValueError('When "transform_value" argument is present, "max_length" is also required.')
            else:
                if 'max_length' not in kwargs:
                    kwargs['max_length'] = _UUID_LEN
                elif kwargs['max_length'] < _UUID_LEN:
                    raise ValueError('"max_length" argument can not be less than %d.' % _UUID_LEN)
            kwargs['blank'] = False
            kwargs['editable'] = False
            kwargs['unique'] = True
            kwargs['db_index'] = True

        self._auto = auto
        self._transform_value = transform_value
        CharField.__init__(self, **kwargs)

    def contribute_to_class(self, cls, name):
        super(UUID4Field, self).contribute_to_class(cls, name)
        # Subscribe to instance creation notifications.
        signals.post_init.connect(self._post_init, sender=cls)

    def _post_init(self, instance, *args, **kwargs):
        # if auto == True and value is not set.
        if self._auto and not getattr(instance, self.attname, None):
            setattr(instance, self.attname, self.generate_value(instance))

    def generate_value(self, instance_or_class):
        # Generate a new value.
        value = '%s' % uuid.uuid4()
        if self._transform_value:
            value = self._transform_value(instance_or_class, value)
            if len(value) > self.max_length:
                raise ValueError('transform_value() returned a string longer than %d characters:%s' %
                                 (self.max_length, value))
        return value
                
        
# This is a model field.
class ClientAssetField(ForeignKey):
    """ Foreign key to client.ClientAsset with custom widget.
    """

    def __init__(self, auto=True, transform_value=None, **kwargs):
        params = dict(null=True, blank=True)
        params.update(kwargs)
        # Note: We used to override the to= argument with 'client.ClientAsset' string
        # to ensure that this field can refer to client.ClientAsset model only.
        # However, we found that this method is incompatible with South.
        # It is commented out for now, however we need a better way.
        # TODO(sbolgov): Find a South-compatible way to enforce the restriction.
        if 'to' not in params:
            params['to'] = 'client.ClientAsset'
        ForeignKey.__init__(self, **params)

    def formfield(self, **kwargs):
        params = dict(form_class=ClientAssetFormField)
        params.update(kwargs)
        return super(ClientAssetField, self).formfield(**params)

# needed by south since this is a custom field
add_introspection_rules([], [
    "^common\.fields\.UUID4Field",
    "^common\.fields\.ClientAssetField",
])
