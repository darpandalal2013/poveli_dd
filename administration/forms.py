from django import forms

from client.models import Client
from common.utils import decorate_bound_field

decorate_bound_field()

class CreateClientForm(forms.ModelForm):

    class Meta:
        model = Client
        exclude = ('sourcecode', 'created_by', 'updated_by', 'old_id')
