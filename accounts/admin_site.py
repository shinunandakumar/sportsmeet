from django.contrib.admin import AdminSite

from accounts.models import UserRole


class RBACAdminSite(AdminSite):
    site_header = "Sports Meet Admin"
    site_title = "Sports Meet Admin"
    index_title = "Dashboard"

    def has_permission(self, request):
        user = request.user
        if not user.is_authenticated:
            return False
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        return user.is_staff and getattr(user, "role", None) != UserRole.STUDENT


admin_site = RBACAdminSite(name="rbac_admin")
