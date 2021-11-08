import uuid

from django_reflinks.models import ReferralLink

from django.views.generic.base import TemplateView


class TermsOfServiceView(TemplateView):
    template_name = "guppy/terms_of_service.html"


class PrivacyPolicyView(TemplateView):
    template_name = "guppy/privacy_policy.html"


class ReferralProgramView(TemplateView):
    template_name = "guppy/referral_program.html"

    def get_context_data(self, **kwargs):
        # TODO: pass referral info to the view
        context = super().get_context_data(**kwargs)
        # Pass referral link
        referral_link, created = ReferralLink.objects.get_or_create(
            user_id=self.request.user.pk,
        )
        if created:
            referral_link.identifier = uuid.uuid4().hex[:6]
            referral_link.save()
        reflink = self.request.build_absolute_uri(referral_link)
        context.update({"reflink": reflink})

        return context
