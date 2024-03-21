import random

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
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

        try:
            lobbyid = Lobby.objects.get(lobbyId=id)
        except Lobby.DoesNotExist:
            return redirect('/lobby/')

        try:
            you = Participant.objects.get(userId=request.user.id)
        except Participant.DoesNotExist:
            you = Participant(lobbyId=lobbyid, userId=request.user)
            you.save()
        return render(request, 'lobby/lobby.html', {'lobbyid': lobbyid, "you": you})


class MainLobbyView(View):
    def get(self, request):
        lobbies = Lobby.objects.all()

        return render(request, 'lobby/main.html', {'lobbies': lobbies})


class LobbyJoinView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        participant_check = Participant.objects.filter(userId=request.user.id).exclude(lobbyId__game_status=2).count()
        participants_count = Participant.objects.filter(lobbyId=lobbyid).count()
        # print(request.user)
        try:

            if participant_check > 0:
                alert = 4
                return render(request, 'lobby/alert.html', {'alert': alert, 'lobbyid': lobbyid})

            elif participants_count > 16:
                alert = 0
                return render(request, 'lobby/alert.html', {'alert': alert, 'lobbyid': lobbyid})

            else:
                participant = Participant(userId=request.user, lobbyId=lobbyid, role=0, vote_count=0, dayvoted=False,
                                          nightvoted=False)
                participant.save()
                lobbyid.game_status = 0
                lobbyid.save()

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
        citizens = Participant.objects.filter(lobbyId=lobbyid, role=0)
        werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1)
        doctors = Participant.objects.filter(lobbyId=lobbyid, role=2)
        you = Participant.objects.get(userId=request.user.id)
        player_count = lobbyid.participants.count()
        you.ready = True
        you.save()
        for p in Participant.objects.filter(lobbyId=lobbyid, ready=False):
            print(p.userId.username)
        if player_count < 4:
            alert = 1
            return render(request, 'lobby/alert.html', {'id': id, 'alert': alert})

        lobbyid.game_cycle = 0
        lobbyid.save()
        if Participant.objects.filter(lobbyId=lobbyid, ready=False).count == 0:
            for everyone in Participant.objects.filter(lobbyId=lobbyid):
                everyone.vote_count = 0
                everyone.dayvoted = False
                everyone.nightvoted = False
                everyone.dead = False
                everyone.save()
            participants = Participant.objects.filter(lobbyId=lobbyid)

            # this code is for giving roles
            participants_list = list(participants)
            random.shuffle(participants_list)

            # Assign roles within each group of 4 participants
            for i, participant in enumerate(participants_list, start=1):
                remainder = i % 4
                if remainder == 1:
                    participant.role = 1  # Assign werewolf
                elif remainder == 2:
                    participant.role = 2  # Assign doctor
                else:
                    participant.role = 0  # Assign citizen (for remainder 0 and 3)
                participant.save()

            if lobbyid.game_status == 0:
                lobbyid.game_status = 1
                lobbyid.save()

                return render(request, 'lobby/alert.html',
                              {'lobbyid': lobbyid, "werewolves": werewolves, "doctors": doctors, "citizens": citizens})
            else:
                alert = 6
                return render(request, 'lobby/alert.html', {"alert": alert, 'lobbyid': lobbyid, "you": you})

        return render(request, 'lobby/lobby.html', {'lobbyid': lobbyid})


