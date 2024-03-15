import random

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Max, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View, generic
from django.http import HttpResponse

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
            lobby = Lobby.objects.get(lobbyId=id)
        except Lobby.DoesNotExist:
            return redirect('/lobby/')

        return render(request, 'lobby/lobby.html', {'lobby': lobby})


class MainLobbyView(View):
    def get(self, request):
        lobbies = Lobby.objects.all()

        return render(request, 'lobby/main.html', {'lobbies': lobbies})


class LobbyJoinView(View):
    def get(self, request, id):
        lobby = Lobby.objects.get(lobbyId=id)
        participant_check = Participant.objects.filter(userId=request.user.id).exclude(lobbyId__game_status=2).count()
        participants_count = Participant.objects.filter(lobbyId=lobby).count()
        # print(request.user)
        try:

            if participant_check > 0:
                alert = 4
                return render(request, 'lobby/alert.html', {'alert': alert, 'id': id})

            elif participants_count > 16:
                alert = 0
                return render(request, 'lobby/alert.html', {'alert': alert, 'id': id})

            else:
                participant = Participant(userId=request.user, lobbyId=lobby, role=0, vote_count=0, voted=False)
                lobby.game_status = 0
                lobby.save()
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

        if len(name) < 3 or len(name) > 20:
            return render(request, 'lobby/CreateLobby.html',
                          {"error": "Name should be between 3 to 20 characters long"})
        Lobby.objects.create(lobby_name=name, max_players=16, game_admin=request.user, game_status=0)
        return redirect(f'/lobby/')


class GameStart(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        # player_count = lobbyid.participants.count()
        # if player_count < 4:
        #     alert = 1
        #     return render(request, 'lobby/alert.html', {'id': id, 'alert': alert})
        lobbyid.game_cycle = 0
        lobbyid.save()
        if lobbyid.game_status == 0:
            lobbyid.game_status = 1
            lobbyid.save()
        for everyone in Participant.objects.filter(lobbyId=lobbyid):
            everyone.vote_count = 0
            everyone.voted = False
            everyone.role = 0
            everyone.dead = False
            everyone.save()
        participants = Participant.objects.filter(lobbyId=lobbyid)
        for p in participants:
            p.role = 0
            p.save()

        # this code is for giving roles
        participants_list = list(participants)
        random.shuffle(participants_list)

        # Assign roles within each group of 4 participants
        for i, participant in enumerate(participants_list, start=1):
            if i % 4 == 1:
                participant.role = 1  # Assign role 1 for the first participant in every group of 4
            elif i % 4 == 0:
                participant.role = 2  # Assign role 2 for the last participant in every group of 4
            else:
                participant.role = 0  # Assign role 0 for the rest of the participants
            participant.save()

        citizens = Participant.objects.filter(lobbyId=lobbyid, role=0)
        werewolfs = Participant.objects.filter(lobbyId=lobbyid, role=1)
        doctors = Participant.objects.filter(lobbyId=lobbyid, role=2)
        for p in Participant.objects.filter(lobbyId=lobbyid):
            print(p.userId.username, p.userId.id, p.role, p.voted, p.vote_count)

        you = Participant.objects.get(userId=request.user.id)
        if you.role == 0:
            role_alert = 0
            return render(request, 'lobby/alert.html', {"role_alert": role_alert, 'lobbyid': lobbyid, "you": you})
        if you.role == 1:
            role_alert = 1
            return render(request, 'lobby/alert.html', {"role_alert": role_alert, 'lobbyid': lobbyid, "you": you})
        if you.role == 2:
            role_alert = 2
            return render(request, 'lobby/alert.html', {"role_alert": role_alert, 'lobbyid': lobbyid, "you": you})

        return render(request, 'lobby/GameStartDay.html',
                      {'lobbyid': lobbyid, "werewolfs": werewolfs, "doctors": doctors, "citizens": citizens})


class DayView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        current_participant_id = 0
        killers = Participant.objects.filter(lobbyId=lobbyid, role=1).count()

        # Participant.userId = request.user.id
        # print(request.GET['userid'])
        if "userid" in request.GET:
            current_participant_id += int(request.GET['userid'])

        # participant object (you)
        you = Participant.objects.get(userId=request.user.id)

        for p in Participant.objects.filter(lobbyId=lobbyid):
            print(p.userId.username, p.userId.id, p.role, p.voted, p.vote_count)

        if you.dead:
            in_game_alert = 1
            # render a page that redirects the user away, with message, you already have voted
            return render(request, 'lobby/alert.html', {'in_game_alert': in_game_alert, 'lobbyid': lobbyid,
                                                        'funnybutton': "<input type=\"button\">this is a funny button<\input>"})
        if "userid" in request.GET and not you.voted:

            you.voted = True
            you.save()
            # participant object (suspect)
            print("Current_participant_id")
            print(current_participant_id)
            current_participant = Participant.objects.get(userId=current_participant_id)
            # change the voted status after nighttime
            current_participant.vote_count += 1
            print("current_participant.vote_count")
            print(current_participant.vote_count)
            current_participant.save()
            maxcount = Participant.objects.filter(lobbyId=lobbyid).aggregate(Max("vote_count"))

            # check if everyone voted
            if Participant.objects.filter(lobbyId=lobbyid, voted=False).exclude(dead=True).count() == 0:

                voted_participants = Participant.objects.filter(lobbyId=lobbyid, vote_count=maxcount['vote_count__max'])
                # checks if there is only one participant with the most votes
                print(voted_participants.count())
                print(maxcount)
                if voted_participants.count() > 0:
                    print("work plz")
                    soon_to_be_dead_participant = random.choice(voted_participants)
                    soon_to_be_dead_participant.dead = True
                    soon_to_be_dead_participant.save()

                    lobbyid.game_cycle = 1
                    lobbyid.save()

                    killers = Participant.objects.filter(lobbyId=lobbyid, role=1, dead=False).count()
                    townspeople = Participant.objects.filter(lobbyId=lobbyid, dead=False, role__in=[0, 2]).count()
                    werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1)
                    if killers.count() < 1 or killers.count() >= townspeople:
                        lobbyid.game_cycle = 2
                        lobbyid.save()
                        return render(request, 'lobby/GameEnd.html', {"killers": killers, "townspeople": townspeople, "werewolves":werewolves})

                    return render(request, 'lobby/GameStartDay.html',
                                  {'lobbyid': lobbyid, 'Dead_participant': soon_to_be_dead_participant})

        return render(request, 'lobby/GameStartDay.html',
                      {'lobbyid': lobbyid})


