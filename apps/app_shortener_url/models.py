from django.db import models


# Create your models here.
class Shortener(models.Model):
    original_url = models.URLField(
        max_length=255, db_column="original_url", name="original_url"
    )
    short_url = models.URLField(
        max_length=100, db_column="short_url", name="short_url", default=""
    )
    created = models.DateTimeField(auto_now_add=True)

    visit_count = models.IntegerField(default=0)

    class Meta:

        ordering = ["-created"]

    def __str__(self):

        return f'{self.original_url} to {self.short_url}'
    # active = models.BooleanField(default=False, null=False, blank=False, name="active")
    # created_at = models.DateTimeField(
    #     name="createTime", auto_now=True, null=False, blank=False
    # )
    # expire_date = models.DateField(name="expireDate", null=False, blank=False)
