from django.contrib.auth.backends import ModelBackend
from accounts.models import User


class RegisterNumberOrEmailBackend(ModelBackend):
    def authenticate(self, request, register_number=None, email=None, password=None, **kwargs):
        try:
            if register_number:
                user = User.objects.get(register_number=register_number)
            elif email:
                user = User.objects.get(email=email)
            else:
                return None
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
