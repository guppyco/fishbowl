import factory

from .models import History, Search


class SearchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Search

    search_terms = factory.Faker("name")


class HistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = History

    url = factory.Faker("url")
