"""
URL configuration for Django_Unit_Project_2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App import views as v
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('About Us', v.About_Us, name='aboutus'),
    path('FAQ/Page', v.FAQ_View, name='faqview'),
    path('admin/', admin.site.urls),
    path('checkout-cart', v.Checkout_Cart, name='checkoutcart'),
    path('<int:pk>/remove_ticket/', v.Remove_Ticket_Cart, name='remove_ticket'),
    path('add-to-cart/<int:pk>/', v.Add_Ticket_Cart, name='Add_Ticket_Cart'),
    path('cart/', v.cart, name='cart'),
    path('payment/success/', v.Payment_Success),
    path('<int:pk>/checkout/', v.CheckoutView, name="purchase_ticket"),
    path('event/page/', v.Event_Page, name='event_page'),
    path('', v.home_view, name='home_page'),
    path('searchbar', v.search_view, name='Search_query'),
    path('searchusers/', v.search_users, name='search_users'),
    path('login/', v.login_view, name='login'),
    path('logout/', v.logout_view, name='logout'),
    path('organization-signup/', v.organization_signup, name='org-signup'),
    path('customer-signup/', v.customer_signup, name='customer-signup'),
    path('addevent/', v.AddEvent, name="addevent"),
    path('<int:pk>/ticketier/', v.SetTicketTier, name="ticket_tier"),
    path('org/<int:org_id>/admin/', v.admin_dashboard, name='admin_dashboard'),
    path('membership/<int:membership_id>/<str:action>/', v.update_membership_status, name='update_membership_status'),
    path('organization/join/', v.request_join_organization, name='join_organization'),
    path('dashboard/customer/', v.customer_dashboard, name='customer_dashboard'),
    path('dashboard/org/<int:org_id>/user/', v.user_dashboard, name='org_user_dashboard'),
    path('organization/select/', v.choose_organization, name='choose_organization'),
    path('organization/cancel-request/<int:pk>/', v.cancel_organization_request, name='cancel_organization_request'),
    path('non/active/', v.non_active_view, name='non_active_goon'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)