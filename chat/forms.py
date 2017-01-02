from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.HiddenInput()

