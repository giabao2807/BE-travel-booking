from django.db import models


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    link = models.CharField(max_length=255)