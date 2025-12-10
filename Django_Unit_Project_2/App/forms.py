from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth.hashers import make_password

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='First Name', max_length=20)
    last_name = forms.CharField(required=True, label='Last Name', max_length=25)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

class CustomOrganizationUserCreationForm(UserCreationForm):
    organization_name = forms.CharField(required=True)
    is_admin = forms.BooleanField(required=False)

    class Meta(UserCreationForm.Meta):
        model = OrganizationUsers
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "organization_name",
            "is_admin",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''
