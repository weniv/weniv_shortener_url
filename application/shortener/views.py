from django.shortcuts import render, redirect
from django.core.cache import cache
from .models import ShortenURL
import hashlib
import base64


def index(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        context = manage_url(original_url)
        return render(request, 'shortener/index.html', context)
    return render(request, 'shortener/index.html')


def manage_url(original_url):
    context = {'original_url': original_url}
    shorten_url = generate_or_fetch_shorten_url(original_url)
    context.update(shorten_url=shorten_url, created_at=ShortenURL.objects.get(shorten_url=shorten_url).created_at)
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
            return shorten_url
        original_url += '0'  # Adjust the URL slightly to try and avoid collisions.
    raise ValueError("Unable to generate a unique shorten URL")


def redirect_original_url(request, shorten_url):
    original_url = cache.get(shorten_url) or fetch_and_cache_original_url(shorten_url)
    return redirect(original_url)


def fetch_and_cache_original_url(shorten_url):
    original_url = ShortenURL.objects.get(shorten_url=shorten_url).original_url
    cache.set(shorten_url, original_url)
    return original_url
