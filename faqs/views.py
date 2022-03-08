from django.contrib import messages
from django.shortcuts import render
from django.views.generic.list import ListView

from .forms import ContactUsCreationForm
from .models import FAQ


class FAQListView(ListView):
    queryset = FAQ.objects.all()


def contact_us(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form = ContactUsCreationForm(
                request.POST, request.FILES, user_profile=request.user
            )
        else:
            form = ContactUsCreationForm(
                request.POST,
                request.FILES,
            )

        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent!")
            form = ContactUsCreationForm()
    else:
        form = ContactUsCreationForm()

    return render(
        request,
        "faqs/contact-us.html",
        {"form": form},
    )
