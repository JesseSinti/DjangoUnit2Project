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
from django.conf import settings 
import stripe 
from django.http import HttpResponse
from decimal import Decimal 
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.mail import EmailMessage 
import json
# ============================================================================================================
#                                                 1. DECORATORS
# ============================================================================================================

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


# =============================================================================================================
#                                    2. AUTHENTICATION (Login, Logout, Signup)
# =============================================================================================================

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
                user=user, status__in=['active', 'Non-active']
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


# =============================================================================================================
#                                         3. PUBLIC VIEWS (Home, Search)
# =============================================================================================================

def home_view(request): 
    event_filter = EventFilter(request.GET, queryset=Event.objects.all().prefetch_related('ticket_tiers').order_by('-date'))
    
    return render(request, 'home.html', {'filter' : event_filter, 'filter_active' :  bool(request.GET), 'Event' : event_filter.qs.distinct()})


def search_view(request):
    query = request.GET.get('query', '')
    events = Event.objects.all().prefetch_related('ticket_tiers')
    if query:
        events = events.filter(Q(title__icontains=query))
    return render(request,'home.html', {'Events' : events, 'SearchActive' : bool(request.GET)})


# =============================================================================================================
#                                       4. DASHBOARDS (Admin, User, Customer)
# =============================================================================================================

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
    admin = User.objects.get(id=request.user.id)

    return render(request, 'admin_dashboard.html', {
        'organization_id': org_id,
        'pending_memberships': pending_memberships,
        'organization_users' : organization_users,
        'organization_events' : events,
        'total_users' : total_users,
        'total_events' : total_events,
        'pending' : total_pending,
        'admin' : admin,
    })



def Event_Page(request):
    User = OrganizationMembership.objects.get(user=request.user)
    organization = Organization.objects.get(name=User.organization.name)
    Events = Event.objects.filter(organization=organization).prefetch_related('ticket_tiers')

    return render(request, 'event_page.html', {'Events' : Events})



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
    events = Event.objects.filter(organization=organization)
    total_users = len(organization_users)
    total_events = len(events)
    total_pending = len(pending_memberships)
    admin = User.objects.get(id=request.user.id)
    
    return render(request,'admin_dashboard.html', {
        'Users' : users, 
        'SearchActive' : bool(request.GET),
        'pending_memberships': pending_memberships,
        'organization_users' : organization_users,
        'organization_events' : events,
        'total_users' : total_users,
        'total_events' : total_events,
        'pending' : total_pending,
        'admin' : admin})

@login_required
def user_dashboard(request, org_id):
    membership = OrganizationMembership.objects.filter(
        user=request.user,
        organization_id=org_id,
        status__in=['active', 'Non-active']
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
    user = request.user
    orders = Order.objects.filter(user=user)

    
    total = sum(order.total_price for order in orders)

    total_orders = orders.count()

    return render(request, "customer_dashboard.html", {
        'Customer': user,
        'total_orders': total_orders,
        'Orders': orders,
        'Total_expenses': total
    })




# =============================================================================================================
#                                       5. MEMBERSHIP ACTIONS (Join, Cancel, Update)
# =============================================================================================================

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
        membership.delete()
        messages.success(request, f"{membership.user.username} removed!")
    elif action == 'non-active':
        membership.status = 'Non-active'
        membership.save()
        messages.success(request, f"{membership.user.username} set to non-active")
    else:
        messages.error(request, "Invalid action.")

    return redirect('admin_dashboard', org_id=membership.organization.id)

@login_required
def non_active_view(request):
    return render(request,'non_active_goon.html')


# ==============================================================================================================
#                                           6. EVENT MANAGEMENT (Add Event, Tickets, Orders)
# ===============================================================================================================

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

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def Checkout_Cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = TicketsSaved.objects.filter(cart=cart)

    if not cart_items.exists():
        return redirect('/cart/')

    line_items = []
    metadata_items = []

    for cart_item in cart_items:
        ticket = cart_item.ticket

        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(ticket.price * Decimal(107.25)),  
                'product_data': {
                    'name': f"{ticket.event.title} – {ticket.type}",
                },
            },
            'quantity': cart_item.quantity,
        })

        metadata_items.append({
            'tier_id': ticket.id,
            'quantity': cart_item.quantity,
            'price': str(ticket.price),
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        line_items=line_items,
        metadata={
            'user_id': str(request.user.id),
            'cart_items': json.dumps(metadata_items),
        },
        success_url="http://127.0.0.1:8000/payment/success/?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/cart/",
    )

    return redirect(checkout_session.url)


@login_required
def CheckoutView(request, pk):
    ticket = TicketTier.objects.get(id=pk)
    quantity = 1
    image_url = None
    MY_DOMAIN = f"{request.scheme}://{request.get_host()}"
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency':'usd',
                'unit_amount':int(ticket.price * Decimal(107.25)),
                'product_data': {
                    "name":ticket.type,
                    'images':[image_url]
                },
            },
            'quantity':1,
        },
    ],
    metadata = {
        'tier_id':ticket.id,
        'user_id':request.user.id,
        'quantity' : quantity
    },
    mode='payment',
    success_url = "http://127.0.0.1:8000/payment/success/?session_id={CHECKOUT_SESSION_ID}",

    cancel_url=MY_DOMAIN + f'/pricing/{pk}',
    )
    return redirect(checkout_session.url)


