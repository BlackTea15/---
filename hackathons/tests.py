
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.db import OperationalError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Application,
    Hackathon,
    JuryScore,
    ProjectSubmission,
    ResultEntry,
    ScheduleItem,
    Team,
    UserProfile,
)


class HackathonPagesTests(TestCase):
    def setUp(self) -> None:
        self.hackathon = Hackathon.objects.create(
            title="AI Hack Moscow",
            description="48-часовой хакатон по AI-решениям для города.",
            start_date="2026-04-10",
            end_date="2026-04-12",
            location="Москва",
            is_open=True,
        )

    def test_home_page_is_available(self):
        response = self.client.get(reverse("hackathons:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "организации хакатонов")
        self.assertContains(response, "Новости")

    def test_list_page_shows_hackathon(self):
        response = self.client.get(reverse("hackathons:hackathon-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hackathon.title)

    def test_detail_page_shows_single_hackathon(self):
        response = self.client.get(
            reverse("hackathons:hackathon-detail", kwargs={"pk": self.hackathon.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hackathon.description)



class AuthAndRolesTests(TestCase):
    def test_signup_creates_profile_with_role_and_logs_in(self):
        response = self.client.post(
            reverse("hackathons:signup"),
            {
                "username": "anna",
                "email": "anna@example.com",
                "role": UserProfile.Roles.ORGANIZER,
                "password1": "StrongPass12345",
                "password2": "StrongPass12345",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="anna")
        self.assertEqual(user.profile.role, UserProfile.Roles.ORGANIZER)
        self.assertContains(response, "Личный кабинет")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("hackathons:dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("hackathons:login"), response.url)

    def test_login_redirects_to_dashboard(self):
        user = User.objects.create_user(username="tom", password="pass12345")
        UserProfile.objects.create(user=user, role=UserProfile.Roles.PARTICIPANT)

        response = self.client.post(
            reverse("hackathons:login"),
            {"username": "tom", "password": "pass12345"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Личный кабинет")


class HackathonCrudTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="org", password="pass12345")
        UserProfile.objects.create(user=self.organizer, role=UserProfile.Roles.ORGANIZER)

        self.participant = User.objects.create_user(username="part", password="pass12345")
        UserProfile.objects.create(user=self.participant, role=UserProfile.Roles.PARTICIPANT)

        self.hackathon = Hackathon.objects.create(
            title="Initial",
            description="Desc",
            start_date="2026-05-01",
            end_date="2026-05-02",
            location="Online",
            is_open=True,
        )

    def test_organizer_can_create_hackathon(self):
        self.client.login(username="org", password="pass12345")

        response = self.client.post(
            reverse("hackathons:hackathon-create"),
            {
                "title": "New Hack",
                "description": "New Desc",
                "start_date": "2026-06-10",
                "end_date": "2026-06-11",
                "application_deadline": "2026-06-09",
                "max_participants": 10,
                "location": "SPB",
                "is_open": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Hackathon.objects.filter(title="New Hack").exists())

    def test_participant_cannot_create_hackathon(self):
        self.client.login(username="part", password="pass12345")

        response = self.client.get(reverse("hackathons:hackathon-create"))

        self.assertEqual(response.status_code, 403)


    def test_superuser_can_open_hackathon_create(self):
        admin = User.objects.create_superuser(
            username="root", email="root@example.com", password="pass12345"
        )
        self.client.login(username="root", password="pass12345")

        response = self.client.get(reverse("hackathons:hackathon-create"))

        self.assertEqual(response.status_code, 200)

    def test_organizer_can_edit_hackathon(self):
        self.client.login(username="org", password="pass12345")

        response = self.client.post(
            reverse("hackathons:hackathon-edit", kwargs={"pk": self.hackathon.pk}),
            {
                "title": "Updated",
                "description": "Updated Desc",
                "start_date": "2026-05-01",
                "end_date": "2026-05-03",
                "application_deadline": "2026-04-29",
                "max_participants": 20,
                "location": "Moscow",
                "is_open": False,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.hackathon.refresh_from_db()
        self.assertEqual(self.hackathon.title, "Updated")

    def test_organizer_can_delete_hackathon(self):
        self.client.login(username="org", password="pass12345")

        response = self.client.post(
            reverse("hackathons:hackathon-delete", kwargs={"pk": self.hackathon.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Hackathon.objects.filter(pk=self.hackathon.pk).exists())

    def test_organizer_can_edit_hackathon_with_russian_date_format(self):
        self.client.login(username="org", password="pass12345")

        response = self.client.post(
            reverse("hackathons:hackathon-edit", kwargs={"pk": self.hackathon.pk}),
            {
                "title": "Date Format Updated",
                "description": "Updated Desc",
                "start_date": "15.05.2026",
                "end_date": "16.05.2026",
                "application_deadline": "14.05.2026",
                "max_participants": 50,
                "location": "Kazan",
                "is_open": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.hackathon.refresh_from_db()
        self.assertEqual(str(self.hackathon.start_date), "2026-05-15")
        self.assertEqual(str(self.hackathon.end_date), "2026-05-16")


class TeamFlowTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="pass12345")
        UserProfile.objects.create(user=self.user1, role=UserProfile.Roles.PARTICIPANT)

        self.user2 = User.objects.create_user(username="u2", password="pass12345")
        UserProfile.objects.create(user=self.user2, role=UserProfile.Roles.PARTICIPANT)

        self.hackathon = Hackathon.objects.create(
            title="Team Hack",
            description="Desc",
            start_date="2026-07-01",
            end_date="2026-07-02",
            location="Online",
            is_open=True,
        )

    def test_login_required_for_team_pages(self):
        response = self.client.get(reverse("hackathons:team-list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("hackathons:login"), response.url)

    def test_user_can_create_team(self):
        self.client.login(username="u1", password="pass12345")

        response = self.client.post(
            reverse("hackathons:team-create"),
            {
                "name": "Alpha",
                "hackathon": self.hackathon.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        team = Team.objects.get(name="Alpha")
        self.assertEqual(team.captain, self.user1)
        self.assertTrue(team.members.filter(pk=self.user1.pk).exists())

    def test_user_can_join_team_by_invite_code(self):
        team = Team.objects.create(name="Beta", hackathon=self.hackathon, captain=self.user1)
        team.members.add(self.user1)

        self.client.login(username="u2", password="pass12345")
        response = self.client.post(
            reverse("hackathons:team-join"),
            {"invite_code": team.invite_code.lower()},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        team.refresh_from_db()
        self.assertTrue(team.members.filter(pk=self.user2.pk).exists())
        self.assertContains(response, "Вы вступили в команду")

    def test_captain_can_delete_own_team(self):
        team = Team.objects.create(name="Gamma", hackathon=self.hackathon, captain=self.user1)
        team.members.add(self.user1)
        self.client.login(username="u1", password="pass12345")

        response = self.client.post(
            reverse("hackathons:team-delete", kwargs={"pk": team.pk}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Team.objects.filter(pk=team.pk).exists())
        self.assertContains(response, "Команда удалена")

    def test_non_captain_cannot_delete_team(self):
        team = Team.objects.create(name="Delta", hackathon=self.hackathon, captain=self.user1)
        team.members.add(self.user1)
        self.client.login(username="u2", password="pass12345")

        response = self.client.post(reverse("hackathons:team-delete", kwargs={"pk": team.pk}))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Team.objects.filter(pk=team.pk).exists())

    def test_superuser_can_delete_any_team(self):
        team = Team.objects.create(name="Omega", hackathon=self.hackathon, captain=self.user1)
        team.members.add(self.user1)
        admin = User.objects.create_superuser(
            username="chief2", email="chief2@example.com", password="pass12345"
        )
        self.client.login(username="chief2", password="pass12345")

        response = self.client.post(
            reverse("hackathons:team-delete", kwargs={"pk": team.pk}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Team.objects.filter(pk=team.pk).exists())
        self.assertContains(response, "Команда удалена")


class ApplicationFlowTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="org2", password="pass12345")
        UserProfile.objects.create(user=self.organizer, role=UserProfile.Roles.ORGANIZER)

        self.participant = User.objects.create_user(username="part2", password="pass12345")
        UserProfile.objects.create(user=self.participant, role=UserProfile.Roles.PARTICIPANT)

        self.hackathon = Hackathon.objects.create(
            title="Apply Hack",
            description="Desc",
            start_date="2026-08-01",
            end_date="2026-08-02",
            location="Online",
            is_open=True,
        )

    def test_participant_can_create_application(self):
        self.client.login(username="part2", password="pass12345")

        response = self.client.post(
            reverse("hackathons:application-create", kwargs={"pk": self.hackathon.pk}),
            {"motivation": "Хочу участвовать"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        app = Application.objects.get(hackathon=self.hackathon, user=self.participant)
        self.assertEqual(app.status, Application.Status.PENDING)

    def test_organizer_can_approve_application(self):
        app = Application.objects.create(hackathon=self.hackathon, user=self.participant)
        self.client.login(username="org2", password="pass12345")

        response = self.client.post(
            reverse(
                "hackathons:application-status",
                kwargs={"pk": app.pk, "status": "approved"},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.APPROVED)

    def test_application_blocked_when_deadline_passed(self):
        self.hackathon.application_deadline = timezone.localdate() - timedelta(days=1)
        self.hackathon.save(update_fields=["application_deadline"])
        self.client.login(username="part2", password="pass12345")

        response = self.client.post(
            reverse("hackathons:application-create", kwargs={"pk": self.hackathon.pk}),
            {"motivation": "late"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Application.objects.filter(hackathon=self.hackathon, user=self.participant).exists())
        self.assertContains(response, "Дедлайн подачи заявок уже прошёл")

    def test_application_blocked_when_limit_reached(self):
        self.hackathon.max_participants = 1
        self.hackathon.save(update_fields=["max_participants"])
        another = User.objects.create_user(username="another", password="pass12345")
        UserProfile.objects.create(user=another, role=UserProfile.Roles.PARTICIPANT)
        Application.objects.create(
            hackathon=self.hackathon,
            user=another,
            status=Application.Status.APPROVED,
        )
        self.client.login(username="part2", password="pass12345")

        response = self.client.post(
            reverse("hackathons:application-create", kwargs={"pk": self.hackathon.pk}),
            {"motivation": "try"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Application.objects.filter(hackathon=self.hackathon, user=self.participant).exists())
        self.assertContains(response, "Лимит участников уже достигнут")


class ProjectSubmissionAndJuryTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="org3", password="pass12345")
        UserProfile.objects.create(user=self.organizer, role=UserProfile.Roles.ORGANIZER)

        self.mentor = User.objects.create_user(username="mentor1", password="pass12345")
        UserProfile.objects.create(user=self.mentor, role=UserProfile.Roles.MENTOR)

        self.participant = User.objects.create_user(username="part3", password="pass12345")
        UserProfile.objects.create(user=self.participant, role=UserProfile.Roles.PARTICIPANT)

        self.hackathon = Hackathon.objects.create(
            title="Submit Hack",
            description="Desc",
            start_date="2026-09-01",
            end_date="2026-09-03",
            location="Online",
            is_open=True,
        )

    def test_approved_participant_can_submit_project(self):
        Application.objects.create(
            hackathon=self.hackathon,
            user=self.participant,
            status=Application.Status.APPROVED,
        )
        self.client.login(username="part3", password="pass12345")

        response = self.client.post(
            reverse("hackathons:project-submit", kwargs={"pk": self.hackathon.pk}),
            {
                "title": "Smart Solution",
                "description": "ML project",
                "repo_url": "https://github.com/example/repo",
                "demo_url": "https://example.com/demo",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ProjectSubmission.objects.filter(hackathon=self.hackathon, user=self.participant).exists()
        )
        self.assertContains(response, "Проект успешно отправлен")

    def test_unapproved_participant_cannot_submit_project(self):
        self.client.login(username="part3", password="pass12345")

        response = self.client.post(
            reverse("hackathons:project-submit", kwargs={"pk": self.hackathon.pk}),
            {
                "title": "Blocked",
                "description": "No app",
                "repo_url": "",
                "demo_url": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ProjectSubmission.objects.filter(hackathon=self.hackathon, user=self.participant).exists())
        self.assertContains(response, "Подача проекта доступна только одобренным участникам")

    def test_jury_member_can_score_project(self):
        submission = ProjectSubmission.objects.create(
            hackathon=self.hackathon,
            user=self.participant,
            title="Score Me",
        )
        self.client.login(username="mentor1", password="pass12345")

        response = self.client.post(
            reverse("hackathons:submission-score", kwargs={"pk": submission.pk}),
            {"score": 9, "comment": "Отличная работа"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        score = JuryScore.objects.get(submission=submission, jury=self.mentor)
        self.assertEqual(score.score, 9)
        self.assertContains(response, "Оценка сохранена")


class BackwardCompatibilityTests(TestCase):
    def setUp(self):
        self.participant = User.objects.create_user(username="compat_part", password="pass12345")
        UserProfile.objects.create(user=self.participant, role=UserProfile.Roles.PARTICIPANT)
        self.hackathon = Hackathon.objects.create(
            title="Compat Hack",
            description="Desc",
            start_date="2026-10-01",
            end_date="2026-10-02",
            location="Online",
            is_open=True,
        )

    @patch("hackathons.views.ProjectSubmission.objects.filter")
    def test_detail_page_does_not_crash_if_submission_table_missing(self, mock_filter):
        mock_filter.side_effect = OperationalError("no such table: hackathons_projectsubmission")

        response = self.client.get(reverse("hackathons:hackathon-detail", kwargs={"pk": self.hackathon.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Подача проектов")


    @patch("hackathons.views.ProjectSubmission.objects.filter")
    def test_submit_page_does_not_crash_if_submission_table_missing(self, mock_filter):
        Application.objects.create(
            hackathon=self.hackathon,
            user=self.participant,
            status=Application.Status.APPROVED,
        )
        self.client.login(username="compat_part", password="pass12345")
        mock_filter.side_effect = OperationalError("no such table: hackathons_projectsubmission")

        response = self.client.get(
            reverse("hackathons:project-submit", kwargs={"pk": self.hackathon.pk}),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("hackathons:hackathon-detail", kwargs={"pk": self.hackathon.pk}),
        )

    @patch("hackathons.views.Hackathon.objects.order_by")
    def test_home_page_does_not_crash_if_hackathon_table_missing(self, mock_order_by):
        mock_order_by.side_effect = OperationalError("no such table: hackathons_hackathon")

        response = self.client.get(reverse("hackathons:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Новости")


class TeamPreconditionsTests(TestCase):
    def test_cannot_open_team_create_without_open_hackathons(self):
        user = User.objects.create_user(username="u3", password="pass12345")
        UserProfile.objects.create(user=user, role=UserProfile.Roles.PARTICIPANT)
        self.client.login(username="u3", password="pass12345")

        response = self.client.get(reverse("hackathons:team-create"), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пока нет открытых хакатонов")


class TemplateIntegrityTests(TestCase):
    def test_templates_do_not_contain_merge_conflict_markers(self):
        templates_dir = Path("templates")
        for template_path in templates_dir.rglob("*.html"):
            content = template_path.read_text(encoding="utf-8")
            self.assertNotIn("<<<<<<<", content, f"Merge marker found in {template_path}")
            self.assertNotIn(">>>>>>>", content, f"Merge marker found in {template_path}")

    def test_home_template_has_single_extends(self):
        home = Path("templates/hackathons/home.html").read_text(encoding="utf-8")
        extends_count = home.count("{% extends")
        self.assertEqual(extends_count, 1)
        self.assertIn("{% extends 'hackathons/base.html' %}", home)


class SuperuserAccessTests(TestCase):
    def test_superuser_sees_manage_buttons_on_list(self):
        admin = User.objects.create_superuser(
            username="chief", email="chief@example.com", password="pass12345"
        )
        Hackathon.objects.create(
            title="Admin Hack",
            description="Desc",
            start_date="2026-11-01",
            end_date="2026-11-02",
            location="Online",
            is_open=True,
        )

        self.client.login(username="chief", password="pass12345")
        response = self.client.get(reverse("hackathons:hackathon-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Создать хакатон")


class HackathonListFiltersTests(TestCase):
    def setUp(self):
        Hackathon.objects.create(
            title="Open AI",
            description="Desc",
            start_date="2026-12-01",
            end_date="2026-12-02",
            location="Online",
            is_open=True,
        )
        Hackathon.objects.create(
            title="Closed Web",
            description="Desc",
            start_date="2026-12-03",
            end_date="2026-12-04",
            location="Online",
            is_open=False,
        )

    def test_filter_by_query(self):
        response = self.client.get(reverse("hackathons:hackathon-list"), {"q": "Open"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Open AI")
        self.assertNotContains(response, "Closed Web")

    def test_filter_open_only(self):
        response = self.client.get(reverse("hackathons:hackathon-list"), {"open_only": "1"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Open AI")
        self.assertNotContains(response, "Closed Web")


class AdminSmokeTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin_smoke", email="admin@example.com", password="pass12345"
        )
        self.staff_user = User.objects.create_user(
            username="staff_to_delete", email="staff@example.com", password="pass12345"
        )
        self.group = Group.objects.create(name="ToDelete")
        self.staff_admin = User.objects.create_user(
            username="staff_admin", email="staff_admin@example.com", password="pass12345", is_staff=True
        )
        self.hackathon = Hackathon.objects.create(
            title="Smoke",
            description="Desc",
            start_date="2026-10-01",
            end_date="2026-10-02",
            location="Online",
            is_open=True,
        )
        self.team = Team.objects.create(
            name="Smoke Team",
            hackathon=self.hackathon,
            captain=self.admin,
        )
        self.team.members.add(self.admin)

    def test_admin_pages_render(self):
        self.client.login(username="admin_smoke", password="pass12345")

        for url in [
            "/admin/",
            "/admin/hackathons/hackathon/",
            f"/admin/hackathons/hackathon/{self.hackathon.pk}/change/",
            f"/admin/hackathons/team/{self.team.pk}/change/",
            "/admin/auth/user/",
            "/admin/auth/group/",
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, msg=f"Failed for {url}")

    def test_team_admin_change_form_has_members_field(self):
        self.client.login(username="admin_smoke", password="pass12345")
        response = self.client.get(f"/admin/hackathons/team/{self.team.pk}/change/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="id_members"')

    def test_admin_can_open_delete_pages_for_core_models(self):
        self.client.login(username="admin_smoke", password="pass12345")

        for url in [
            f"/admin/hackathons/hackathon/{self.hackathon.pk}/delete/",
            f"/admin/hackathons/team/{self.team.pk}/delete/",
            f"/admin/auth/user/{self.staff_user.pk}/delete/",
            f"/admin/auth/group/{self.group.pk}/delete/",
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, msg=f"Failed for {url}")

    def test_staff_admin_can_manage_user_and_group_in_admin(self):
        victim = User.objects.create_user(username="victim_user", password="pass12345")
        grp = Group.objects.create(name="VictimGroup")
        self.client.login(username="staff_admin", password="pass12345")

        for url in [
            "/admin/auth/user/",
            f"/admin/auth/user/{victim.pk}/change/",
            f"/admin/auth/user/{victim.pk}/delete/",
            "/admin/auth/group/",
            f"/admin/auth/group/{grp.pk}/change/",
            f"/admin/auth/group/{grp.pk}/delete/",
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, msg=f"Failed for {url}")


class AdminTemplateSourceTests(TestCase):
    def test_project_does_not_override_admin_changelist_template(self):
        template_path = Path("templates/admin/change_list.html")
        self.assertFalse(template_path.exists())

    def test_project_does_not_override_admin_change_form_template(self):
        template_path = Path("templates/admin/change_form.html")
        self.assertFalse(template_path.exists())


class ScheduleAndResultsTests(TestCase):
    def setUp(self):
        self.hackathon = Hackathon.objects.create(
            title="Final Hack",
            description="Desc",
            start_date="2026-09-10",
            end_date="2026-09-11",
            location="Online",
            is_open=True,
        )
        self.team = Team.objects.create(
            name="Winners",
            hackathon=self.hackathon,
            captain=User.objects.create_user(username="cap", password="pass12345"),
        )
        ScheduleItem.objects.create(
            hackathon=self.hackathon,
            title="Открытие",
            starts_at=timezone.make_aware(datetime(2026, 9, 10, 10, 0)),
            description="Старт программы",
        )
        ResultEntry.objects.create(
            hackathon=self.hackathon,
            place=1,
            team=self.team,
            project_name="Best Project",
            description="Победитель хакатона",
        )

    def test_detail_shows_schedule_and_results(self):
        response = self.client.get(reverse("hackathons:hackathon-detail", kwargs={"pk": self.hackathon.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Расписание")
        self.assertContains(response, "Открытие")
        self.assertContains(response, "Результаты")
        self.assertContains(response, "Best Project")
