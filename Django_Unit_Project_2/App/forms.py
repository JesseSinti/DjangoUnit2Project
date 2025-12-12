from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.hashers import make_password

class OrganizationSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)

    organization_name = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address', 'password1', 'password2', 'organization_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = False
        if commit:
            user.save()
        return user
    
class OrganizationJoinRequestForm(UserCreationForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    role = forms.ChoiceField(choices=OrganizationMembership.ROLE_CHOICES, initial='user')

    def save(self, commit=True):
        user = super().save(commit=commit)
        OrganizationMembership.objects.create(
            user=user,
            organization=self.cleaned_data['organization'],
            role=self.cleaned_data['role'],
            status='pending'
        )
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''


    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address', 'password1', 'password2', 'organization', 'role')


    
class CustomerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        if commit:
            user.save()
        return user
    
class AddEventForm(forms.ModelForm):
    organizer = forms.TextInput()
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': "Name of Your Event"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Your Event's Description"}),required=True)
    banner_image = forms.FileInput()
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Enter Your Event's Location"}), required=True)
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'placeholder': "Enter Your Event's Starting Time", 'type' : 'time'}), required=True)
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'placeholder': "Enter Your Event's Ending Time", 'type' : 'time'}), required=True)
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
    price = forms.IntegerField()
    quantity = forms.IntegerField()

    class Meta:
        model = TicketTier
        fields = ('ticket_type', 'price', 'quantity')
