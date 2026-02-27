from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    DashboardView,
    HackathonCreateView,
    HackathonDeleteView,
    HackathonDetailView,
    HackathonListView,
    HackathonUpdateView,
    HomeView,
    SignUpView,
)

app_name = "hackathons"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("hackathons/", HackathonListView.as_view(), name="hackathon-list"),
    path("hackathons/create/", HackathonCreateView.as_view(), name="hackathon-create"),
    path("hackathons/<int:pk>/", HackathonDetailView.as_view(), name="hackathon-detail"),
    path("hackathons/<int:pk>/edit/", HackathonUpdateView.as_view(), name="hackathon-edit"),
    path("hackathons/<int:pk>/delete/", HackathonDeleteView.as_view(), name="hackathon-delete"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
