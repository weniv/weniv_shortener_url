"""위룸 짧은 주소: DB·캐시·외부 서버 없이 연결하고 기존 교재·일반 주소와 구분한다."""

from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import Resolver404, resolve

from .views import redirect_book_short_code, redirect_original_url, redirect_study_short_link, redirect_weroom_short_link


class WeroomLinksTest(SimpleTestCase):
    def test_grouped_alphanumeric_code_keeps_leading_zeroes(self):
        response = self.client.get('/r/km-012-034')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/r/km-012-034/'))

    def test_redirect_with_query(self):
        response = self.client.get('/r/Python-Study?from=class&week=2')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/r/python-study/?from=class&week=2'))
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertEqual(response['X-Robots-Tag'], 'noindex')

    def test_child_and_optional_slash(self):
        for suffix in ('', '/'):
            response = self.client.get(f'/r/abc234/page1234{suffix}')
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response['Location'].endswith('/r/abc234/page1234/'))

    def test_no_database_cache_or_api_dependency(self):
        with patch('shortener.views.fetch_and_cache_original_url') as lookup:
            for _ in range(40):
                self.assertEqual(self.client.get('/r/abc234/').status_code, 302)
            lookup.assert_not_called()

    def test_existing_routes(self):
        self.assertEqual(resolve('/1055-08-06/').func, redirect_book_short_code)
        self.assertEqual(resolve('/2026aid-g/').func, redirect_original_url)
        self.assertEqual(resolve('/r/python-study/').func, redirect_weroom_short_link)
        self.assertEqual(resolve('/s/abc234').func, redirect_study_short_link)
        self.assertEqual(resolve('/sabc23/').func, redirect_original_url)

    def test_study_short_link(self):
        for path in ('/s/abc234', '/s/ABC234/'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response['Location'].endswith('/study/join/?code=ABC234'))
            self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertEqual(self.client.get('/s/abc2345').status_code, 404)

    def test_invalid_names_do_not_match(self):
        for path in ('/r/-bad/', '/r/bad-/', '/r/ab/', '/r/' + 'a' * 41 + '/', '/r/abc/extra/path/'):
            with self.assertRaises(Resolver404):
                resolve(path)
