from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    class Meta:
        model =User
        fields=[
            'first_name','last_name','username','email','password1','password2',
        ]

class LocationForm(forms.Form):
    city = forms.CharField(label='City', max_length=100)
    state = forms.CharField(label='State', max_length=100, required=False)
    country = forms.CharField(label='Country', max_length=100)
