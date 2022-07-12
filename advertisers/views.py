import logging

import stripe
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt

from advertisers.models import Advertiser
from advertisers.utils import get_ad_from_size, get_popup_ad

from .forms import AdvertisementCreationForm

LOGGER = logging.getLogger(__name__)


def index(request):
    """
    Advertiser landing page
    """

    email = ""
    if request.user.is_authenticated:
        email = request.user.email
    template = "advertisers/index.html"
    return render(request, template, {"email": email})


def signup(request):
    """
    Handle signup user
    """

    template = "advertisers/signup.html"
    email = request.POST.get("email", "")
    advertiser_id = request.POST.get("advertiser_id", "")
    if not email and not advertiser_id:
        return redirect("advertisers")
    if not advertiser_id:
        advertiser = Advertiser.objects.create(email=email)

        advertisement_form = AdvertisementCreationForm(
            initial={"advertiser_id": advertiser.pk}
        )
        context = {
            "is_payment": False,
            "form": advertisement_form,
        }
    else:
        advertiser_model = Advertiser.objects.get(pk=advertiser_id)
        advertisement_form = AdvertisementCreationForm(
            request.POST,
            request.FILES,
        )

        if advertisement_form.is_valid():
            advertisement = advertisement_form.save()
            stripe.api_key = settings.STRIPE_SECRET_KEY

            customer_data = {"email": request.POST.get("email")}
            if request.user.is_authenticated:
                advertisement_form.user_profile = request.user
            customer = stripe.Customer.create(**customer_data)
            setup_intent = stripe.SetupIntent.create(
                customer=customer.id,
                payment_method_types=["card"],
            )

            advertiser_model.advertisement = advertisement
            advertiser_model.stripe_id = customer.id
            if request.user.is_authenticated:
                advertiser_model.user_profile = request.user
            advertiser_model.save()

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
            advertisement_form = AdvertisementCreationForm(
                initial={"advertiser_id": advertiser_id}
            )
            context = {
                "is_payment": False,
                "form": advertisement_form,
            }
            for _, errors in advertisement_form.errors.items():
                for error in errors:
                    messages.add_message(request, messages.ERROR, error)

    return render(request, template, context)


def signup_success(request):
    """
    Signup advertiser success page
    """

    customer_id = request.GET.get("customer_id", "")
    redirect_status = request.GET.get("redirect_status", "")
    error_text = None
    if not customer_id or redirect_status != "succeeded":
        error_text = "Something went wrong!"
    else:
        try:
            advertiser = Advertiser.objects.get(stripe_id=customer_id)
            advertiser.is_valid_payment = True
            advertiser.save()
        except Advertiser.DoesNotExist:
            LOGGER.error(
                "Advertiser with stripe_id %s does not exist.", customer_id
            )
            error_text = (
                "Something went wrong - we'll be reaching out "
                "for more information, or please contact us at help@guppy.co."
            )

    template = "advertisers/signup_success.html"
    return render(request, template, {"error_text": error_text})


@xframe_options_exempt
def ads(request, width=0, height=0, brand="all"):
    """
    Show ads with size
    TODO: make the dynamic ads with multiple services!?
    """

    width = round(float(width))
    height = round(float(height))

    if not width or not height:
        return HttpResponseNotFound("Not found")

    ad_obj = get_ad_from_size(width, height, brand)
    if ad_obj:
        code = ad_obj.code
        # Update the view of this ad
        ad_obj.view = ad_obj.view + 1
        ad_obj.save()
    else:
        code = None
    template = "advertisers/ads.html"
    context = {
        "code": code,
        "width": width,
        "height": height,
    }
    return render(request, template, context)


def ads_checker(request, width=0, height=0):
    """
    Check if having an ad for size
    Return 200 if yes, 404 if no
    """

    width = round(float(width))
    height = round(float(height))
    if not width or not height:
        return HttpResponseNotFound("Not found")
    ad_obj = get_ad_from_size(width, height)
    if ad_obj:
        return HttpResponse("")
    return HttpResponseNotFound("Not found")


@api_view(("GET",))
@permission_classes([AllowAny])
@authentication_classes([BasicAuthentication])
def popup_ads(request):
    """
    Show popup ads code
    """

    popup_ad = get_popup_ad()

    if popup_ad:
        return Response(
            {
                "has_ads": True,
                "code": popup_ad.code,
            }
        )

    return Response({"has_ads": False})
