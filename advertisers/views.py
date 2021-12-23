import logging

import stripe

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse

from advertisers.models import Advertiser

from .forms import AdvertiserCreationForm

LOGGER = logging.getLogger(__name__)


def signup(request):
    """
    Handle signup user
    """

    form = AdvertiserCreationForm()
    context = {
        "is_payment": False,
        "form": form,
    }
    template = "advertisers/signup.html"

    if request.method == "POST":
        # Change `ad_sizes` in to a list to pass the form validator
        post = request.POST.copy()  # to make it mutable
        ad_sizes = request.POST.get("ad_sizes")
        post["ad_sizes"] = [ad_sizes]
        request.POST = post

        advertiser_form = AdvertiserCreationForm(
            data=request.POST,
            ad_size=ad_sizes,
        )

        if advertiser_form.is_valid():
            stripe.api_key = settings.STRIPE_SECRET_KEY

            customer_data = {}
            if request.user.is_authenticated:
                customer_data = {"email": request.user.email}
                advertiser_form.user_profile = request.user
            customer = stripe.Customer.create(**customer_data)
            setup_intent = stripe.SetupIntent.create(
                customer=customer.id,
                payment_method_types=["card"],
            )

            advertiser_form.stripe_id = customer.id
            advertiser_form.save()
            advertiser_form.save_m2m()

            success_url = (
                request.build_absolute_uri(reverse("advertiser_signup_success"))
                + "?customer_id="
                + customer.id
            )
            context = {
                "is_payment": True,
                "client_secret": setup_intent.client_secret,
                "customer_id": customer.id,
                "success_url": success_url,
            }
        else:
            for _, errors in advertiser_form.errors.items():
                for error in errors:
                    messages.add_message(request, messages.ERROR, error)

    return render(request, template, context)


def signup_success(request):
    """
    Signup advertiser success page
    """

    text = "The advertiser is created successfully"
    customer_id = request.GET.get("customer_id", "")
    redirect_status = request.GET.get("redirect_status", "")
    if not customer_id or redirect_status != "succeeded":
        text = "Something went wrong!"
    else:
        try:
            advertiser = Advertiser.objects.get(stripe_id=customer_id)
            advertiser.is_valid_payment = True
            advertiser.save()
        except Advertiser.DoesNotExist:
            text = "The advertiser does not exist."

    template = "advertisers/signup_success.html"
    return render(request, template, {"text": text})
