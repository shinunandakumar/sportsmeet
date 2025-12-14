from django.contrib import admin

from accounts.admin import RoleAdminPermissionMixin
from accounts.admin_site import admin_site
from meet.models import Category, Event, Meet


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class EventInline(admin.TabularInline):
    model = Event
    extra = 0


@admin.register(Meet, site=admin_site)
class MeetAdmin(RoleAdminPermissionMixin, admin.ModelAdmin):
    model_key = "meet"

    list_display = ("name", "start_date", "end_date", "status")
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("name",)
    inlines = (CategoryInline,)


@admin.register(Category, site=admin_site)
class CategoryAdmin(RoleAdminPermissionMixin, admin.ModelAdmin):
    model_key = "category"

    list_display = ("name", "meet")
    list_filter = ("meet",)
    search_fields = ("name", "meet__name")
    inlines = (EventInline,)


@admin.register(Event, site=admin_site)
class EventAdmin(RoleAdminPermissionMixin, admin.ModelAdmin):
    model_key = "event"

    list_display = ("name", "category", "event_type", "status")
    list_filter = ("status", "event_type", "category__meet")
    search_fields = ("name", "category__name", "category__meet__name")
