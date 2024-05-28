from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

def index(request):
    return render(request, "books/index.html")

def sign_up(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("main:index"))
    else:
        form = UserCreationForm()
    
    return render(request, "registration/sign_up.html", {"form": form})