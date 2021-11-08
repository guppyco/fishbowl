import uuid

import factory
from django_reflinks.models import ReferralHit, ReferralLink

from .models import Payout, UserProfile, UserProfileReferralHit


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


class ReferralHitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReferralHit

    authenticated = False
    ip = factory.Faker("ipv4")


class UserProfileReferralHitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfileReferralHit


class PayoutFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payout

    amount = 1
