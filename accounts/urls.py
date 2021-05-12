from rest_framework_jwt.blacklist.views import BlacklistView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from django.urls import include, path

from accounts import views

urlpatterns = [
    path("signup/", views.signup_user, name="signup"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("account/", views.UserProfileView.as_view(), name="user_profile"),
    path("api/token-auth/", obtain_jwt_token, name="token_obtain_pair"),
    path("api/token-refresh/", refresh_jwt_token, name="token_refresh"),
    path(
        "api/token-destroy/",
        BlacklistView.as_view({"post": "create"}),
        name="token_destroy",
    ),
    path(
        "api/account/",
        views.UserProfileAPIView.as_view(),
        name="user_profile_api",
    ),
    path("", include("django.contrib.auth.urls")),
]
