from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView

from .forms import SignUpForm
from .models import Hackathon, UserProfile


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


class SignUpView(TemplateView):
    template_name = "registration/signup.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response({"form": SignUpForm()})

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data["role"])
            login(request, user)
            return redirect("hackathons:dashboard")
        return self.render_to_response({"form": form})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "hackathons/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)
        context["profile"] = profile
        context["hackathons_count"] = Hackathon.objects.count()
        return context
