from django.views.generic.base import TemplateView

from accounts.utils import cents_to_dollars


class TermsOfServiceView(TemplateView):
    template_name = "guppy/terms_of_service.html"


class PrivacyPolicyView(TemplateView):
    template_name = "guppy/privacy_policy.html"


class ReferralProgramView(TemplateView):
    template_name = "guppy/referral_program.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_profile = self.request.user
        # Pass referral link
        referral_link = self.request.user.get_refferal_link()
        reflink = self.request.build_absolute_uri(referral_link)

        context.update(
            {
                "reflink": reflink,
                "current_referral_payout": cents_to_dollars(
                    user_profile.current_referral_payout()
                ),
                "total_earnings_for_referrals": cents_to_dollars(
                    user_profile.total_earnings_for_referrals()
                ),
                "number_of_referrals": user_profile.number_of_referrals(),
                "number_of_activate_referrals": (
                    user_profile.number_of_activate_referrals()
                ),
            }
        )

        return context
