from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from django.db.models import Q
from functools import wraps
from .forms import *
from .filters import *

# ==============================================================================
# 1. DECORATORS
# ==============================================================================

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


# ==============================================================================
# 2. AUTHENTICATION (Login, Logout, Signup)
# ==============================================================================

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


def organization_signup(request):
    """Sign up a new User and create a new Organization simultaneously."""
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
                login(request, user)
            return redirect('admin_dashboard', org_id=organization.id)
    else:
        form = OrganizationSignupForm()

    return render(request, 'organization_signup.html', {'form': form})


def request_join_organization(request):
    """
    Sign up a NEW User and request to join an EXISTING Organization.
    """
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


# ==============================================================================
# 3. PUBLIC VIEWS (Home, Search)
# ==============================================================================

def home_view(request): 
    event_filter = EventFilter(request.GET, queryset=Event.objects.all())
    
    return render(request, 'home.html', {'filter' : event_filter, 'filter_active' :  bool(request.GET), 'Event' : event_filter.qs.distinct()})


def search_view(request):
    query = request.GET.get('query', '')
    events = Event.objects.all()
    if query:
        events = events.filter(Q(title__icontains=query))
    return render(request,'home.html', {'Events' : events, 'SearchActive' : bool(request.GET)})


# ==============================================================================
# 4. DASHBOARDS (Admin, User, Customer)
# ==============================================================================

@login_required
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
    
    organization = Organization.objects.get(id=org_id)
    organization_users = OrganizationMembership.objects.filter(organization=organization)
    events = Event.objects.filter(organization=organization)
    total_users = len(organization_users)
    total_events = len(events)
    total_pending = len(pending_memberships)

    return render(request, 'admin_dashboard.html', {
        'organization_id': org_id,
        'pending_memberships': pending_memberships,
        'organization_users' : organization_users,
        'organization_events' : events,
        'total_users' : total_users,
        'total_events' : total_events,
        'pending' : total_pending,
    })


def search_users(request):
    """
    Used within the Admin Dashboard to search for users.
    """
    query = request.GET.get('query', '')
    current_user = OrganizationMembership.objects.get(user=request.user)
    organization = Organization.objects.get(name=current_user.organization.name)
    users = OrganizationMembership.objects.filter(organization=organization)
    if query:
        users = users.filter(Q(user__username__icontains=query))
    
    pending_memberships = OrganizationMembership.objects.filter(
        organization=organization,
        status='pending'
    ).select_related('user')
    organization_users = OrganizationMembership.objects.filter(organization=organization)
    events = Event.objects.filter(organization=request.user)
    total_users = len(organization_users)
    total_events = len(events)
    total_pending = len(pending_memberships)
    
    return render(request,'admin_dashboard.html', {
        'Users' : users, 
        'SearchActive' : bool(request.GET),
        'pending_memberships': pending_memberships,
        'organization_users' : organization_users,
        'organization_events' : events,
        'total_users' : total_users,
        'total_events' : total_events,
        'pending' : total_pending,})

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

    my_events = Event.objects.filter(
        organization=membership.organization
    ).order_by('-created_at')

    return render(request, "org_user_dashboard.html", {
        "organization": membership.organization,
        "membership": membership,
        "my_events": my_events, 
    })


@login_required
def customer_dashboard(request):
    return render(request, "customer_dashboard.html")


# ==============================================================================
# 5. MEMBERSHIP ACTIONS (Join, Cancel, Update)
# ==============================================================================

@login_required
def choose_organization(request):
    all_memberships = OrganizationMembership.objects.filter(
        user=request.user
    ).select_related("organization").order_by('-joined_at')

    active_memberships = all_memberships.filter(status='active')
    pending_memberships = all_memberships.filter(status='pending')
    
    can_join_new = not (active_memberships.exists() or pending_memberships.exists())

    if request.method == 'POST':
        form = JoinExistingOrganizationForm(request.user, request.POST)
        if form.is_valid():
            OrganizationMembership.objects.create(
                user=request.user,
                organization=form.cleaned_data['organization'],
                role=form.cleaned_data['role'],
                status='pending'
            )
            messages.success(request, "Request sent successfully.")
            return redirect('choose_organization')
    else:
        form = JoinExistingOrganizationForm(request.user)

    return render(request, "choose_organization.html", {
        "active_memberships": active_memberships,
        "pending_memberships": pending_memberships,
        "join_form": form,
        "can_join_new": can_join_new,
    })


@login_required
@require_POST
def cancel_organization_request(request, pk):
    membership = get_object_or_404(OrganizationMembership, pk=pk, user=request.user)

    if membership.status == 'pending':
        org_name = membership.organization.name
        membership.delete()
        messages.success(request, f"Request to join {org_name} has been cancelled.")
    else:
        messages.error(request, "You cannot cancel a membership that is already active or kicked.")

    return redirect('choose_organization')


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


# ==============================================================================
# 6. EVENT MANAGEMENT (Add Event, Tickets)
# ==============================================================================

# views.py

@login_required
def AddEvent(request):
    if request.method == "POST":
        form = AddEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            
            membership = OrganizationMembership.objects.filter(
                user=request.user, 
                status='active'
            ).first()

            if not membership:
                messages.error(request, "You must belong to an organization to create events.")
                return redirect('home_page')

            event.organization = membership.organization
            
            event.save()
            return redirect('ticket_tier', pk=event.id)
    else: 
        form = AddEventForm()
    
    return render(request, 'addEvent.html', {'form': form})


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