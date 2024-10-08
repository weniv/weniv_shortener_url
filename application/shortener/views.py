from django.shortcuts import render, redirect
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse, HttpResponsePermanentRedirect
from .models import ShortenURL
import hashlib
import base64
from django.conf import settings
from urllib.parse import urlparse
import re
import json

BASE_NAME = settings.BASE_NAME


@ratelimit(key='ip', rate='8/m', block=False)
def index(request):
    was_limit_exceeded = getattr(request, 'limited', False)
    if was_limit_exceeded:
        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        if not is_valid_url(original_url):
            return render(request, 'shortener/index.html', {'error': 'Invalid URL'})
        # log_access(request)
        context = manage_url(original_url)
        return render(request, 'shortener/index.html', context)
    return render(request, 'shortener/index.html')


def manage_url(original_url):
    try:
        shorten_url_with_protocol, shorten_url_code = generate_or_fetch_shorten_url(original_url)
        shorten_url_obj = ShortenURL.objects.get(shorten_url=shorten_url_with_protocol)
        context = {
            'original_url': original_url,
            'shorten_url': shorten_url_with_protocol,
            'created_at': shorten_url_obj.created_at,
            'shorten_url_code': shorten_url_code
        }
        return context
    except ShortenURL.DoesNotExist:
        return {'error': 'Shorten URL does not exist.'}
    except ValueError as e:
        return {'error': str(e)}


def generate_or_fetch_shorten_url(original_url):
    # 원본 URL에 해당하는 객체가 이미 있는지 확인합니다.
    existing_obj = ShortenURL.objects.filter(original_url=original_url).first()
    if existing_obj:
        # 이미 존재하는 경우, 저장된 단축 URL과 코드를 반환합니다.
        return existing_obj.shorten_url, existing_obj.shorten_url.split('/')[-1]

    # 새로운 단축 URL을 생성하는 로직
    shorten_url_code = generate_shorten_url(original_url)
    shorten_url_with_protocol = f"https://{BASE_NAME}/{shorten_url_code}"
    obj, created = ShortenURL.objects.get_or_create(
        original_url=original_url,
        defaults={'shorten_url': shorten_url_with_protocol}
    )
    if created:
        cache.set(shorten_url_with_protocol, original_url)
    return shorten_url_with_protocol, shorten_url_code


def generate_shorten_url(original_url: str) -> str:
    max_attempts = 10
    for attempt in range(max_attempts):
        temp_url = original_url + str(attempt)
        hash_data = hashlib.sha256(temp_url.encode('utf-8')).digest()
        shorten_url_code = base64.urlsafe_b64encode(hash_data).decode('utf-8')[:6]
        if not ShortenURL.objects.filter(shorten_url__endswith=shorten_url_code).exists():
            return shorten_url_code
    raise ValueError("Failed to generate a unique shorten URL after multiple attempts")


@ratelimit(key='ip', rate='30/m', block=False)
def redirect_original_url(request, shorten_url_code):
    was_limit_exceeded = getattr(request, 'limited', False)
    if was_limit_exceeded:
        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

    # URL 끝의 슬래시 제거
    shorten_url_code = shorten_url_code.rstrip('/') if shorten_url_code.endswith('/') else shorten_url_code

    shorten_url = f"https://{BASE_NAME}/{shorten_url_code}"
    original_url = cache.get(shorten_url) or fetch_and_cache_original_url(shorten_url)
    if not original_url:
        # 적절한 에러 페이지나 홈페이지로 리다이렉트
        return redirect('/')
    return redirect(original_url)


def fetch_and_cache_original_url(shorten_url):
    shorten_url = shorten_url.rstrip('/') if shorten_url.endswith('/') else shorten_url
    try:
        original_url_obj = ShortenURL.objects.get(shorten_url=shorten_url)
        cache.set(shorten_url, original_url_obj.original_url, timeout=86400)  # 예를 들어, 1일 동안 캐시
        return original_url_obj.original_url
    except ShortenURL.DoesNotExist:
        return None


def is_valid_url(url) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def generate_staff_url(original_url, url_name):
    shorten_url_with_protocol = f"https://{BASE_NAME}/{url_name}"
    existing_url = ShortenURL.objects.filter(shorten_url=shorten_url_with_protocol).first()

    if existing_url:
        if existing_url.original_url != original_url:
            return {'error': 'This short name is already in use for a different URL.'}
    else:
        ShortenURL.objects.create(
            original_url=original_url,
            shorten_url=shorten_url_with_protocol
        )

    shorten_url_obj = ShortenURL.objects.get(shorten_url=shorten_url_with_protocol)
    context = {
        'original_url': original_url,
        'shorten_url': shorten_url_with_protocol,
        'created_at': shorten_url_obj.created_at,
        'shorten_url_code': url_name
    }

    return context


def staff_index(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        url_name = request.POST.get('url_name')

        if not is_valid_url(original_url):
            return render(request, 'shortener/staff.html', {'error': 'Invalid URL format'})

        if not re.match(r'^[a-zA-Z0-9-]+$', url_name):
            return render(request, 'shortener/staff.html',
                          {'error': 'Invalid URL name. Use only alphanumeric characters.'})

        ## URL이 http:// 또는 https://로 시작하는지 확인, 대소문자, 숫자만 적용되었는지 확인
        if "http" not in original_url or "https" not in original_url:
            return render(request, 'shortener/staff.html', {'error': 'URL must start with http:// or https://'})

        context = generate_staff_url(original_url, url_name)

        if 'error' in context:
            return render(request, 'shortener/staff.html', {'error': context['error']})

        return render(request, 'shortener/staff.html', context)
    return render(request, 'shortener/staff.html')


@csrf_exempt
@require_http_methods(['POST'])
def api_generate_shorten_url(request):
    try:
        data = json.loads(request.body)
        original_url = data.get('url')

        if not original_url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        if not is_valid_url(original_url):
            return JsonResponse({'error': 'Invalid URL'}, status=400)

        shorten_url_code = generate_shorten_url(original_url)
        shorten_url = f"https://{BASE_NAME}/{shorten_url_code}"

        if ShortenURL.objects.filter(shorten_url=shorten_url).exists():
            return JsonResponse(JsonResponse({'shorten_url': shorten_url}))
        else:
            ShortenURL.objects.create(
                original_url=original_url,
                shorten_url=shorten_url
            )

        return JsonResponse({'shorten_url': shorten_url})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
