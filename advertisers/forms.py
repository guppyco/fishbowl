from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout

from django import forms

from .models import Advertisement, Advertiser


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

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop("user_profile", None)
        super().__init__(*args, **kwargs)
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

    class Meta:
        model = Advertiser
        fields = [
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
        return instance


class AdvertisementCreationForm(forms.ModelForm):
    """
    A form that creates an advertisement
    and advertiser_id and monthly_budget to create Advertiser
    """

    advertiser_id = forms.IntegerField()
    monthly_budget = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["advertiser_id"].widget = forms.HiddenInput()
        self.fields["url"].label = "Ad URL"
        self.fields["monthly_budget"].label = "Monthly budget (US $)"
        self.fields[
            "image"
        ].help_text = "<i>* Must be .png, .jpg, .jpeg, .gif</i>"
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

    class Meta:
        model = Advertisement
        fields = [
            "url",
            "image",
        ]
