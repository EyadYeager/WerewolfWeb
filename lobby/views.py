from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View, generic

from lobby.models import Lobby, Participant
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
        print(request.user.id)

        return render(request, 'lobby/main.html', {'lobbies': lobbies})


class LobbyJoinView(View):
    def get(self, request, id):
        user = request.user
        alert = 2

        participants_count = Participant.objects.filter(userId=request.user.id).exclude(lobbyId__game_status=2).count()
        print(request.user)
        try:
            lobby = Lobby.objects.get(id=id)

            if participants_count > 0:
                alert = 4
                return render(request, 'lobby/alert.html', {'alert': alert, 'id': id})

            else:
                participant = Participant(userId=request.user, lobbyId=lobby, role=0, vote_count=0)
                participant.save()

        except Lobby.DoesNotExist:
            redirect('/lobby/')
        return redirect(f'/lobby/{id}/')


class LobbyLeaveView(View):
    def get(self, request, id):
        user = request.user
        participants = Participant.objects.filter(userId=request.user.id).exclude(lobbyId__game_status=2).all()

        try:
            for l in participants:
                l.delete()

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
        Lobby.objects.create(lobby_name=name, max_players=10, game_admin=request.user, game_status=0)
        return redirect(f'/lobby/')


class GameStart(View):
    def get(self, request, id):
        game = Lobby.objects.get(id=id)
        player_count = game.participants.count()
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
