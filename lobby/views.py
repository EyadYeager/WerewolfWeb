import asyncio

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Max, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View, generic
from django.http import HttpResponse
from celery import Celery, shared_task, result

from lobby.models import Lobby, Participant
from WerewolfWeb.settings import GAME_STATUS, GAME_ROLES


# Create your views here.
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class LobbyView(View):
    def get(self, request, id):
        # print(id)

        try:
            lobby = Lobby.objects.get(lobbyid=id)
        except Lobby.DoesNotExist:
            return redirect('/lobby/')

        return render(request, 'lobby/lobby.html', {'lobby': lobby})


class MainLobbyView(View):
    def get(self, request):
        lobbies = Lobby.objects.all()
        you = Participant.objects.get(userId=request.user.id)
        you.voted = False
        you.role = 0
        you.vote_count = 0
        you.save()
        print(you.vote_count)
        print(you.voted)
        print(you.role)

        return render(request, 'lobby/main.html', {'lobbies': lobbies})


class LobbyJoinView(View):
    def get(self, request, id):

        participants_count = Participant.objects.filter(userId=request.user.id).exclude(lobbyId__game_status=2).count()
        # print(request.user)
        try:
            lobby = Lobby.objects.get(lobbyid=id)

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
        lobbyid = Lobby.objects.get(lobbyid=id)
        player_count = lobbyid.participants.count()
        # if player_count < 3:
        #     alert = 1
        #     return render(request, 'lobby/alert.html', {'id': id, 'alert': alert})

        lobbyid.game_cycle = 0
        lobbyid.save()
        if lobbyid.game_status == 0:
            lobbyid.game_status = 1
            lobbyid.save()
            everyone = Participant.objects.filter(lobbyId=lobbyid)
            everyone.vote_count = 0
            everyone.voted = False
            everyone.role = 0
            everyone.save()

        return render(request, 'lobby/GameStartDay.html', {'lobbyid': lobbyid})

        round = Round.objects.create(lobby=lobbyid)

        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            user.profile.game_role = 0
            user.profile.game_role = 0
            user.save()

        # create a werewolf
        if 3 < user_count < 7:
            user = User.objects.get(id=user_ids[0])
            user.profile.game_role = 1
            user.save()


class DayView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyid=id)

        # Participant.userId = request.user.id
        print(request.GET['userid'])
        current_participant_id = int(request.GET['userid'])

        # participant object (you)

        you = Participant.objects.get(userId=request.user.id)

        if you.role == 3:
            in_game_alert = 1
            # render a page that redirects the user away, with message, you already have voted
            return render(request, 'lobby/alert.html', {'in_game_alert': in_game_alert, 'lobbyid': lobbyid,
                                                        'funnybutton': "<input type=\"button\">this is a funny button<\input>"})

        if you.voted:
            in_game_alert = 0
            # render a page that redirects the user away, with message, you already have voted
            return render(request, 'lobby/alert.html', {'in_game_alert': in_game_alert, 'lobbyid': lobbyid,
                                                        'funnybutton': "<input type=\"button\">this is a funny button<\input>"})
        you.voted = True
        you.save()
        # participant object (suspect)
        current_participant = Participant.objects.get(userId=current_participant_id)
        # change the voted status after nighttime
        current_participant.vote_count += 1
        print(current_participant.vote_count)
        current_participant.save()
        maxcount = Participant.objects.aggregate(Max("vote_count"))

        check_voting = Participant.objects.filter(lobbyId=lobbyid, voted=False).exclude(role=3)
        # check if everyone voted
        if check_voting.count() == 0:

            voted_participants = Participant.objects.filter(vote_count=maxcount['vote_count__max'], lobbyId=lobbyid)
            # checks if there is only one participant with the most votes
            if voted_participants.count() == 1:
                soon_to_be_dead_participant = voted_participants[0]
                soon_to_be_dead_participant.role = 3
                soon_to_be_dead_participant.save()

                lobbyid.game_cycle = 1
                lobbyid.save()
                print(soon_to_be_dead_participant.role)
                print(soon_to_be_dead_participant.userId.username)

                return render(request, 'lobby/GameStartDay.html',
                              {'lobbyid': lobbyid, 'Dead_participant': soon_to_be_dead_participant})

        return render(request, 'lobby/GameStartDay.html',
                      {'lobbyid': lobbyid})


class NightView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyid=id)
        current_participant_id = int(request.GET['userid'])
        action_id = int(request.GET['action'])
        current_participant = Participant.objects.get(userId=current_participant_id)
        if action_id == "killed":
            current_participant.killed += 1
        else:
            current_participant.rescued += 1
        current_participant.save()
        counting_killed = Participant.objects.filter(lobbyId=lobbyid, killed__gt=0).aggregate(Sum('killed'))
        counting_rescued = Participant.objects.filter(lobbyId=lobbyid, rescued__gt=0).aggregate(Sum('rescued'))
        counting_killers = Participant.objects.filter(lobbyId=lobbyid, role=1).count()
        counting_doctors = Participant.objects.filter(lobbyId=lobbyid, role=2).count()
        if counting_killers == counting_killed and counting_doctors == counting_rescued:
            participants = Participant.objects.filter(lobbyId=lobbyid)
            for p in participants:
                if p.killed > p.rescued:
                    p.role = 3
                p.killed = 0
                p.rescued = 0
                p.save()
        return render(request, 'lobby/GameStartNight.html', {'lobbyid': lobbyid})


class CheckCycleView(View):
    def get(self, request, id):
        lobby = Lobby.objects.get(lobbyid=id)

        return HttpResponse(lobby.game_cycle)

        # vote_button = Participant.vote_count.get()
        # vote_button += Participant.userId
        # vote_button += 1
        # vote_button.save()
        # print(Participant.vote_count)

#
# class DeleteLobby(View):
#     def get(self, request):
#         LobbyDelete = GAME_STATUS(2)
#         if LobbyDelete:
#             LobbyDelete.delete()