class DayView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        current_participant_id = 0
        werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1, dead=False).count()
        townspeople = Participant.objects.filter(lobbyId=lobbyid, dead=False, role__in=[0, 2]).count()
        List_werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1)

        for everyone in Participant.objects.filter(lobbyId=lobbyid, dead=False):
            everyone.nightvoted = False
            everyone.rescued = 0
            everyone.killed = 0
        # Participant.userId = request.user.id
        if "userid" in request.GET:
            current_participant_id += int(request.GET['userid'])

        # participant object (you)
        you = Participant.objects.get(userId=request.user.id)

        if "userid" in request.GET and not you.dayvoted:

            if you.dead:
                in_game_alert = 1
                # render a page that redirects the user away, with message, you are already dead
                return render(request, 'lobby/alert.html', {'in_game_alert': in_game_alert, 'lobbyid': lobbyid})
            you.dayvoted = True
            you.save()
            # participant object (suspect)
            current_participant = Participant.objects.get(userId=current_participant_id)
            # change the voted status after nighttime
            current_participant.vote_count += 1
            current_participant.save()
            maxcount = Participant.objects.filter(lobbyId=lobbyid).aggregate(Max("vote_count"))

            # check if everyone voted
            if Participant.objects.filter(lobbyId=lobbyid, dayvoted=False).exclude(dead=True).count() == 0:

                voted_participants = Participant.objects.filter(lobbyId=lobbyid, vote_count=maxcount['vote_count__max'])
                # checks if there is only one participant with the most votes

                if voted_participants.count() > 0:
                    soon_to_be_dead_participant = random.choice(voted_participants)
                    soon_to_be_dead_participant.dead = True
                    soon_to_be_dead_participant.save()

                    if werewolves < 1:
                        lobbyid.game_cycle = 2
                        lobbyid.save()
                        return render(request, 'lobby/TownspeopleWin.html',
                                      {"werewolves": werewolves, "townspeople": townspeople,
                                       "List_werewolves": List_werewolves})
                    elif werewolves >= townspeople:
                        lobbyid.game_cycle = 2
                        lobbyid.save()
                        return render(request, 'lobby/WerewolvesWin.html',
                                      {"werewolves": werewolves, "townspeople": townspeople,
                                       "List_werewolves": List_werewolves})
                    lobbyid.game_cycle = 1
                    lobbyid.save()
                    hasnt_voted = Participant.objects.filter(lobbyId=lobbyid, dayvoted=False, dead=False)
                    for k in Participant.objects.filter(lobbyId=lobbyid):
                        k.ready = False
                        k.save()
                        print(k.userId.username)
                        print(k.ready)
                    return render(request, 'lobby/GameStartDay.html',
                                  {"werewolves": werewolves, "townspeople": townspeople,
                                   "List_werewolves": List_werewolves,
                                   'lobbyid': lobbyid, 'Dead_participant': soon_to_be_dead_participant,
                                   "hasnt_voted": hasnt_voted})
        hasnt_voted = Participant.objects.filter(lobbyId=lobbyid, dayvoted=False, dead=False)

        return render(request, 'lobby/GameStartDay.html',
                      {"werewolves": werewolves, "townspeople": townspeople, "List_werewolves": List_werewolves,
                       'lobbyid': lobbyid, "hasnt_voted": hasnt_voted})


class NightView(View):
    def get(self, request, id):
        you = Participant.objects.get(userId=request.user.id)
        lobbyid = Lobby.objects.get(lobbyId=id)
        werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1, dead=False).count()
        townspeople = Participant.objects.filter(lobbyId=lobbyid, role__in=[0, 2], dead=False).count()
        List_werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1, )
        doctors = Participant.objects.filter(lobbyId=lobbyid, role=2, dead=False).count()

        for everyone in Participant.objects.filter(lobbyId=lobbyid, dead=False):
            everyone.dayvoted = False
            everyone.vote_count = 0
        if "action" in request.GET:
            current_participant_id = int(request.GET['userid'])
            action_id = str(request.GET['action'])
            current_participant = Participant.objects.get(userId=current_participant_id)
            if you.dead:
                night_alert = 1
                return render(request, 'lobby/alert.html', {'night_alert': night_alert, 'lobbyid': lobbyid})
            else:
                if action_id == "killed":
                    if you.role == 1 and not you.nightvoted:
                        current_participant.killed += 1
                        you.nightvoted = True
                        you.save()
                    elif you.role == 1 and you.nightvoted:
                        night_alert = 0
                        return render(request, 'lobby/alert.html', {'night_alert': night_alert, 'lobbyid': lobbyid})
                else:
                    if you.role == 2 and not you.nightvoted:
                        current_participant.rescued += 1
                        you.nightvoted = True
                        you.save()
                    elif you.role == 2 and you.nightvoted:
                        night_alert = 0
                        return render(request, 'lobby/alert.html', {'night_alert': night_alert, 'lobbyid': lobbyid})
                current_participant.save()
            counting_killed = Participant.objects.filter(lobbyId=lobbyid, killed__gt=0).aggregate(Sum('killed'))[
                                  "killed__sum"] or 0
            counting_rescued = Participant.objects.filter(lobbyId=lobbyid, rescued__gt=0).aggregate(Sum('rescued'))[
                                   "rescued__sum"] or 0
            if werewolves <= counting_killed and doctors <= counting_rescued:
                participants = Participant.objects.filter(lobbyId=lobbyid)
                for p in participants:
                    if p.killed > p.rescued:
                        p.dead = True
                    p.killed = 0
                    p.rescued = 0
                    p.save()

                if werewolves < 1:
                    lobbyid.game_cycle = 2
                    lobbyid.save()
                    return render(request, 'lobby/TownspeopleWin.html',
                                  {"werewolves": werewolves, "townspeople": townspeople,
                                   "List_werewolves": List_werewolves})
                if werewolves >= townspeople:
                    lobbyid.game_cycle = 2
                    lobbyid.save()
                    return render(request, 'lobby/WerewolvesWin.html',
                                  {"werewolves": werewolves, "townspeople": townspeople,
                                   "List_werewolves": List_werewolves})

                dead_participants = Participant.objects.filter(lobbyId=lobbyid, dead=True)
                hasnt_voted = Participant.objects.filter(lobbyId=lobbyid, nightvoted=False, dead=False)
                lobbyid.game_cycle = 0
                lobbyid.save()
                return render(request, 'lobby/GameStartNight.html',
                              {"werewolves": werewolves, "townspeople": townspeople, "List_werewolves": List_werewolves,
                               'lobbyid': lobbyid,
                               "dead_participants": dead_participants, "you": you, "hasnt_voted": hasnt_voted})
        return render(request, 'lobby/GameStartNight.html',
                      {"werewolves": werewolves, "townspeople": townspeople, "List_werewolves": List_werewolves,
                       'lobbyid': lobbyid, "you": you})


