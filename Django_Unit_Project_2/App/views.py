from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .filters import *

def home_view(request): 
    f = TicketFilter(request.GET, queryset=TicketTier.objects.all())
    return render(request, 'home.html', {'filter' : f})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid:
            user = form.save()
            login(request, user)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            request.session['user_data'] = {'firstname':first_name, 'lastname':last_name}
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration.html', {'form':form})

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
            return redirect('home')
        else:
            messages.success(request, "There was an error logging in, Please try again...")
            return redirect('login')
    return render(request, 'login.html', {})

def logout_view(request):
    logout(request)
    messages.success(request, "You were logged out.")
    return redirect('register')
