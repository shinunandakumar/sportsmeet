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

        if role == UserRole.FACULTY_COORDINATOR and obj:
            return (
                obj.department == request.user.department
                and obj.role in (
                    UserRole.STUDENT,
                    UserRole.STUDENT_COORDINATOR,
                )
            )

        return False

    def has_delete_permission(self, request, obj=None):
        role = self._role(request)
        return role == UserRole.ADMIN

    def get_readonly_fields(self, request, obj=None):
        role = self._role(request)

        if role == UserRole.ADMIN:
            return ()

        if role == UserRole.FACULTY_COORDINATOR:
            return (
                "email",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )

        return super().get_readonly_fields(request, obj)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        role = self._role(request)
        
        if db_field.name == "department" and role == UserRole.FACULTY_COORDINATOR:
            kwargs["queryset"] = Department.objects.filter(
                id=request.user.department_id
            )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        role = self._role(request)
        
        if role == UserRole.FACULTY_COORDINATOR:
            return qs.filter(department=request.user.department)
        
        return qs
    
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        role = self._role(request)
        
        if db_field.name == "role" and role == UserRole.FACULTY_COORDINATOR:
            kwargs["choices"] = [
                (UserRole.STUDENT, "Student"),
                (UserRole.STUDENT_COORDINATOR, "Student Coordinator"), #only assign student coordinator
            ]
        
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
    
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Auto-assign coordinators to department
        if obj.role == UserRole.FACULTY_COORDINATOR and obj.department:
            Department.objects.filter(
                faculty_coordinator=obj
            ).exclude(
                id=obj.department.id
            ).update(faculty_coordinator=None)

            obj.department.faculty_coordinator = obj
            obj.department.save()

        elif obj.role == UserRole.STUDENT_COORDINATOR and obj.department:
            Department.objects.filter(
                student_coordinator=obj
            ).exclude(
                id=obj.department.id
            ).update(student_coordinator=None)

            obj.department.student_coordinator = obj
            obj.department.save()