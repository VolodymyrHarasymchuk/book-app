from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm

def index(request):
    return render(request, "books/index.html")

def sign_up(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("books:index"))
    else:
        form = CustomUserCreationForm()
    
    return render(request, "registration/sign_up.html", {"form": form})