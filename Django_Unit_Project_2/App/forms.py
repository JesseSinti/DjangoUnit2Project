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


class AddEventForm(forms.Form):
    organizer = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': "Enter Your Organization's Name"}),
        required=True
    )
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': "Name of Your Event"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Your Event's Description"}),required=True)
    banner_image = forms.FileField(required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Enter Your Event's Location"}), required=True)
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'placeholder': "Enter Your Event's Starting Time"}), required=True)
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'placeholder': "Enter Your Event's Ending Time"}), required=True)
    capacity = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': "Enter Your Event's Capacity"}), required=True)

    class Meta:
        model = Event
        fields = ('organizer','title','description','banner_image','location','start_time','end_time','capacity')

class TickerTierForm(forms.Form):
    ticket_type = forms.CharField(widget=forms.TextInput(attrs={}))