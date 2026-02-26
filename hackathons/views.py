from django.views.generic import DetailView, ListView, TemplateView

from .models import Hackathon


class HomeView(TemplateView):
    template_name = "hackathons/home.html"


class HackathonListView(ListView):
    model = Hackathon
    template_name = "hackathons/hackathon_list.html"
    context_object_name = "hackathons"


class HackathonDetailView(DetailView):
    model = Hackathon
    template_name = "hackathons/hackathon_detail.html"
    context_object_name = "hackathon"
