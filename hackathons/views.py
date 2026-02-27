from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import HackathonForm, SignUpForm
from .models import Hackathon, UserProfile


class OrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        profile = getattr(self.request.user, "profile", None)
        return bool(profile and profile.role == UserProfile.Roles.ORGANIZER)


class HomeView(TemplateView):
    template_name = "hackathons/home.html"


class HackathonListView(ListView):
    model = Hackathon
    template_name = "hackathons/hackathon_list.html"
    context_object_name = "hackathons"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)
        context["can_manage_hackathons"] = bool(
            self.request.user.is_authenticated
            and profile
            and profile.role == UserProfile.Roles.ORGANIZER
        )
        return context


class HackathonDetailView(DetailView):
    model = Hackathon
    template_name = "hackathons/hackathon_detail.html"
    context_object_name = "hackathon"


class HackathonCreateView(OrganizerRequiredMixin, CreateView):
    model = Hackathon
    form_class = HackathonForm
    template_name = "hackathons/hackathon_form.html"
    success_url = reverse_lazy("hackathons:hackathon-list")


class HackathonUpdateView(OrganizerRequiredMixin, UpdateView):
    model = Hackathon
    form_class = HackathonForm
    template_name = "hackathons/hackathon_form.html"
    success_url = reverse_lazy("hackathons:hackathon-list")


class HackathonDeleteView(OrganizerRequiredMixin, DeleteView):
    model = Hackathon
    template_name = "hackathons/hackathon_confirm_delete.html"
    success_url = reverse_lazy("hackathons:hackathon-list")


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
        context["can_manage_hackathons"] = bool(
            profile and profile.role == UserProfile.Roles.ORGANIZER
        )
        return context
