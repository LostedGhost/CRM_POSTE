# Generated by Django 5.0.2 on 2024-03-26 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_validation_montant'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='delai',
            field=models.IntegerField(default=0),
        ),
    ]
