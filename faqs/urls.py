from django.conf.urls import url
from django.urls import path

from faqs import views

app_name = "faqs"
urlpatterns = [
    url("faqs/", views.FAQListView.as_view(), name="faqs-list"),
    path("contact-us/", views.contact_us, name="contact-us"),
]
