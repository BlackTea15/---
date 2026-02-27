from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    DashboardView,
    HackathonDetailView,
    HackathonListView,
    HomeView,
    SignUpView,
)

app_name = "hackathons"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("hackathons/", HackathonListView.as_view(), name="hackathon-list"),
    path("hackathons/<int:pk>/", HackathonDetailView.as_view(), name="hackathon-detail"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
