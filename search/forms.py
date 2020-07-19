"""
Forms for the Guppy search page.
"""
from django import forms


class SearchForm(forms.Form):
    """
    Form for the home page search function.
    """
    search = forms.CharField(label="Search", max_length=100)
