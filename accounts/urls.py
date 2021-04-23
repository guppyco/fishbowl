from django.urls import include, path

from accounts import views

urlpatterns = [
    path("signup/", views.signup_user, name="signup"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("account/", views.UserProfileView.as_view(), name="user_profile"),
    path("", include("django.contrib.auth.urls")),
]
