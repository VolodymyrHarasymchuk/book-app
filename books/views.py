from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import author_required
from .models import Book, Review
from .forms import CustomUserCreationForm, BookForm

def index(request):
    latest_books_list = Book.objects.order_by("date_posted")[:5]
    context = { "latest_books_list": latest_books_list }
    return render(request, "books/index.html", context)

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

def book_info(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    latest_reviews_list = Review.objects.filter(book_id=book_id).order_by("-date_posted")[:5]
    return render(request, "books/book_info.html", {"book": book, "latest_reviews_list": latest_reviews_list})

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