def Payment_Success(request):
    # This collects the payment's session id
    session_id = request.GET.get("session_id")

# if the session isn't does't have the id then it cant create an order 
    if not session_id:
        return HttpResponse("Missing session ID", status=400)
    
    # Gets the actual session using its id 
    session = stripe.checkout.Session.retrieve(session_id)

    # makes sure the session had a succesful payment beofre allowing the creation of a order 
    if session.payment_status != 'paid':
        return HttpResponse("Payment not completed", status=400)
    

    # Gets the data that was passed to the checkout session
    metadata = session.metadata
    if "cart_items" in metadata:
        handle_cart_payment(
            user_id=metadata["user_id"],
            cart_items=json.loads(metadata["cart_items"]),
            payment_id=session.payment_intent
        )
    else:
    # runs the function if the payment was succesful 
        Handle_Successful_Payment(
            user_id=metadata["user_id"],
            tier_id=metadata["tier_id"],
            quantity=int(metadata["quantity"]),
            payment_id=session.payment_intent
        )
    return redirect('home_page')

def send_ticket_email(order, user):
    tickets = Ticket.objects.filter(order=order)

    subject = "Your Tickets"
    body = f"""
Thank you for your purchase!

Attached are your {tickets.count()} ticket(s).
Please bring the QR codes with you to the event.
        """
    from_email = "jessecorbin75@gmail.com"


    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[user.email],
    )

    for ticket in tickets:
        if not ticket.qr_code_image:
            generate_qr_code(ticket)
            ticket.save()

        email.attach_file(ticket.qr_code_image.path)

    email.send(fail_silently=False)


def generate_qr_code(ticket):
    # This makes the qr code using the installs and imports 
    qr = qrcode.make(str(ticket.ticket_id))
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    # saves the produced qr code to the ticket image 
    ticket.qr_code_image.save(
        f"{ticket.ticket_id}.png",
        File(buffer),
        save=False
    )

def handle_cart_payment(*, user_id, cart_items, payment_id):
    with transaction.atomic():
        user = User.objects.get(id=user_id)

        order = Order.objects.create(
            user=user,
            total_price=Decimal("0.00")
        )

        total = Decimal("0.00")

        for item in cart_items:
            tier = TicketTier.objects.select_for_update().get(id=item["tier_id"])
            quantity = int(item["quantity"])

            if tier.quantity < quantity:
                raise Exception("Not enough tickets")

            tier.quantity -= quantity
            tier.save()

            Ticket.objects.bulk_create([
                Ticket(order=order, tier=tier)
                for _ in range(quantity)
            ])

            total += tier.price * quantity
            taxes = total  * Decimal(0.0725)

            true_total = total + taxes
        order.total_price = true_total
        order.save()

        send_ticket_email(order, user)

def Handle_Successful_Payment(*, user_id, tier_id, quantity, payment_id):
    with transaction.atomic():
        user = User.objects.get(id=user_id)
        tier = TicketTier.objects.select_for_update().get(id=tier_id)

        if tier.quantity < quantity:
            raise Exception("Not Enough Tickets")

        tier.quantity -= quantity
        tier.save()
        total = tier.price * quantity 
        taxes = total * Decimal(0.0725)
        true_total =  total + taxes
        order = Order.objects.create(
            user=user,
            total_price=true_total
        )

        Ticket.objects.bulk_create([
            Ticket(order=order, tier=tier)
            for _ in range(quantity)
        ])

        send_ticket_email(order, user)


@require_POST
def Add_Ticket_Cart(request, pk):
    # 1. Get the quantity from the form data (Default to 1 if missing)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    # 2. Get or Create Cart
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # 3. Get the Ticket Tier
    added_ticket = get_object_or_404(TicketTier, id=pk)

    # 4. Get or Create the item in the cart
    ticket_item, created = TicketsSaved.objects.get_or_create(
        cart=cart, 
        ticket=added_ticket,
        # You can set defaults here if your model requires it
        # defaults={'quantity': quantity} 
    )

    # 5. Update Quantity logic
    if not created:
        # If item already exists in cart, ADD the new amount to existing amount
        ticket_item.quantity += quantity
        ticket_item.save()
    else:
        # If it's a new item, set the initial quantity
        ticket_item.quantity = quantity
        ticket_item.save()
    
    return redirect('cart')

@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    ticket = cart.tickets.all()
    total = cart.total()
    taxes = total * Decimal(.0725)
    true_total = total + taxes

    return render(request, 'cart.html', {'cart':cart, 'tickets':ticket, 'total' : total, 'Taxes' : taxes, 'true_total' : true_total})

def Remove_Ticket_Cart(request,pk):
    cart = Cart.objects.get(user=request.user)

    ticket = TicketsSaved.objects.get(id=pk, cart=cart)
    remove_qty = int(request.POST.get('quantity', 1))
    if remove_qty >= ticket.quantity:
        ticket.delete()
    else: 
        ticket.quantity -= remove_qty
        ticket.save()

    return redirect('cart')


        
    
        