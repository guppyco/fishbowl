import factory

from .models import UserProfile


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "test")
