# Generated by Django 5.0.2 on 2024-02-15 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agence',
            name='geolocalisation_latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='agence',
            name='geolocalisation_longitude',
            field=models.FloatField(default=0),
        ),
    ]