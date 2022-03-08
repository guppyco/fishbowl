from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout

from django import forms

from .models import ContactUs


class ContactUsCreationForm(forms.ModelForm):
    """
    A form that creates an ContactUs
    """

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop("user_profile", None)
        super().__init__(*args, **kwargs)
        self.fields["content"].widget = forms.Textarea()
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
        self.helper.form_tag = False
        self.helper.help_text = False

    class Meta:
        model = ContactUs
        fields = [
            "email",
            "content",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user_profile = self.user_profile
        if commit:
            instance.save()
        return instance
