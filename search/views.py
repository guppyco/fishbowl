import urllib

from rest_framework import generics, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import redirect, render

from .forms import SearchForm
from .models import Result, Search
from .serializers import SimpleSearchSerializer


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
            "search_results": results,
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
            search_model.search_results.add(*result_ids)
            return Response(serializer.data)

        raise ValidationError(serializer.errors)

    def click(self, request):
        # TODO: add code for click tracking
        return self, request
