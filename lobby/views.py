from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View, generic

from lobby.models import Lobby, Round
from WerewolfWeb.settings import GAME_STATUS


# Create your views here.
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


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
        alert = 2
        lobbies = Lobby.objects.filter(players=request.user).exclude(game_status=2, id=id).count()

        try:
            lobby = Lobby.objects.get(id=id)

            if user in lobby.players.all():
                alert = 4
                return render(request, 'lobby/alert.html', {'alert': alert, 'id': id})
            elif lobbies > 0:
                return render(request, 'lobby/alert.html', {'alert': alert, 'id': id})
            else:
                lobby.players.add(user)

        except Lobby.DoesNotExist:
            redirect('/lobby/')
        return redirect(f'/lobby/{id}/')


class LobbyLeaveView(View):
    def get(self, request, id):
        user = request.user
        alert = 3
        lobbies = Lobby.objects.filter(players=request.user).exclude(game_status=2)

        try:
            for l in lobbies:
                l.players.remove(user)

        except Lobby.DoesNotExist:
            redirect('/lobby/')
        return redirect(f'/lobby/{id}/')


class LobbyCreateView(View):
    def get(self, request):
        name = ""
        return render(request, 'lobby/CreateLobby.html')

    def post(self, request):
        name = request.POST.get('name', "Lobby with no name")

        if len(name) < 3:
            return render(request, 'lobby/CreateLobby.html', {"error": "Name should be longer than 2 characters"})
        Lobby.objects.create(name=name, max_players=10, game_admin=request.user, game_status=0)
        return redirect(f'/lobby/')


class GameStart(View):
    def get(self, request, id):
        game = Lobby.objects.get(id=id)
        player_count = game.players.count()
        if player_count < 3:
            alert = 1
            return render(request, 'lobby/alert.html', {'id': id, 'alert': alert})

        gamestatus = Lobby.objects.get(id=id)
        gamestatus.game_status = 1
        gamestatus.save()
        return render(request, 'lobby/GameStart.html', {'gamestatus': gamestatus})

        round = Round.objects.create(lobby=lobby)

        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            user.profile.game_role = 0
            user.save()

        # create a werewolf
        if 3 < user_count < 7:
            user = User.objects.get(id=user_ids[0])
            user.profile.game_role = 1
            user.save()

#
# class DeleteLobby(View):
#     def get(self, request):
#         LobbyDelete = GAME_STATUS(2)
#         if LobbyDelete:
#             LobbyDelete.delete()
