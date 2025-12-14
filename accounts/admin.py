from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.admin_site import admin_site
from accounts.models import Department, User, UserRole


class RoleAdminPermissionMixin:
    model_key = None

    def _role(self, request):
        user = request.user
        if not user.is_authenticated:
            return None
        if user.is_superuser:
            return UserRole.ADMIN
        return getattr(user, "role", None)

    def has_view_permission(self, request, obj=None):
        role = self._role(request)
        if role is None:
            return False
        if role == UserRole.ADMIN:
            return True
        if role == UserRole.FACULTY:
            return True
        if role == UserRole.FACULTY_COORDINATOR:
            return True
        if role == UserRole.STUDENT_COORDINATOR:
            return self.model_key in {"meet", "category", "event"}
        return False

    def has_add_permission(self, request):
        role = self._role(request)
        if role == UserRole.ADMIN:
            return True
        if role == UserRole.FACULTY_COORDINATOR:
            return self.model_key in {"meet", "category", "event"}
        return False

    def has_change_permission(self, request, obj=None):
        role = self._role(request)
        if role == UserRole.ADMIN:
            return True
        if role == UserRole.FACULTY_COORDINATOR:
            return self.model_key in {"meet", "category", "event"}
        return False

    def has_delete_permission(self, request, obj=None):
        role = self._role(request)
        if role == UserRole.ADMIN:
            return True
        if role == UserRole.FACULTY_COORDINATOR:
            return self.model_key in {"meet", "category", "event"}
        return False


@admin.register(Department, site=admin_site)
class DepartmentAdmin(RoleAdminPermissionMixin, admin.ModelAdmin):
    model_key = "department"
    list_display = ("name", "faculty_coordinator", "student_coordinator")
    search_fields = ("name", "faculty_coordinator__email", "student_coordinator__email")


@admin.register(User, site=admin_site)
class UserAdmin(RoleAdminPermissionMixin, DjangoUserAdmin):
    model_key = "user"

    ordering = ("email",)
    list_display = ("email", "role", "department", "is_active", "is_staff")
    list_filter = ("role", "department", "is_active")
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Profile"), {"fields": ("role", "department")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "department", "is_active"),
            },
        ),
    )

    def has_add_permission(self, request):
        role = self._role(request)
        return role == UserRole.ADMIN

    def has_change_permission(self, request, obj=None):
        role = self._role(request)
        if role == UserRole.ADMIN:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        role = self._role(request)
        return role == UserRole.ADMIN

    def get_readonly_fields(self, request, obj=None):
        role = self._role(request)
        if role == UserRole.ADMIN:
            return ()
        return ("email", "role", "department", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")
