from django.shortcuts import render, redirect
from django.views import View


# Create your views here.

class MainView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/lobby/')
        return render(request, 'main/index.html')
