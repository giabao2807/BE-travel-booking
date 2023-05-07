from django.db import models
from django.db.models import Manager


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    link = models.CharField(max_length=255)

    objects = Manager
