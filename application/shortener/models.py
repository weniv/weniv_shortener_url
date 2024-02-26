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


