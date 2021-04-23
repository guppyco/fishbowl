from django.contrib.auth import authenticate

from .models import UserProfile


def setup_tests(client):
    user = UserProfile.objects.create_user("anna@guppy.co", "test")
    client.user = authenticate(username=user.email, password="test")
    client.login(username=user.email, password="test")
    return user


def setup_tests_admin(client):
    user = UserProfile.objects.create_user("anna_admin@guppy.co", "test")
    user.is_staff = True
    user.save()
    client.user = authenticate(username=user.email, password="test")
    client.login(username=user.email, password="test")
    UserProfile.objects.create_user("ian@guppy.co", "test")
    return user
