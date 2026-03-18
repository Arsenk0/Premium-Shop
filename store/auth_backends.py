from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            # Allow login with either username or email
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Multiple users found — check password for each one
            users = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).order_by('id')
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
