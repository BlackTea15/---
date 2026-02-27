from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Hackathon, UserProfile


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserProfile.Roles.choices,
        label="Роль",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    email = forms.EmailField(required=True, label="Email")


class HackathonForm(forms.ModelForm):
    class Meta:
        model = Hackathon
        fields = ("title", "description", "start_date", "end_date", "location", "is_open")
        labels = {
            "title": "Название",
            "description": "Описание",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "location": "Локация",
            "is_open": "Открыт набор",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
