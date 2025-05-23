from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator
from WerewolfWeb.settings import GAME_STATUS, GAME_CYCLE, GAME_ROLES


class Lobby(models.Model):
    lobbyId = models.AutoField(primary_key=True)
    lobby_name = models.CharField(max_length=255)
    # players = models.ManyToManyField(User, default=None, blank=True)
    game_admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    game_status = models.IntegerField(choices=GAME_STATUS)
    game_cycle = models.IntegerField(choices=GAME_CYCLE, default=0)
    max_players = models.IntegerField(validators=[MaxValueValidator(16)])

    # def __str__(self):
    #     return f'{self.lobbyid} - max: {self.max_players} - players: {self.players.count()}'


class Participant(models.Model):
    lobbyId = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='participants')
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(choices=GAME_ROLES, default=4)
    vote_count = models.IntegerField(default=0)
    dayvoted = models.BooleanField(default=False)
    nightvoted = models.BooleanField(default=False)
    killed = models.IntegerField(default=0)
    rescued = models.IntegerField(default=0)
    dead = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)


class Message(models.Model):
    lobbyId = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    userId = models.ForeignKey(Participant, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
