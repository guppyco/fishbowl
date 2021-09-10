# accounts/forms.py

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout

from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)

from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user with no privileges from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        del self.fields["password2"]
        self.fields["password1"].help_text = None
        # TODO: Update when django-crispy-forms gets updated.
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
        model = UserProfile
        fields = [
            "email",
            "password1",
            "first_name",
            "last_name",
            "address1",
            "address2",
            "city",
            "state",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        return email


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Your email"
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


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        del self.fields["username"]

    class Meta:
        model = UserProfile
        fields = ["email", "password"]
