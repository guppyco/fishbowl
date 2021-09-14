from django.views.generic.base import TemplateView


class TermsOfServiceView(TemplateView):
    template_name = "guppy/terms_of_service.html"


class PrivacyPolicyView(TemplateView):
    template_name = "guppy/privacy_policy.html"
