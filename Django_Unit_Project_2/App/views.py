from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .filters import *

def home_view(request): 
    f = TicketFilter(request.GET, queryset=Event.objects.all())
    filter_active = any(param in request.GET for param in request.GET.keys())
    return render(request, 'home.html', {'filter' : f, 'filter_active' : filter_active})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            request.session['user_data'] = {'firstname':first_name, 'lastname':last_name}
            return redirect('home_page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form':form})

def organization_signup_view(request):
    if request.method == 'POST':
        form = CustomOrganizationUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['user_data'] = {
                'firstname': user.first_name,
                'lastname': user.last_name
            }
            return redirect('home_page')
    else:
        form = CustomOrganizationUserCreationForm()

    return render(request, 'organization_signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            first_name = user.first_name
            last_name = user.last_name
            request.session['user_data'] = {
                'firstname': first_name,
                'lastname': last_name
            }
            return redirect('home_page')
        else:
            messages.success(request, "There was an error logging in, Please try again...")
            return redirect('login')
    return render(request, 'login.html', {})

def organization_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['user_data'] = {
                'firstname': user.first_name,
                'lastname': user.last_name
            }
            return redirect('home_page')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('org-login')
    return render(request, 'organization_login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You were logged out.")
    return redirect('home_page')

def AddEvent(request):
    if request.method == "POST":
        
        form = AddEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect('ticket_tier', pk=event.id)
    else: 
        form = AddEventForm()
    return render(request, 'addEvent.html', {'form' : form})

def SetTicketTier(request, pk):
    if request.method == "POST":
        form = TicketTierForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request,'home_page')
    else:
        form = TicketTierForm()
    return render(request, 'ticketTier.html', {'form' : form})