# Generated by Django 4.1 on 2023-05-14 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_general', '0003_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='for_all',
            field=models.BooleanField(default=True),
        ),
    ]
