from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import ApplicationForm, HackathonForm, JoinTeamForm, SignUpForm, TeamForm
from .models import Application, Hackathon, ResultEntry, ScheduleItem, Team, UserProfile


def user_can_manage_hackathons(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and profile.role == UserProfile.Roles.ORGANIZER)


class OrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return user_can_manage_hackathons(self.request.user)


class HomeView(TemplateView):
    template_name = "hackathons/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_hackathons"] = user_can_manage_hackathons(self.request.user)
        context["latest_hackathons"] = Hackathon.objects.order_by("-created_at")[:5]
        context["latest_teams"] = Team.objects.select_related("hackathon").order_by("-created_at")[:5]
        return context


class HackathonListView(ListView):
    model = Hackathon
    template_name = "hackathons/hackathon_list.html"
    context_object_name = "hackathons"

    def get_queryset(self):
        queryset = Hackathon.objects.all()
        q = self.request.GET.get("q", "").strip()
        open_only = self.request.GET.get("open_only") == "1"

        if q:
            queryset = queryset.filter(title__icontains=q)
        if open_only:
            queryset = queryset.filter(is_open=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_hackathons"] = user_can_manage_hackathons(self.request.user)
        context["q"] = self.request.GET.get("q", "").strip()
        context["open_only"] = self.request.GET.get("open_only") == "1"
        return context


class HackathonDetailView(DetailView):
    model = Hackathon
    template_name = "hackathons/hackathon_detail.html"
    context_object_name = "hackathon"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["already_applied"] = False
        context["my_application"] = None
        if user.is_authenticated:
            my_app = Application.objects.filter(hackathon=self.object, user=user).first()
            context["already_applied"] = bool(my_app)
            context["my_application"] = my_app
        context["deadline_passed"] = self.object.is_deadline_passed()
        context["limit_reached"] = self.object.is_participants_limit_reached()
        context["approved_count"] = self.object.approved_applications_count()
        context["schedule_items"] = ScheduleItem.objects.filter(hackathon=self.object)
        context["result_entries"] = ResultEntry.objects.filter(hackathon=self.object)
        return context


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


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "hackathons/team_list.html"
    context_object_name = "teams"

    def get_queryset(self):
        return Team.objects.select_related("hackathon", "captain").prefetch_related("members")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["join_form"] = JoinTeamForm()
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "hackathons/team_form.html"
    success_url = reverse_lazy("hackathons:team-list")

    def dispatch(self, request, *args, **kwargs):
        if not Hackathon.objects.filter(is_open=True).exists():
            messages.error(request, "Пока нет открытых хакатонов. Сначала создайте или откройте хакатон.")
            return redirect("hackathons:hackathon-list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.captain = self.request.user
        response = super().form_valid(form)
        self.object.members.add(self.request.user)
        return response


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = "hackathons/team_confirm_delete.html"
    success_url = reverse_lazy("hackathons:team-list")

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Team.objects.all()
        return Team.objects.filter(captain=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Команда удалена.")
        return super().form_valid(form)


class JoinTeamView(LoginRequiredMixin, TemplateView):
    template_name = "hackathons/team_list.html"

    def post(self, request, *args, **kwargs):
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            invite_code = form.cleaned_data["invite_code"].upper()
            team = Team.objects.filter(invite_code=invite_code).first()
            if not team:
                messages.error(request, "Команда с таким кодом не найдена.")
            else:
                team.members.add(request.user)
                messages.success(request, f"Вы вступили в команду «{team.name}».")
        return redirect("hackathons:team-list")


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = "hackathons/application_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.hackathon = get_object_or_404(Hackathon, pk=self.kwargs["pk"])
        if not self.hackathon.is_open:
            messages.error(request, "Набор на этот хакатон закрыт.")
            return redirect("hackathons:hackathon-detail", pk=self.hackathon.pk)
        if self.hackathon.is_deadline_passed():
            messages.error(request, "Дедлайн подачи заявок уже прошёл.")
            return redirect("hackathons:hackathon-detail", pk=self.hackathon.pk)
        if self.hackathon.is_participants_limit_reached():
            messages.error(request, "Лимит участников уже достигнут.")
            return redirect("hackathons:hackathon-detail", pk=self.hackathon.pk)
        if Application.objects.filter(hackathon=self.hackathon, user=request.user).exists():
            messages.info(request, "Вы уже отправили заявку на этот хакатон.")
            return redirect("hackathons:hackathon-detail", pk=self.hackathon.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.hackathon = self.hackathon
        form.instance.user = self.request.user
        messages.success(self.request, "Заявка отправлена.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("hackathons:hackathon-detail", kwargs={"pk": self.hackathon.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hackathon"] = self.hackathon
        return context


class ApplicationListView(OrganizerRequiredMixin, ListView):
    model = Application
    template_name = "hackathons/application_list.html"
    context_object_name = "applications"

    def get_queryset(self):
        return Application.objects.select_related("user", "hackathon")


class ApplicationStatusUpdateView(OrganizerRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.kwargs["pk"])
        status = self.kwargs["status"]
        if status not in [Application.Status.APPROVED, Application.Status.REJECTED]:
            messages.error(request, "Некорректный статус.")
            return redirect("hackathons:application-list")
        application.status = status
        application.save(update_fields=["status"])
        messages.success(request, "Статус заявки обновлён.")
        return redirect("hackathons:application-list")


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
        context["teams_count"] = Team.objects.filter(members=self.request.user).count()
        context["applications_count"] = Application.objects.filter(user=self.request.user).count()
        context["can_manage_hackathons"] = user_can_manage_hackathons(self.request.user)
        context["is_admin_user"] = bool(self.request.user.is_staff or self.request.user.is_superuser)
        return context
