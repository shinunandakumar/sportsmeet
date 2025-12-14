from django.urls import path

from accounts.admin_site import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
]
