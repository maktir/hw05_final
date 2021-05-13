from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_uses_correct_template(self):
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
