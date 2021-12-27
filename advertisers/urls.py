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
]
