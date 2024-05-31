from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .decorators import author_required
from .models import Book, Review
from .forms import CustomUserCreationForm, BookForm, ReviewForm, RatingForm, BookSearchForm

def index(request):
    latest_books_list = Book.objects.order_by("date_posted")[:8]
    form = BookSearchForm()
    return render(request, "books/index.html", { "latest_books_list": latest_books_list, "form": form})

def search_results(request):
    query = request.GET.get('query')
    if query:
        books = Book.objects.filter(Q(name__icontains=query) | Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
    else:
        books = Book.objects.all()
    form = BookSearchForm()
    return render(request, 'books/search_results.html', {'books': books, 'query': query, "form": form})

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
    latest_reviews_list = Review.objects.filter(book_id=book_id).order_by("-date_posted")[:10]

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            return HttpResponseRedirect(reverse("books:book_info", args=[book_id]))
    else:
        form = ReviewForm()
    
    return render(request, "books/book_info.html", {"book": book, "latest_reviews_list": latest_reviews_list, "form": form})

def profile(request):
    return render(request, "books/profile.html")

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

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user == request.user:
        review.delete()
    return redirect('books:book_info', book_id=review.book.id)

def rate_book(request, book_id):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            book = get_object_or_404(Book, pk=book_id)
            book.add_rating(int(rating))
            return HttpResponseRedirect(reverse("books:book_info", args=[book_id]))
    else:
        form = RatingForm()
    return render(request, 'books/index.html')