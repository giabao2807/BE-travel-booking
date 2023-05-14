# Generated by Django 4.1 on 2023-05-14 03:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api_general', '0003_coupon'),
        ('api_tour', '0004_reset_data_tour'),
    ]

    operations = [
        migrations.CreateModel(
            name='TourCoupon',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tour_coupons', to='api_general.coupon')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tour_coupons', to='api_tour.tour')),
            ],
            options={
                'db_table': 'tour_coupons',
            },
        ),
    ]
