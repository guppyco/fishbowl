from django.urls import path

from advertisers import views

urlpatterns = [
    path("", views.index, name="advertisers"),
    path("signup/", views.signup, name="advertiser_signup"),
    path(
        "signup/success/",
        views.signup_success,
        name="advertiser_signup_success",
    ),
    path("ads/<width>/<height>/", views.ads, name="ads_view"),
    path("ads/<width>/<height>/<brand>", views.ads, name="ads_brand_view"),
    path(
        "ads-checker/<width>/<height>/",
        views.ads_checker,
        name="ads_checker",
    ),
    path("ads/popup/", views.popup_ads, name="popup_ads_view"),
]
