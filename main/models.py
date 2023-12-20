from django.db import models
from django.contrib.auth.models import User
from WerewolfWeb.settings import GAME_ROLES


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game_role = models.IntegerField(choices=GAME_ROLES, default=0)

    # action_id = models.AutoField()
# DO NOT USE _id!

# sessionId = models.ForeignKey
# playerId = models.ForeignKey
# night = models.BooleanField
# actionType = models.
# targetId =

# Create your models here.
