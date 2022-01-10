import factory

from advertisers.models import AdSize, Advertiser


class AdSizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AdSize

    width = factory.Faker("pyint", min_value=0, max_value=1000)
    height = factory.Faker("pyint", min_value=0, max_value=1000)


class AdvertiserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Advertiser

    ad_url = "https://staging.guppy.co/"
    budget = "1000"
