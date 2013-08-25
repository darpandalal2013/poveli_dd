from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from accounts.models import UserProfile


# We use e-mails as usernames.
# Django does not accept usernames longer than 30 characters.
# This form solves that problem.
class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        # Same label as in AuthenticationForm.
        label=AuthenticationForm.base_fields['username'].label,
        # Take the max_length from User.email field.
        max_length=User._meta.get_field_by_name('email')[0].max_length,
    )


class UserProfileForm(forms.ModelForm):
    """
    Lets a user edit its profile.
    """
    first_name = forms.CharField(label='First Name', required=False)
    last_name = forms.CharField(label='Last Name', required=False)

    class Meta:
        model = UserProfile
        exclude = ('clients', 'user', 'active', 'created_by')


class UserCreateForm(forms.Form):
    """
    Used to add a new user to the client for access.
    """
    email = forms.EmailField(max_length=255)

class UserActivateForm(forms.Form):
    first_name = forms.CharField(label='First Name', required=True)
    last_name = forms.CharField(label='Last Name', required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=50)
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=50)

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data
