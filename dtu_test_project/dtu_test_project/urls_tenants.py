from django.conf.urls import include, url
from django.contrib import admin
from core.tenant_views import TenantView

urlpatterns = [
        url(r'^$', TenantView.as_view()),

    url(
        r'^admin/',
        include(admin.site.urls)),


    ]
