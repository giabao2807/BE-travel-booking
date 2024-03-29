# Generated by Django 4.1 on 2023-05-09 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_general', '0002_migrate_cities'),
        ('api_hotel', '0006_migrate_des_rules_for_hotel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='num_review',
        ),
        migrations.AlterField(
            model_name='hotelimage',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotel_images', to='api_hotel.hotel'),
        ),
        migrations.AlterField(
            model_name='hotelimage',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotel_images', to='api_general.image'),
        ),
    ]
