from django.db import models


# Create your models here.

class ShortenURL(models.Model):
    original_url = models.URLField(max_length=200)
    shorten_url = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_url + ' -> ' + self.shorten_url

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shorten URL'
        verbose_name_plural = 'Shorten URLs'
        db_table = 'shortener_url'


class AccessLog(models.Model):
    ip_address = models.CharField(max_length=45)  # IPv4와 IPv6 지원
    access_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('ip_address', 'access_date')  # IP와 날짜 조합으로 유니크 설정
        db_table = 'shortener_access_log'

    def __str__(self):
        return f"{self.ip_address} - {self.access_date}"
