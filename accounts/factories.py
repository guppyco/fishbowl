import factory
from django_reflinks.models import ReferralLink

from .models import UserProfile


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    first_name = factory.Faker("name")
    last_name = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "test")


class ReferralLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReferralLink

    identifier = "test"
