from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Hackathon, UserProfile


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

    def test_organizer_can_edit_hackathon(self):
        self.client.login(username="org", password="pass12345")

        response = self.client.post(
            reverse("hackathons:hackathon-edit", kwargs={"pk": self.hackathon.pk}),
            {
                "title": "Updated",
                "description": "Updated Desc",
                "start_date": "2026-05-01",
                "end_date": "2026-05-03",
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
