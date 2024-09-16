# models.py

from django.db import models


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class NewUser(TimestampModel):
    google_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    authkey = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    picture_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
