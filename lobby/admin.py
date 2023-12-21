from django.contrib import admin

# Register your models here.

from lobby.models import *


class LobbyAdmin(admin.ModelAdmin):
    list_display = ["name", "max_players", "game_status", "no_of_players"]

    def no_of_players(self, obj):
        return obj.players.count()


admin.site.register(Lobby, LobbyAdmin)
