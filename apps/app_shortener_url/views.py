# Create your views here.
import base64

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.app_shortener_url.CustomException import CurrentException
from apps.app_shortener_url.models import Shortener
from apps.app_shortener_url.serializers import UrlSerializer

DOMAIN_NAME: str = "http://we.niv"


def home(request):
    return render(request, "homepage.html")


def transform_url(original_url: str) -> str:
    original_url_bytes = original_url.encode("ascii")
    short_url =  base64.b64encode(original_url_bytes).decode("ascii")
    return short_url


def decode_url(short_url: str) -> str:
    original_url = base64.b64decode(short_url)
    return original_url.decode("ascii")


@api_view(["POST"])
@csrf_exempt
def convert_url(request) -> Response:

    try:
        url = Shortener.objects.get(original_url=request.data["original_url"])
        serializer = UrlSerializer(url)
        return Response(serializer.data)

    except Shortener.DoesNotExist:
        serializer = UrlSerializer(data =request.data)
        if serializer.is_valid(raise_exception=True):
            short_url = transform_url(request.data["original_url"])
            serializer.save(short_url=short_url)
            return Response(serializer.data)



def redirect_url(request, short_url: str):
    try:
        print(short_url)
        url = Shortener.objects.get(short_url=short_url)
        url.visit_count += 1
        url.save()
        return HttpResponseRedirect(url.original_url)

    except Shortener.DoesNotExist:
        raise CurrentException(404, "URL not found")
