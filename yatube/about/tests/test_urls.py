from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_url_exists_at_desired_location(self):
        urls = ['/about/author/', '/about/tech/']
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
