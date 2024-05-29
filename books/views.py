from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from .models import Book
from .forms import CustomUserCreationForm

def index(request):
#    latest_question_list = Book.objects.filter(pub_date__lte=timezone.now()).exclude(choice__isnull=True).order_by("pub_date")
#    context = { "latest_question_list": latest_question_list }
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