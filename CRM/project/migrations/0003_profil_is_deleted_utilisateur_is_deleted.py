# Generated by Django 5.0.2 on 2024-02-14 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_utilisateur_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
