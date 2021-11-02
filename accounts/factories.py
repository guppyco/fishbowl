import uuid

import factory
from django_reflinks.models import ReferralLink

from .models import UserProfile, UserProfileReferralHit


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

    identifier = uuid.uuid4().hex[:6]


class UserProfileReferralHitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfileReferralHit
