# Generated by Django 5.0 on 2024-03-27 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_profile_game_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='game_role',
            field=models.IntegerField(choices=[(0, 'Citizen'), (1, 'Werewolf'), (2, 'Doctor'), (3, 'DEAD'), (4, 'Spectate')], default=0),
        ),
    ]
