# Generated by Django 4.1 on 2023-06-05 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_tour', '0006_alter_tour_total_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='num_review',
        ),
        migrations.AlterField(
            model_name='tour',
            name='language_tour',
            field=models.CharField(blank=True, default='Việt Nam', max_length=255, null=True),
        ),
    ]
