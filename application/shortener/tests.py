from django.test import TestCase

# Create your tests here.
import base64
import hashlib
import random
from unittest import TestCase
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse
from .models import ShortenURL
from .views import index, redirect_original_url
from .urls import app_name
from django.conf import settings
from django.core.cache import cache
from urllib.parse import urlparse
import base64
from .views import generate_or_fetch_shorten_url, generate_shorten_url, fetch_and_cache_original_url, is_valid_url
from django.db import transaction

class Test(TestCase):


    def test_get_index(self):
        request = RequestFactory().get(reverse(f'{app_name}:index'))
        response = index(request)
        self.assertEqual(response.status_code, 200)

    @transaction.atomic
    def test_post_index(self):
        original_url = get_random_original_url()
        request = RequestFactory().post(reverse(f'{app_name}:index'), {'original_url': original_url})
        response = index(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(original_url, response.content.decode('utf-8'))

    @transaction.atomic
    def test_get_redirect_original_url(self):
        original_url = get_random_original_url()
        shorten_url_data = generate_shorten_url(original_url)

        shorten_url = ShortenURL.objects.create(original_url=original_url, shorten_url=shorten_url_data)
        request = RequestFactory().get(reverse(f'shortener:redirect_original_url', args=[shorten_url.shorten_url]))
        response = redirect_original_url(request, shorten_url.shorten_url)
        self.assertEqual(response.url, original_url)

    def test_post_index_invalid_url(self):
        request = RequestFactory().post(reverse(f'{app_name}:index'), {'original_url': 'google.com'})
        response = index(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid URL', response.content.decode('utf-8'))

    def test_generate_or_fetch_shorten_url(self):
        original_url = get_random_original_url()
        shorten_url = generate_or_fetch_shorten_url(original_url)
        cache.set(shorten_url, original_url)
        self.assertEqual(ShortenURL.objects.get(shorten_url=shorten_url).original_url, original_url)
        self.assertEqual(cache.get(shorten_url), original_url)

    @transaction.atomic
    def test_generate_shorten_url(self):
        original_url = get_random_original_url()
        shorten_url = generate_shorten_url(original_url)
        cache.set(shorten_url, original_url)
        ShortenURL.objects.create(original_url=original_url, shorten_url=shorten_url)
        self.assertEqual(ShortenURL.objects.get(shorten_url=shorten_url).original_url, original_url)
        self.assertEqual(cache.get(shorten_url), original_url)

    @transaction.atomic
    def test_fetch_and_cache_original_url(self):
        original_url = get_random_original_url()
        shorten_url_data = generate_shorten_url(original_url)
        shorten_url = ShortenURL.objects.create(original_url=original_url, shorten_url=shorten_url_data)
        original_url = fetch_and_cache_original_url(shorten_url.shorten_url)
        self.assertEqual(cache.get(shorten_url.shorten_url), original_url)

    def test_is_valid_url(self):
        self.assertTrue(is_valid_url('http://www.google.com'))
        self.assertFalse(is_valid_url('google.com'))


def get_random_original_url():
    return f'http://www.google.com/{random.randint(1, 1000)}'
