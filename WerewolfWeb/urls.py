"""
URL configuration for WerewolfWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from lobby.views import *
from main.views import MainView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('', MainView.as_view()),
    path('lobby/<int:id>/', LobbyView.as_view(), name='lobby'),
    path('lobby/', MainLobbyView.as_view(), name='mainlobby'),
    path('lobby/<int:id>/join/', LobbyJoinView.as_view(), name='lobby'),
    path('lobby/<int:id>/leave/', LobbyLeaveView.as_view(), name='lobby'),
    path('lobby/CreateLobby/', LobbyCreateView.as_view(), name='name'),
    path('lobby/<int:id>/gamestart/', GameStart.as_view(), name='start'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('lobby/<int:id>/gamestart/day/', DayView.as_view(), name='day'),
    path('lobby/<int:id>/gamestart/night/', NightView.as_view(), name='night'),
    path('lobby/<int:id>/gamestart/check/', CheckCycleView.as_view(), name='check'),
    path('lobby/<int:id>/gamestart/end/', EndView.as_view(), name='end'),

]
