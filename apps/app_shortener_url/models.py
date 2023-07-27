from django.db import models


# Create your models here.
class Shortener(models.Model):
    original_url = models.CharField(max_length=255, db_column="original_url", name="originalUrl")
    short_url = models.CharField(max_length=100, db_column="short_url", name="shortUrl", null=True, blank=False)
    active = models.BooleanField(default=False, null=False, blank=False, name="active")
    created_at = models.DateTimeField(name="createTime", auto_now=True, null=False, blank=False)
    expire_date = models.DateField(name="expireDate", null=False, blank=False)
