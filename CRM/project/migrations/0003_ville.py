# Generated by Django 5.0.2 on 2024-02-15 11:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_alter_agence_geolocalisation_latitude_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ville',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=10)),
                ('date_creation', models.DateField(auto_now_add=True)),
                ('date_cessation', models.DateField(default=datetime.datetime(9999, 12, 31, 0, 0))),
                ('modifier_par', models.CharField(max_length=10)),
                ('is_deleted', models.BooleanField(default=False)),
                ('intitule', models.CharField(max_length=100)),
                ('code_postal', models.CharField(max_length=100)),
                ('pays', models.CharField(max_length=100)),
            ],
        ),
    ]
