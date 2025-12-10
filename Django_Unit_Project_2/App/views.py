from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home_view(request): 
    return render(request, 'home.html', None)

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
    return render(request, 'signup.html', {'form':form})

def organization_signup_view(request):
    if request.method == 'POST':
        form = CustomOrganizationUserCreationForm(request.POST)
        if form.is_valid:
            user = form.save()
            login(request, user)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            request.session['user_data'] = {'firstname':first_name, 'lastname':last_name}
            return redirect('home')
    else:
        form = CustomOrganizationUserCreationForm()
    return render(request, 'organization_signup.html', {'form':form})

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

def organization_login_view(request):
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
            return redirect('org-login')
    return render(request, 'organization_login.html', {})

def logout_view(request):
    logout(request)
    messages.success(request, "You were logged out.")
    return redirect('register')
