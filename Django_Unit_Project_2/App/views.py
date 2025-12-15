from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .filters import *
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from django.contrib.auth import login as auth_login

# Home page and dashboards for users
def home_view(request): 
    f = TicketFilter(request.GET, queryset=Event.objects.all())
    filter_active = any(param in request.GET for param in request.GET.keys())
    return render(request, 'home.html', {'filter' : f, 'filter_active' : filter_active})

def org_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, org_id, *args, **kwargs):
        membership = OrganizationMembership.objects.filter(
            user=request.user,
            organization_id=org_id,
            role="admin",
            status="active"
        ).first()

        if not membership:
            messages.error(request, "Admin access required.")
            return redirect("home_page")

        return view_func(request, org_id, *args, **kwargs)

    return wrapper


@org_admin_required
def admin_dashboard(request, org_id):
    try:
        membership = OrganizationMembership.objects.get(
            user=request.user, 
            organization_id=org_id,
            role='admin',
            status='active'
        )
    except OrganizationMembership.DoesNotExist:
        messages.error(request, "You don't have admin access to this organization.")
        return redirect('home_page')

    pending_memberships = OrganizationMembership.objects.filter(
        organization_id=org_id,
        status='pending'
    ).select_related('user')

    return render(request, 'admin_dashboard.html', {
        'organization_id': org_id,
        'pending_memberships': pending_memberships,
    })

@login_required
def update_membership_status(request, membership_id, action):
    membership = get_object_or_404(OrganizationMembership, id=membership_id)
    try:
        admin_membership = OrganizationMembership.objects.get(
            user=request.user,
            organization=membership.organization,
            role='admin',
            status='active'
        )
    except OrganizationMembership.DoesNotExist:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home_page')

    if action == 'approve':
        membership.status = 'active'
        membership.save()
        messages.success(request, f"{membership.user.username} approved!")
    elif action == 'kick':
        membership.status = 'kicked'
        membership.save()
        messages.success(request, f"{membership.user.username} removed!")
    else:
        messages.error(request, "Invalid action.")

    return redirect('admin_dashboard', org_id=membership.organization.id)

@login_required
def user_dashboard(request, org_id):
    membership = OrganizationMembership.objects.filter(
        user=request.user,
        organization_id=org_id,
        status='active'
    ).first()

    if not membership:
        messages.error(request, "You do not belong to this organization.")
        return redirect("home_page")

    return render(request, "org_user_dashboard.html", {
        "organization": membership.organization
    })

def choose_organization(request):
    memberships = OrganizationMembership.objects.filter(
        user=request.user
    ).select_related("organization")

    return render(request, "choose_organization.html", {
        "memberships": memberships
    })

@login_required
def customer_dashboard(request):
    return render(request, "customer_dashboard.html")



# Sign Up pages for users
def organization_signup(request):
    if request.method == 'POST':
        form = OrganizationSignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()

                org_name = form.cleaned_data['organization_name']
                organization = Organization.objects.create(name=org_name)

                OrganizationMembership.objects.create(
                    user=user,
                    organization=organization,
                    role='admin',
                    status='active',
                )
            return redirect('admin_dashboard', org_id=organization.id)
    else:
        form = OrganizationSignupForm()

    return render(request, 'organization_signup.html', {'form': form})

from django.db import transaction


def request_join_organization(request):
    if request.user.is_authenticated:
        return redirect('choose_organization')

    if request.method == 'POST':
        form = OrganizationJoinRequestForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()

            login(request, user)

            messages.success(
                request,
                "Your account was created and your request is pending admin approval."
            )
            return redirect('choose_organization')
    else:
        form = OrganizationJoinRequestForm()

    return render(request, 'join_organization.html', {'form': form})



def customer_signup(request): 
    if request.method == 'POST': 
        form = CustomerSignupForm(request.POST) 
        if form.is_valid(): 
            user = form.save()
            login(request, user)
            return redirect('customer_dashboard') 
    else: 
        form = CustomerSignupForm() 
    return render(request, 'customer_signup.html', {'form': form})

# Login page
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_customer:
                return redirect("customer_dashboard")

            membership = OrganizationMembership.objects.filter(
                user=user, status="active"
            ).first()

            if membership:
                if membership.role == "admin":
                    return redirect("admin_dashboard", org_id=membership.organization.id)
                else:
                    return redirect("org_user_dashboard", org_id=membership.organization.id)

            return redirect("choose_organization")

        else:
            messages.error(request, "Incorrect username or password")

    return render(request, "login.html")


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
    event = Event.objects.get(id=pk)
    if request.method == "POST":
        form = TicketTierForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event
            ticket.save()
            return redirect('home_page')
    else:
        form = TicketTierForm()
    return render(request, 'ticketTier.html', {'form' : form})