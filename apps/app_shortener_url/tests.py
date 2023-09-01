# Create your tests here.
import unittest

from django.test import Client, TestCase

from apps.app_shortener_url.models import Shortener


class ShortenerTest(TestCase):

    def test_home(self):
        client = Client()

        response = client.get("/home/",headers={"Charset":"utf-8"})
        self.assertEqual(response.status_code,200)

    def test_convert_url_success(self):
        client = Client()

        response = client.post("/shortener/",{"origin_url":"https://www.google.com/"},content_type="application/json")
        html = response.content.decode("utf-8")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.charset,"utf-8")
        self.assertEqual(True,"http://we.niv" in html)

    @unittest.expectedFailure
    def test_convert_url_fail(self):
        client = Client()

        response = client.post("/shortener/",{"origin_url":""},content_type="application/json")
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.charset,"utf-8")

    def test_redirect_url_success(self):
        Shortener.objects.create(
            original_url="https://www.google.com/", short_url="age", hash_key=300000
        )
        client = Client()

        response = client.get("/age",headers={"Charset":"utf-8"})
        self.assertEqual(response.status_code,302)

    def test_redirect_url_fail(self):
        client = Client()

        response = client.get("/age",headers={"Charset":"utf-8"})
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.charset,"utf-8")