from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import *

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

class CustomOrganizationUserCreationForm(forms.Form):
    username = forms.CharField(required=True, label='Username')
    first_name = forms.CharField(required=True, label='First Name', max_length=20)
    last_name = forms.CharField(required=True, label='Last Name', max_length=25)
    email = forms.EmailField(required=True, label='Email')
    password = forms.CharField(required=True, label='Password', min_length=8)
    organization = forms.CharField(required=True, label='Organization')
    is_admin = forms.BooleanField(required=True, label='Admin')

    class Meta(forms.ModelForm):
        class Meta:
            model = OrganizationUsers
            fields = ['username', 'email', 'first_name', 'last_name', 'password', 'organization_name', 'is_admin']