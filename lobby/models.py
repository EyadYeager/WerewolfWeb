from django.contrib.auth.models import User
from django.db import models

from WerewolfWeb.settings import GAME_STATUS, GAME_CYCLE, GAME_ROLES


# class Player(models.Model):
#     playerId = models.AutoField(User, primary_key=True)
#     username = models.CharField(User, max_length=20)

# Create your models here.


class Lobby(models.Model):
    lobbyId = models.AutoField(primary_key=True)
    lobby_name = models.CharField(max_length=255)
    # players = models.ManyToManyField(User, default=None, blank=True)
    game_admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    game_status = models.IntegerField(choices=GAME_STATUS)
    game_cycle = models.IntegerField(choices=GAME_CYCLE, default=0)
    max_players = models.IntegerField()

    # def __str__(self):
    #     return f'{self.lobbyid} - max: {self.max_players} - players: {self.players.count()}'


class Participant(models.Model):
    lobbyId = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='participants')
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(choices=GAME_ROLES)
    vote_count = models.IntegerField()
    voted = models.BooleanField(default=False)
    killed = models.IntegerField(default=0)
    rescued = models.IntegerField(default=0)


# class GameCycle(models.Model):
#     lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
#     is_night = models.BooleanField(default=False)
#
#
# class Round(models.Model):
#     lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
#     round = models.IntegerField(default=1)