class WerewolvesView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1, dead=False).count()
        townspeople = Participant.objects.filter(lobbyId=lobbyid, role__in=[0, 2]).count()
        List_werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1,)
        lobbyid.game_status = 0
        for everyone in Participant.objects.filter(lobbyId=lobbyid):
            everyone.vote_count = 0
            everyone.dayvoted = False
            everyone.nightvoted = False
            everyone.role = 0
            everyone.ready = False
            everyone.dead = False
            everyone.save()
        return render(request, 'lobby/WerewolvesWin.html',
                      {"werewolves": werewolves, "townspeople": townspeople, "List_werewolves": List_werewolves,
                       "lobbyid": lobbyid})


class TownsPeopleView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1, dead=False).count()
        townspeople = Participant.objects.filter(lobbyId=lobbyid, role__in=[0, 2]).count()
        List_werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1)
        lobbyid.game_status = 0
        for everyone in Participant.objects.filter(lobbyId=lobbyid):
            everyone.vote_count = 0
            everyone.dayvoted = False
            everyone.nightvoted = False
            everyone.role = 0
            everyone.ready = False
            everyone.dead = False
            everyone.save()
        return render(request, 'lobby/TownspeopleWin.html',
                      {"werewolves": werewolves, "townspeople": townspeople, "List_werewolves": List_werewolves,
                       "lobbyid": lobbyid})


class CheckCycleView(View):
    def get(self, request, id):
        lobby = Lobby.objects.get(lobbyId=id)

        return HttpResponse(lobby.game_cycle)


class CheckReadyView(View):
    def get(self, request, id):
        lobby = Lobby.objects.get(lobbyId=id)
        unready = Participant.objects.filter(lobbyId=lobby, ready=False).count()
        return HttpResponse(unready)


class CheckDayView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        hasnt_voted = Participant.objects.filter(lobbyId=lobbyid, dayvoted=False, dead=False)
        listNotVoted = ""
        for n in hasnt_voted:
            listNotVoted += ", " + n.userId.username

        return HttpResponse(listNotVoted)

class ShowRoleView(View):
    def get(self, request, id):
        lobbyid = Lobby.objects.get(lobbyId=id)
        werewolves = Participant.objects.filter(lobbyId=lobbyid, role=1)
        doctors = Participant.objects.filter(lobbyId=lobbyid, role=2)
        citizens = Participant.objects.filter(lobbyId=lobbyid, role=0)
        you = Participant.objects.get(userId=request.user.id)
        return render(request, 'lobby/alert.html', {"lobbyid": lobbyid, "citizens": citizens, "doctors": doctors, "werewolves": werewolves,"role_alert": you.role})
# class DeleteLobby(View):
#     def get(self, request):
#         LobbyDelete = GAME_STATUS(2)
#         if LobbyDelete:
#             LobbyDelete.delete()
