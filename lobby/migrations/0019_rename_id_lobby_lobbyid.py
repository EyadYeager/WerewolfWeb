# Generated by Django 5.0 on 2024-01-24 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lobby', '0018_rename_lobbyid_lobby_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lobby',
            old_name='id',
            new_name='lobbyid',
        ),
    ]
