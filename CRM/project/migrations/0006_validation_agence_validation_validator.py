# Generated by Django 5.0.2 on 2024-03-15 15:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_validation'),
    ]

    operations = [
        migrations.AddField(
            model_name='validation',
            name='agence',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='project.agence'),
        ),
        migrations.AddField(
            model_name='validation',
            name='validator',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='validators', to='project.utilisateur'),
        ),
    ]
