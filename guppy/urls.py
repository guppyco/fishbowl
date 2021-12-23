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
from django.contrib import admin
from django.urls import include, path

from guppy import views

urlpatterns = [  # pylint: disable=invalid-name
    path("admin/", admin.site.urls),
    path("", include("search.urls", namespace="search")),
    path("", include("accounts.urls")),
    path("advertisers/", include("advertisers.urls")),
    path("faqs/", include("faqs.urls", namespace="faqs")),
    path(
        "terms-of-service/",
        views.TermsOfServiceView.as_view(),
        name="terms-of-service",
    ),
    path(
        "privacy-policy/",
        views.PrivacyPolicyView.as_view(),
        name="privacy-policy",
    ),
    path(
        "referral-program/",
        views.ReferralProgramView.as_view(),
        name="referral-program",
    ),
    path(
        "about/",
        views.AboutView.as_view(),
        name="about",
    ),
    path("ref/", include("django_reflinks.urls")),
]
