"""dtu_test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from core.views import CreateUser, MainView, CreateSuperUser, CreateTenant

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^create-user/', CreateUser.as_view(), name='create_user'),
    url(r'^create-super-user/', CreateSuperUser.as_view(), name='create_super_user'),
    url(r'^create-tenant/', CreateTenant.as_view(), name='create_tenant'),
    url(r'^', MainView.as_view(), name='main'),
]
