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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', v.home_view, name='home_page'),
    path('signup/', v.signup_view, name='signup'),
    path('login/', v.login_view, name='login'),
    path('logout/', v.logout_view, name='logout'),
    path('organization-login/', v.organization_login_view, name='org-login'),
    path('organization-signup/', v.organization_signup_view, name='org-signup')
]
