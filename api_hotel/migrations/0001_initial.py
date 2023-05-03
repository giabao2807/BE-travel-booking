# Generated by Django 4.1 on 2023-05-03 11:18

import dirtyfields.dirtyfields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0001_initial'),
        ('api_tour', '0005_migrate_tour'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('cover_picture', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('descriptions', models.TextField(blank=True, null=True)),
                ('group_size', models.IntegerField(blank=True, null=True)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('rate', models.FloatField(blank=True, null=True)),
                ('rules', models.TextField(blank=True, null=True)),
                ('num_review', models.IntegerField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api_tour.city')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'hotels',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('content', models.CharField(max_length=255)),
                ('rate', models.FloatField(blank=True, null=True)),
                ('hotel_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api_hotel.hotel')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'reviews',
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HotelImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hotel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api_hotel.hotel')),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.image')),
            ],
            options={
                'db_table': 'hotel_image',
            },
        ),
    ]
