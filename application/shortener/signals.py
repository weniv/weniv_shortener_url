"""ShortenURL 이 바뀌면 Redis 캐시를 함께 무효화한다.

리다이렉트 뷰(views.redirect_original_url)는 DB 보다 캐시를 먼저 조회하므로,
캐시를 지우지 않으면 DB 에서 삭제한 URL 이 캐시 TTL(1일) 동안 계속 연결된다.
"""
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ShortenURL


def _purge(instance):
    # shorten_url 을 수정한 경우 예전 키가 남아 옛 목적지로 계속 연결되므로 함께 지운다.
    keys = {instance.shorten_url, getattr(instance, '_loaded_shorten_url', None)}
    for key in keys:
        if key:
            cache.delete(key)


@receiver(post_delete, sender=ShortenURL)
def purge_cache_on_delete(sender, instance, **kwargs):
    _purge(instance)


@receiver(post_save, sender=ShortenURL)
def purge_cache_on_save(sender, instance, **kwargs):
    _purge(instance)
