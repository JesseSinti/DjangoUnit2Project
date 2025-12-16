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
    path('admin/', admin.site.urls),
    path('', v.home_view, name='home_page'),
    path('searchbar', v.search_view, name='Search_query'),
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)