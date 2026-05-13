from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Application, Hackathon, JuryScore, ProjectSubmission, Team, UserProfile


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
        fields = (
            "title",
            "description",
            "start_date",
            "end_date",
            "application_deadline",
            "max_participants",
            "location",
            "is_open",
        )
        labels = {
            "title": "Название",
            "description": "Описание",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "application_deadline": "Дедлайн заявок",
            "max_participants": "Лимит одобренных участников",
            "location": "Локация",
            "is_open": "Открыт набор",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "application_deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["start_date", "end_date", "application_deadline"]:
            self.fields[field_name].input_formats = ["%Y-%m-%d", "%d.%m.%Y"]


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("name", "hackathon")
        labels = {
            "name": "Название команды",
            "hackathon": "Хакатон",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hackathon"].queryset = Hackathon.objects.filter(is_open=True)


class JoinTeamForm(forms.Form):
    invite_code = forms.CharField(max_length=10, label="Код приглашения")


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("motivation",)
        labels = {"motivation": "Комментарий к заявке"}
        widgets = {
            "motivation": forms.Textarea(attrs={"rows": 4, "placeholder": "Коротко опишите вашу идею"}),
        }


class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = ("title", "description", "repo_url", "demo_url")
        labels = {
            "title": "Название проекта",
            "description": "Описание",
            "repo_url": "Ссылка на репозиторий",
            "demo_url": "Ссылка на демо",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Коротко опишите решение"}),
        }


class JuryScoreForm(forms.ModelForm):
    class Meta:
        model = JuryScore
        fields = ("score", "comment")
        labels = {
            "score": "Оценка (1-10)",
            "comment": "Комментарий жюри",
        }
        widgets = {
            "score": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
