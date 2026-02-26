from django.test import TestCase
from django.urls import reverse

from .models import Hackathon


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
