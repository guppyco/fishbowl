import urllib

from django.conf import settings
from django.shortcuts import redirect, render

from .forms import SearchForm


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
