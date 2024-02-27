from django.shortcuts import render, redirect
from django.core.cache import cache
from .models import ShortenURL
import hashlib
import base64
from django.conf import settings
from urllib.parse import urlparse

BASE_NAME = settings.BASE_NAME


def index(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        if not is_valid_url(original_url):
            return render(request, 'shortener/index.html', {'error': 'Invalid URL'})

        context = manage_url(original_url)
        return render(request, 'shortener/index.html', context)
    return render(request, 'shortener/index.html')


def manage_url(original_url):
    shorten_url = generate_or_fetch_shorten_url(original_url)
    shorten_url_obj = ShortenURL.objects.get(shorten_url=shorten_url)
    context = {
        'original_url': original_url,
        'shorten_url': shorten_url,
        'created_at': shorten_url_obj.created_at,
        'shorten_url_code': shorten_url.split('/')[-1]
    }
    return context


def generate_or_fetch_shorten_url(original_url):
    shorten_url = generate_shorten_url(original_url)
    _, created = ShortenURL.objects.get_or_create(
        original_url=original_url,
        defaults={'shorten_url': shorten_url}
    )
    if created:
        cache.set(shorten_url, original_url)
    return shorten_url


def generate_shorten_url(original_url: str) -> str:
    for _ in range(10):
        shorten_url = create_shorten_url(original_url)
        if not ShortenURL.objects.filter(shorten_url=shorten_url).exists():
            return f"https://{BASE_NAME}/{shorten_url}"
        original_url += '0'
    raise ValueError("Unable to generate a unique shorten URL")


def create_shorten_url(original_url: str) -> str:
    hash_data = hashlib.sha256(original_url.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(hash_data).decode('utf-8')[:6]


def redirect_original_url(request, shorten_url_code):
    shorten_url = f"https://{BASE_NAME}/{shorten_url_code}"
    original_url = cache.get(shorten_url) or fetch_and_cache_original_url(shorten_url)
    return redirect(original_url)


def fetch_and_cache_original_url(shorten_url):
    print('Fetching from DB')
    print(shorten_url)
    original_url = ShortenURL.objects.get(shorten_url=shorten_url).original_url
    cache.set(shorten_url, original_url)
    return original_url


def is_valid_url(url) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
