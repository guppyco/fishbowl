"""guppy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views

app_name = "search"  # pylint: disable=invalid-name
urlpatterns = [  # pylint: disable=invalid-name
    path("", views.home, name="home"),
    path("api/search/", views.SearchView.as_view(), name="api_search"),
    path(
        "api/search/click",
        views.SearchView.click,
        name="api_search_click",
    ),
]
