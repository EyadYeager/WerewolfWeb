from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View

from lobby.models import Lobby


# Create your views here.

class LobbyView(View):
    def get(self, request, id):
        # print(id)

        try:
            lobby = Lobby.objects.get(id=id)
        except Lobby.DoesNotExist:
            return redirect('/lobby/')

        return render(request, 'lobby/lobby.html', {'lobby': lobby})


class MainLobbyView(View):
    def get(self, request):
        lobbies = Lobby.objects.all()

        return render(request, 'lobby/main.html', {'lobbies': lobbies})


class LobbyJoinView(View):
    def get(self, request, id):
        user = request.user

        try:
            lobby = Lobby.objects.get(id=id)

            if user not in lobby.players.all():
                lobby.players.add(user)
            else:
                print("already in game")
        except Lobby.DoesNotExist:
            redirect('/lobby/')
        return redirect(f'/lobby/{id}/')


class LobbyLeaveView(View):
    def get(self, request, id):
        user = request.user

        try:
            lobby = Lobby.objects.get(id=id)

            if user not in lobby.players.all():
                print("Player is not in the lobby")
            else:
                lobby.players.remove(user)
        except Lobby.DoesNotExist:
            redirect('/lobby/')
        return redirect(f'/lobby/{id}/')
