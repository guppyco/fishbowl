import urllib

from rest_framework import generics, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import redirect, render

from .forms import SearchForm
from .models import History, Result, Search
from .serializers import HistorySerialzer, SimpleSearchSerializer
from .utils import click_url


def home(request):
    """
    Main search home page for Guppy.
    """
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search_string = urllib.parse.quote_plus(form.cleaned_data["search"])
            search_path = f"/search?q={search_string}"
            if "search-guppy" in request.POST:
                return redirect(f"{settings.BASE_URL}{search_path}")
            if "search-google" in request.POST:
                return redirect(f"http://www.google.com{search_path}")
    else:
        form = SearchForm()
    template = "search/home.html"
    context = {"form": form}
    return render(request, template, context)


def search(request):
    template = "search/search.html"
    context = {"q": request.GET["q"]}
    return render(request, template, context)


class SearchView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = SimpleSearchSerializer
    permission_classes = [AllowAny]
    queryset = Search.objects.all()

    def post(self, request):
        results = []
        # TODO: parse results from HTML content?
        if "search_results" in request.data:
            results = request.data.getlist("search_results")

        user_id = request.user.pk
        if user_id is None:
            user_id = 0
        data = {
            "user_id": user_id,
            "results": results,
        }
        if "search_terms" in request.data:
            data["search_terms"] = request.data["search_terms"]
        if "search_type" in request.data:
            data["search_type"] = request.data["search_type"]
        serializer = self.serializer_class(
            data=data,
        )
        if serializer.is_valid(raise_exception=True):
            searchs = Search.objects.filter(
                search_type=data["search_type"],
                search_terms=data["search_terms"],
                user_id=user_id,
            )
            if searchs.count():
                search = searchs.first()
                serializer = self.serializer_class(
                    search,
                    data=data,
                )
                serializer.is_valid(raise_exception=True)
            serializer.save()
            result_ids = []
            for result in results:
                model, _ = Result.objects.get_or_create(url=result)
                result_ids.append(model.pk)
            search_model = Search.objects.get(pk=serializer.data["id"])
            search_model.results.add(*result_ids)
            return Response(serializer.data, status.HTTP_201_CREATED)

        raise ValidationError(serializer.errors)


class HistoryCreateView(CreateAPIView):
    serializer_class = HistorySerialzer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = {}
        for key, item in request.data.items():
            if item.strip():
                data[key] = item
        user_id = request.user.pk
        if user_id is None:
            user_id = 0
        data["user_id"] = user_id
        serializer = self.serializer_class(
            data=data,
        )

        if serializer.is_valid(raise_exception=True):
            histories = History.objects.filter(
                url=data["url"],
                user_id=user_id,
            )
            if histories.count():
                history = histories.first()
                data["count"] = history.count + 1
                serializer = self.serializer_class(
                    history,
                    data=data,
                )
                serializer.is_valid(raise_exception=True)
            serializer.save()
            # Track clicked URL
            click_url(data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        raise ValidationError(serializer.errors)
