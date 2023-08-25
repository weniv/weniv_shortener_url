from rest_framework import serializers

from apps.app_shortener_url import models
from apps.app_shortener_url.models import Shortener


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shortener
        fields = "__all__"

