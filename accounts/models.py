from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


# -----------------------------
# USER ROLE
# -----------------------------
class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    FACULTY_COORDINATOR = "FACULTY_COORDINATOR", "Faculty Coordinator"
    STUDENT_COORDINATOR = "STUDENT_COORDINATOR", "Student Coordinator"
    FACULTY = "FACULTY", "Faculty"
    STUDENT = "STUDENT", "Student"


# -----------------------------
# GENDER
# -----------------------------
class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"


# -----------------------------
# USER MANAGER
# -----------------------------
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        role = extra_fields.get("role", UserRole.STUDENT)
        extra_fields.setdefault("is_staff", role != UserRole.STUDENT)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)


# -----------------------------
# DEPARTMENT
# -----------------------------
class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    faculty_coordinator = models.OneToOneField(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="faculty_coordinator_department",
    )
    student_coordinator = models.OneToOneField(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="student_coordinator_department",
    )

    def __str__(self):
        return self.name


# -----------------------------
# USER (ONLY ONE!)
# -----------------------------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    register_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.STUDENT
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.is_superuser:
            self.is_staff = self.role != UserRole.STUDENT
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
