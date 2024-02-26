from django.shortcuts import render, redirect
from django.core.cache import cache
from .models import ShortenURL
import hashlib
import base64


# Create your views here.


def index(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')

        shorten_url = generate_shorten_url(original_url)
        if ShortenURL.objects.filter(shorten_url=shorten_url).exists():
            return render(request, 'shortener/index.html', {'shorten_url': shorten_url})
        shorten_url_obj = ShortenURL(original_url=original_url, shorten_url=shorten_url)
        shorten_url_obj.save()
        cache.set(shorten_url, original_url)
        return render(request, 'shortener/index.html', {'shorten_url': shorten_url})
    return render(request, 'shortener/index.html')


def generate_shorten_url(original_url: str) -> str:
    hash_data = hashlib.sha256(original_url.encode('utf-8')).digest()
    shorten_url = base64.urlsafe_b64encode(hash_data).decode('utf-8')[:6]
    return shorten_url


def redirect_original_url(request, shorten_url):
    original_url = cache.get(shorten_url)
    if original_url is None:
        original_url = ShortenURL.objects.get(shorten_url=shorten_url).original_url
        cache.set(shorten_url, original_url)
    return redirect(original_url)
