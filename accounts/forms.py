from django import forms
from django.contrib.auth.models import User


class UserProfileForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=255)
    last_name = forms.CharField(label="Last Name", max_length=255)
    email = forms.EmailField(label="Email", disabled=True, required=False)
    get_prop_bet_emails = forms.BooleanField(required=False)
    get_accepted_bet_emails = forms.BooleanField(required=False)
