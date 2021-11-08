import factory
from factory.fuzzy import FuzzyDecimal

from .models import FAQ


class FAQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQ

    question = "This is test question"
    answer = "This is the test answer"
    order = FuzzyDecimal(low=0, high=100)