class NightView(View):
    def get(self, request, id):
        you = Participant.objects.get(userId=request.user.id)
        lobbyid = Lobby.objects.get(lobbyId=id)
        if "action" in request.GET:
            current_participant_id = int(request.GET['userid'])
            action_id = str(request.GET['action'])
            current_participant = Participant.objects.get(userId=current_participant_id)
            if action_id == "killed":
                if you.role == 1:
                    current_participant.killed += 1
            else:
                if you.role == 2:
                    current_participant.rescued += 1
            current_participant.save()
            counting_killed = Participant.objects.filter(lobbyId=lobbyid, killed__gt=0).aggregate(Sum('killed'))[
                                  "killed__sum"] or 0
            counting_rescued = Participant.objects.filter(lobbyId=lobbyid, rescued__gt=0).aggregate(Sum('rescued'))[
                                   "rescued__sum"] or 0
            counting_killers = Participant.objects.filter(lobbyId=lobbyid, role=1).count()
            counting_doctors = Participant.objects.filter(lobbyId=lobbyid, role=2).count()
            if counting_killers <= counting_killed and counting_doctors <= counting_rescued:
                participants = Participant.objects.filter(lobbyId=lobbyid)
                for p in participants:
                    if p.killed > p.rescued:
                        p.dead=True
                    p.killed = 0
                    p.rescued = 0
                    p.save()

            killers = Participant.objects.filter(lobbyId=lobbyid, role=1,dead=False).count()
            townspeople = Participant.objects.filter(lobbyId=lobbyid, role__in=[0, 2], dead=False).count()
            werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1,)
            if killers.count() < 1 or killers.count() >= townspeople:
                lobbyid.game_cycle = 2
                lobbyid.save()
                return render(request, 'lobby/GameEnd.html', {"killers": killers, "townspeople": townspeople, "werewolves":werewolves})
        dead_participants = Participant.objects.filter(lobbyId=lobbyid, dead=True)

        you = Participant.objects.get(userId=request.user.id)
        print(Participant.objects.filter(lobbyId=lobbyid, dead=True).count())
        lobbyid.game_cycle = 0
        return render(request, 'lobby/GameStartNight.html',
                      {'lobbyid': lobbyid, "dead_participants": dead_participants, "you": you})


class EndView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        killers = Participant.objects.filter(lobbyId=lobbyid, role=1).count()
        townspeople = Participant.objects.filter(lobbyId=lobbyid, role__in=[0, 2]).count()
        werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1,)
        return render(request, 'lobby/GameEnd.html', {"killers": killers, "townspeople": townspeople, "werewolves":werewolves})


class CheckCycleView(View):
    def get(self, request, id):
        lobby = Lobby.objects.get(lobbyId=id)

        return HttpResponse(lobby.game_cycle)

#
# class DeleteLobby(View):
#     def get(self, request):
#         LobbyDelete = GAME_STATUS(2)
#         if LobbyDelete:
#             LobbyDelete.delete()
