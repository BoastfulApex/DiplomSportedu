from django import forms
from .models import *
from apps.superadmin.models import *

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Foydalanuvchi nomi",
                "class": "form-control form-control-lg"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Parol",
                "class": "form-control form-control-lg"
            }
        ))
