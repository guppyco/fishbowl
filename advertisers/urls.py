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
    path("ads/<int:width>/<int:height>/", views.ads, name="ads_view"),
    path(
        "ads-checker/<int:width>/<int:height>/",
        views.ads_checker,
        name="ads_checker",
    ),
    path("ads/popup/", views.popup_ads, name="popup_ads_view"),
]
