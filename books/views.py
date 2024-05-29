from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import author_required
from .models import Book
from .forms import CustomUserCreationForm, BookForm

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

@login_required
@author_required
def upload_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            return HttpResponseRedirect(reverse("books:index"))
    else:
        form = BookForm()
    return render(request, 'books/upload_book.html', {'form': form})