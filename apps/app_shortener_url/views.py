# Create your views here.
import base64
import json
import string

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from apps.app_shortener_url.models import Shortener

DOMAIN_NAME: str = "http://we.niv"
MAP: str = string.digits + string.ascii_letters
APPEND_HASH_KEY: int = 300000


def home(request):
    return render(request, "homepage.html")


def encode_url(original_url: str, hash_key: int) -> str:
    short_url = ""
    hash_map = {}
    while hash_key > 0:
        p = hash_key % 62
        short_url += MAP[p]
        hash_key = hash_key // 62
    hash_map[short_url] = original_url

    return short_url


def decode_url(short_url: str) -> str:
    original_url = base64.b64decode(short_url)
    return original_url.decode("ascii")

def parsing_data_to_json(data):
    return json.loads(data.decode('utf-8'))

@csrf_exempt
def convert_url(request):

    origin_url = parsing_data_to_json(request.body)["origin_url"]

    try:
        hash_key = (Shortener.objects.order_by("-id").first().id + 1) + APPEND_HASH_KEY
    except AttributeError:
        hash_key = 1 * APPEND_HASH_KEY

    short_url = encode_url(origin_url, hash_key)

    shortener = Shortener.objects.create(original_url=origin_url, short_url=short_url,hash_key=hash_key)
    shortener.save()

    return render(request, "homepage.html", {"data": short_url, "origin_url": origin_url})


def redirect_url(request, short_url: str):
    try:
        print(short_url)
        url = Shortener.objects.get(short_url=short_url)
        url.visit_count += 1
        url.save()
        return HttpResponseRedirect(url.original_url)

    except Shortener.DoesNotExist:
        raise Http404("Shortened URL does not exist.")
