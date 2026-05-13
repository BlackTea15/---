
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    ApplicationCreateView,
    ApplicationListView,
    ApplicationStatusUpdateView,
    DashboardView,
    HackathonCreateView,
    HackathonDeleteView,
    HackathonDetailView,
    HackathonListView,
    HackathonUpdateView,
    HomeView,
    JoinTeamView,
    JuryScoreUpdateView,
    ProjectSubmissionCreateView,
    SignUpView,
    TeamCreateView,
    TeamDeleteView,
    TeamListView,
)

from django.urls import path

from .views import HackathonDetailView, HackathonListView, HomeView


app_name = "hackathons"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("hackathons/", HackathonListView.as_view(), name="hackathon-list"),
codex/create-web-app-for-hackathon-automation-8v2i6vv
    path("hackathons/create/", HackathonCreateView.as_view(), name="hackathon-create"),
    path("hackathons/<int:pk>/", HackathonDetailView.as_view(), name="hackathon-detail"),
    path("hackathons/<int:pk>/edit/", HackathonUpdateView.as_view(), name="hackathon-edit"),
    path("hackathons/<int:pk>/delete/", HackathonDeleteView.as_view(), name="hackathon-delete"),
    path("hackathons/<int:pk>/apply/", ApplicationCreateView.as_view(), name="application-create"),
    path(
        "hackathons/<int:pk>/submit-project/",
        ProjectSubmissionCreateView.as_view(),
        name="project-submit",
    ),
    path("submissions/<int:pk>/score/", JuryScoreUpdateView.as_view(), name="submission-score"),
    path("applications/", ApplicationListView.as_view(), name="application-list"),
    path(
        "applications/<int:pk>/<str:status>/",
        ApplicationStatusUpdateView.as_view(),
        name="application-status",
    ),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path("teams/<int:pk>/delete/", TeamDeleteView.as_view(), name="team-delete"),
    path("teams/join/", JoinTeamView.as_view(), name="team-join"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("hackathons/<int:pk>/", HackathonDetailView.as_view(), name="hackathon-detail"),
]
