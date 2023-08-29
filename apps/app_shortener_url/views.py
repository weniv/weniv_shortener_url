# Create your views here.
import base64
import string

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response

from apps.app_shortener_url.CustomException import CurrentException
from apps.app_shortener_url.models import Shortener

DOMAIN_NAME: str = "http://we.niv"
MAP: str = string.digits + string.ascii_letters


def home(request) -> Response:
    return render(request, "homepage.html")


def encode_url(original_url: str, hash_key: int) -> str:
    short_url = ""
    hash_map = {}
    while hash_key > 0:
        p = hash_key % 62
        short_url += MAP[p]
        hash_key = hash_key // 62
    hash_map[short_url] = original_url
    print(hash_map, short_url)
    return short_url


def decode_url(short_url: str) -> str:
    original_url = base64.b64decode(short_url)
    return original_url.decode("ascii")


@csrf_exempt
def convert_url(request) -> Response:
    origin = "https://chimaek.net"
    hash_key = Shortener.objects.order_by("-id").first().id + 1
    data = encode_url(origin, hash_key)
    return render(request, "homepage.html", {"data": data, "origin_url": origin})


def redirect_url(request, short_url: str):
    try:
        print(short_url)
        url = Shortener.objects.get(short_url=short_url)
        url.visit_count += 1
        url.save()
        return HttpResponseRedirect(url.original_url)

    except Shortener.DoesNotExist:
        raise CurrentException(404, "URL not found")
