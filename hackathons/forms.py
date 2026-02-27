from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserProfile.Roles.choices,
        label="Роль",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    email = forms.EmailField(required=True, label="Email")
