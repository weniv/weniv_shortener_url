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
        # check url validation
        if not is_valid_url(original_url):
            return render(request, 'shortener/index.html', {'error': 'Invalid URL'})

        context = manage_url(original_url)
        return render(request, 'shortener/index.html', context)
    return render(request, 'shortener/index.html')


def manage_url(original_url):
    context = {'original_url': original_url}
    shorten_url = generate_or_fetch_shorten_url(original_url)
    shorten_url_code = shorten_url.split('/')[-1]
    context.update(shorten_url=shorten_url, created_at=ShortenURL.objects.get(shorten_url=shorten_url).created_at,
                   shorten_url_code=shorten_url_code)
    return context


def generate_or_fetch_shorten_url(original_url):
    shorten_url = generate_shorten_url(original_url)
    if not ShortenURL.objects.filter(shorten_url=shorten_url).exists():
        ShortenURL(original_url=original_url, shorten_url=shorten_url).save()
        cache.set(shorten_url, original_url)
    return shorten_url


def generate_shorten_url(original_url: str) -> str:
    for _ in range(10):  # Try up to 3 times to avoid hash collisions.
        hash_data = hashlib.sha256(original_url.encode('utf-8')).digest()
        shorten_url = base64.urlsafe_b64encode(hash_data).decode('utf-8')[:6]
        if not ShortenURL.objects.filter(shorten_url=shorten_url).exists():
            return f"https://{BASE_NAME}/{shorten_url}"
        original_url += '0'  # Adjust the URL slightly to try and avoid collisions.
    raise ValueError("Unable to generate a unique shorten URL")


def redirect_original_url(request, shorten_url_code):
    shorten_url_code = f"https://{BASE_NAME}/{shorten_url_code}"
    original_url = cache.get(shorten_url_code) or fetch_and_cache_original_url(shorten_url_code)
    return redirect(original_url)


def fetch_and_cache_original_url(shorten_url):
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
