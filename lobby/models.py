from django.contrib.auth.models import User
from django.db import models

from WerewolfWeb.settings import GAME_STATUS


# Create your models here.


class Lobby(models.Model):
    name = models.CharField(max_length=255)
    max_players = models.IntegerField(default=0)
    players = models.ManyToManyField(User, default=None, blank=True)
    game_status = models.IntegerField(choices=GAME_STATUS)
    game_admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_admin')

    def __str__(self):
        return f'{self.name} - max: {self.max_players} - players: {self.players.count()}'


class Round(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    round = models.IntegerField(default=1)
