from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout

from django import forms

from .models import AdSize, Advertiser


class M2MSelect(forms.Select):
    """
    Override `value_from_datadict` to view m2m field as single-select
    """

    def value_from_datadict(self, data, files, name):
        return data.get(name, None)


class AdvertiserCreationForm(forms.ModelForm):
    """
    A form that creates an advertiser with credit card info
    """

    # Only select one ad size
    ad_sizes = forms.ModelMultipleChoiceField(
        widget=M2MSelect,
        required=True,
        queryset=AdSize.objects.filter(is_enabled=True),
    )

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop("user_profile", None)
        self.ad_size = kwargs.pop("ad_size", None)
        super().__init__(*args, **kwargs)
        self.fields["ad_url"].label = "Ad URL"
        self.fields["monthly_budget"].label = "Monthly budget (US $)"
        self.helper = FormHelper(self)
        self.helper.layout = Layout()
        for field_name, field in list(self.fields.items()):
            self.helper.layout.append(
                Div(
                    Field(
                        field_name,
                        placeholder=field.label,
                        css_class="form-control",
                    ),
                    css_class="form-group mb-3",
                )
            )
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.help_text = False

    class Meta:
        model = Advertiser
        fields = [
            "ad_url",
            "ad_sizes",
            "monthly_budget",
        ]

    def clean_monthly_budget(self):
        """
        Convert monthly bedgut from dollar to cent
        """
        monthly_budget = self.cleaned_data["monthly_budget"] * 100
        return monthly_budget

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user_profile = self.user_profile
        instance.stripe_id = self.stripe_id
        if commit:
            instance.save()
            instance.ad_sizes.add(self.ad_size)
        return instance
