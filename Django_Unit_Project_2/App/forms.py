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
    
class AddEventForm(forms.ModelForm):
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': "Name of Your Event"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Your Event's Description"}),required=True)
    banner_image = forms.FileInput()
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Enter Your Event's Location"}), required=True)
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'placeholder': "Enter Your Event's Starting Time"}), required=True)
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'placeholder': "Enter Your Event's Ending Time"}), required=True)
    capacity = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': "Enter Your Event's Capacity"}), required=True)

    class Meta:
        model = Event
        fields = ('organizer','title','description','banner_image','location','start_time','end_time','capacity')

class TicketTierForm(forms.ModelForm):
    TICKET_CHOICES = [
        ('vip', 'VIP'),
        ('general', 'GENERAL'),
        ('basic', 'BASIC'),
    ]

    ticket_type = forms.ChoiceField(choices=TICKET_CHOICES, widget=forms.Select(attrs={'class' : 'form-control'}))
    price = forms.IntegerField(widget=forms.IntegerField())
    quantity = forms.IntegerField(widget=forms.IntegerField())
