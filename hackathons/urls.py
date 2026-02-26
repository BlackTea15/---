from django.urls import path

from .views import HackathonDetailView, HackathonListView, HomeView

app_name = "hackathons"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("hackathons/", HackathonListView.as_view(), name="hackathon-list"),
    path("hackathons/<int:pk>/", HackathonDetailView.as_view(), name="hackathon-detail"),
]
