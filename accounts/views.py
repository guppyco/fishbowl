# accounts/views.py

import logging
import urllib

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import UserProfile

LOGGER = logging.getLogger(__name__)


def signup_user(request):
    if request.user.is_authenticated:
        return redirect_user(request)

    signup_form = CustomUserCreationForm(prefix="signup")
    if request.method == "POST":
        signup_form = CustomUserCreationForm(data=request.POST, prefix="signup")
        if signup_form.is_valid():
            account = signup_form.save()
            email = account.email
            password = signup_form.cleaned_data["password1"]
            user = authenticate(username=email, password=password)
            if user is not None and user.is_active:
                login(request, user)
                if not settings.DEBUG:
                    request.session["first_signup"] = True
                return redirect_user(request)
            #  TODO: MAKE SURE ERROR RETURNS PROPERLY
            messages.error(request, "This account is not valid")

    context = {
        "signup_form": signup_form,
        "hero_image": True,
        "next": get_next_str(request),
    }
    template = "accounts/signup.html"

    return render(request, template, context)


def login_user(request):
    if request.user.is_authenticated:
        return redirect_user(request)

    login_form = CustomAuthenticationForm(prefix="login")
    if request.method == "POST":
        login_form = CustomAuthenticationForm(data=request.POST, prefix="login")
        if login_form.is_valid():
            email = request.POST["login-username"]
            password = request.POST["login-password"]
            member = authenticate(username=email, password=password)
            if member is not None and member.is_active:
                login(request, member)
                return redirect_user(request)

        else:
            #  TODO: Make sure error returns properly.
            messages.error(request, "This account is not valid")

    context = {
        "login_form": login_form,
        "hero_image": True,
        "next": get_next_str(request),
    }

    template = "accounts/login.html"

    return render(request, template, context)


def logout_user(request):
    logout(request)
    return redirect("login")


def redirect_user(request):
    next_str = request.GET.get("next", "") or "user_profile"

    return redirect(next_str)


def get_next_str(request):
    if request.GET.get("next", ""):
        return "?next=" + urllib.parse.quote(request.GET.get("next", ""))
    return ""


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = "accounts/profile.html"
    model = UserProfile

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # Pass first_signup or premium variable to tell Google Analytics
        # if this signup/premium should be counted as a conversion.
        if hasattr(self.request, "session"):
            first_signup = self.request.session.pop("first_signup", False)
            if first_signup:
                context["first_signup"] = True

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserProfileUpdate(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ["name", "email", "password"]
    success_url = ""

    def get_object(self, queryset=None):
        return self.request.user


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            "user": str(request.user),
            "auth": str(request.auth),
        }

        return Response(content)
