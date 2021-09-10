from django.conf.urls import url

from .views import FAQListView

app_name = "faqs"
urlpatterns = [url(r"^", FAQListView.as_view(), name="faqs-list")]
