# accounts/views.py

import json
import logging
import urllib

from django_reflinks.models import ReferralHit
from honeypot.decorators import check_honeypot
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView

from .forms import (
    CustomAuthenticationForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
)
from .models import Payout, UserProfile, UserProfileReferralHit
from .utils import cents_to_dollars

LOGGER = logging.getLogger(__name__)


@check_honeypot
def signup_user(request):
    """
    Handle signup user
    """
    if request.user.is_authenticated:
        return redirect_user(request)

    signup_form = CustomUserCreationForm(prefix="signup")
    if request.method == "POST":
        signup_form = CustomUserCreationForm(data=request.POST, prefix="signup")
        if signup_form.is_valid():
            account = signup_form.save()

            number_of_allowed_users = UserProfile.objects.filter(
                is_waitlisted=False
            ).count()
            if number_of_allowed_users < UserProfile.NUMBER_OF_ALLOWED_USERS:
                account.is_waitlisted = False
                account.save()

            email = account.email
            password = signup_form.cleaned_data["password1"]
            user = authenticate(username=email, password=password)
            if user is not None and user.is_active:
                login(request, user)
                request.session["first_signup"] = True
                return redirect("signup_success")
            #  TODO: MAKE SURE ERROR RETURNS PROPERLY
            messages.error(request, "This account is not valid")

    context = {
        "signup_form": signup_form,
        "hero_image": True,
        "next": get_next_str(request),
    }
    template = "accounts/signup.html"

    return render(request, template, context)


def signup_user_success(request):
    """
    Handle signup user
    """
    if not request.user.is_authenticated:
        return redirect("login")

    context = {"browser_family": request.user_agent.browser.family}
    template = "accounts/signup_success.html"

    # Pass first_signup variable to tell Google Analytics
    # if this signup should be counted as a conversion.
    if hasattr(request, "session"):
        first_signup = request.session.pop("first_signup", False)
        if first_signup:
            context["first_signup"] = True
            # Add refferal to reffered account
            try:
                referral_hit = ReferralHit.objects.filter(
                    hit_user_id=request.user.pk
                ).latest("created")
            except ReferralHit.DoesNotExist:
                referral_hit = None
            if referral_hit is not None:
                referred_user = referral_hit.referral_link.user
                UserProfileReferralHit.objects.create(
                    referral_hit=referral_hit,
                    user_profile=referred_user,
                )
                referral_hit.confirmed = timezone.now()
                referral_hit.save()

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


@api_view(("POST",))
@csrf_exempt
@permission_classes([AllowAny])
@authentication_classes([BasicAuthentication])
def api_login_user(request):
    if request.POST:
        data = request.POST
    else:
        data = request.data
    login_form = CustomAuthenticationForm(data=data)
    if login_form.is_valid():
        username = data["username"]
        password = data["password"]
        member = authenticate(username=username, password=password)
        if member is not None and member.is_active:
            login(request, member)
            csrf_token = get_token(request)
            return Response(
                {
                    "error": False,
                    "csrf_token": csrf_token,
                }
            )

    return Response(
        {
            "error": True,
            "message": "This account is not valid",
        }
    )


@login_required
def profile_edit(request):
    if request.method == "POST":
        profile_form = CustomUserChangeForm(
            request.POST, request.FILES, instance=request.user
        )

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile is updated successfully")
            return redirect("user_profile")
    else:
        profile_form = CustomUserChangeForm(instance=request.user)

    return render(
        request,
        "accounts/userprofile_form.html",
        {"profile_form": profile_form},
    )


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
    """
    The view for user profile (web)
    """

    template_name = "accounts/profile.html"
    model = UserProfile

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """
        Custom get method
        """
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        paid_amount = self.object.get_earned_amount(Payout.PAID)
        requesting_amount = self.object.get_earned_amount(Payout.REQUESTING)
        unpaid_amount = self.object.get_earned_amount(Payout.UNPAID)
        context["profile"] = {
            "paid_amount": paid_amount,
            "paid_amount_text": cents_to_dollars(paid_amount),
            "requesting_amount": requesting_amount,
            "requesting_amount_text": cents_to_dollars(requesting_amount),
            "unpaid_amount": unpaid_amount,
            "unpaid_amount_text": cents_to_dollars(unpaid_amount),
        }
        # Pass referral link
        referral_link = request.user.get_refferal_link()
        context["reflink"] = request.build_absolute_uri(referral_link)

        # Pass first_signup variable to tell Google Analytics
        # if this signup should be counted as a conversion.
        if hasattr(self.request, "session"):
            first_signup = self.request.session.pop("first_signup", False)
            if first_signup:
                context["first_signup"] = True
                # Add refferal to reffered account
                try:
                    referral_hit = ReferralHit.objects.filter(
                        hit_user_id=request.user.pk
                    ).latest("created")
                except ReferralHit.DoesNotExist:
                    referral_hit = None
                if referral_hit is not None:
                    referred_user = referral_hit.referral_link.user
                    UserProfileReferralHit.objects.create(
                        referral_hit=referral_hit,
                        user_profile=referred_user,
                    )
                    referral_hit.confirmed = timezone.now()
                    referral_hit.save()

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserProfileAPIView(APIView):
    """
    The view for user profile API
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Custome get method
        """
        try:
            user = request.user
            profile = UserProfile.objects.get(email=user)
            paid_amount = profile.get_earned_amount(Payout.PAID)
            requesting_amount = profile.get_earned_amount(Payout.REQUESTING)
            unpaid_amount = profile.get_earned_amount(Payout.UNPAID)
            content = {
                "user": str(request.user),
                "auth": str(request.auth),
                "profile": {
                    "full_name": profile.get_full_name(),
                    "address": profile.get_address(),
                    "status": profile.get_status(),
                    "is_waitlisted": profile.is_waitlisted,
                    "last_time": profile.get_last_posting_time(),
                    "paid_amount": paid_amount,
                    "paid_amount_text": cents_to_dollars(paid_amount),
                    "requesting_amount": requesting_amount,
                    "requesting_amount_text": cents_to_dollars(
                        requesting_amount
                    ),
                    "unpaid_amount": unpaid_amount,
                    "unpaid_amount_text": cents_to_dollars(unpaid_amount),
                    "reflink": False,
                },
            }
            referral_link = request.user.get_refferal_link()
            content["profile"]["reflink"] = request.build_absolute_uri(
                referral_link
            )

            return Response(content)
        except UserProfile.DoesNotExist as exc:
            LOGGER.exception(exc)
            return Response(status=status.HTTP_404_NOT_FOUND)


class PayoutAPIView(ViewSet):
    """
    Handle payout requests
    """

    permission_classes = [IsAuthenticated]

    def request_payout(self, request):  # pylint: disable=no-self-use
        """
        Process a payout request
        """
        user = request.user
        profile = UserProfile.objects.get(email=user)

        requesting_amount = profile.get_earned_amount(Payout.REQUESTING)
        if requesting_amount:
            return Response(
                {"message": "You cannot request more than one payout"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        unpaid_payouts = profile.get_earned_amount(
            status=Payout.UNPAID,
            return_objects=True,
        )

        if unpaid_payouts["amount"] < 1000:
            return Response(
                {"message": "Minimum Guppy payout is $10"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Create payout request
        payout_ids = unpaid_payouts["objects"].values_list("pk", flat=True)
        user.payout_requests.create(
            amount=unpaid_payouts["amount"],
            payout_ids=json.dumps(list(payout_ids)),
        )
        # Update requesting payouts
        unpaid_payouts["objects"].update(payment_status=Payout.REQUESTING)

        return Response({}, status=status.HTTP_201_CREATED)
