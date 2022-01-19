import factory

from advertisers.models import Ad, AdBrand, AdSize, Advertiser


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


class AdBrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AdBrand

    name = factory.Faker("name")
    url = "https://staging.guppy.co/"


class AdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ad

    brand = factory.SubFactory(AdBrandFactory)
    size = factory.SubFactory(AdSizeFactory)
    code = "ad_code"
