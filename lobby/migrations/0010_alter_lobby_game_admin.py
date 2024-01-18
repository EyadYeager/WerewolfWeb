# Generated by Django 5.0 on 2024-01-12 13:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lobby', '0009_alter_lobby_game_admin'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='lobby',
            name='game_admin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_admin', to=settings.AUTH_USER_MODEL),
        ),
    ]
