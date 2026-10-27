"""보안 점검(2026-10-27): 직원 페이지 서버 확인, http(s) 외 주소 거부, API 오류 내용 숨기기, 접속 IP."""

from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from application.middleware import XForwardedForMiddleware

from .models import ShortenURL
from .views import is_valid_url


class SecurityTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_only_http_and_https_are_valid(self):
        self.assertTrue(is_valid_url('https://weniv.co.kr'))
        self.assertTrue(is_valid_url('HTTP://weniv.co.kr/a'))
        for url in ('javascript://x', 'javascript:alert(1)', 'kakaoopen://card/create', 'ftp://a.b', '//a.b', 'a.b', '', None):
            self.assertFalse(is_valid_url(url), url)

    def test_staff_page_needs_server_side_password(self):
        response = self.client.get('/staff/shorten_url')
        self.assertContains(response, 'name="password"')
        response = self.client.post('/staff/shorten_url', {'original_url': 'https://weniv.co.kr', 'url_name': 'evil'})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ShortenURL.objects.filter(shorten_url='https://weniv.link/evil').exists())

    def test_wrong_password_is_rejected_and_limited(self):
        for _ in range(5):
            self.assertEqual(self.client.post('/staff/login', {'password': 'hati'}).status_code, 403)
        self.assertEqual(self.client.post('/staff/login', {'password': 'staff-test-password'}).status_code, 429)

    def test_staff_can_create_named_link_after_login(self):
        response = self.client.post('/staff/login', {'password': 'staff-test-password'})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/staff/shorten_url', {'original_url': ' https://weniv.co.kr ', 'url_name': 'study1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ShortenURL.objects.get(shorten_url='https://weniv.link/study1').original_url, 'https://weniv.co.kr')

    @override_settings(STAFF_PASSWORD='')
    def test_staff_page_closed_without_password_setting(self):
        self.assertEqual(self.client.post('/staff/login', {'password': ''}).status_code, 403)

    def test_api_rejects_non_http_and_hides_errors(self):
        response = self.client.post('/api/generate', '{"url": "javascript://x"}', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/api/generate', '[1]', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/api/generate', '{"url": "https://weniv.co.kr/x"}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        first = response.json()['shorten_url']
        # 예전에는 이미 있는 주소면 JsonResponse를 두 번 감싸 500과 Django 오류 화면이 나왔다
        response = self.client.post('/api/generate', '{"url": "https://weniv.co.kr/x"}', content_type='application/json')
        self.assertEqual(response.json()['shorten_url'], first)

    def test_saved_bad_scheme_goes_home_and_leading_space_still_works(self):
        ShortenURL.objects.create(original_url='javascript://x', shorten_url='https://weniv.link/badOne')
        ShortenURL.objects.create(original_url=' https://forms.gle/abc', shorten_url='https://weniv.link/space1')
        self.assertEqual(self.client.get('/badOne/')['Location'], '/')
        self.assertEqual(self.client.get('/space1/')['Location'], 'https://forms.gle/abc')

    def test_client_cannot_spoof_ip_with_first_forwarded_value(self):
        seen = {}
        middleware = XForwardedForMiddleware(lambda request: seen.setdefault('ip', request.META['REMOTE_ADDR']))
        middleware(RequestFactory().get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 203.0.113.9'))
        self.assertEqual(seen['ip'], '203.0.113.9')
