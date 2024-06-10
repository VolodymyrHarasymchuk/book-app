from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .decorators import author_required
from .models import Book, Review, Ratings, User, Purchase
from .forms import CustomUserCreationForm, BookForm, ReviewForm, RatingForm, BookSearchForm, EditProfileForm, UserSearchForm
import stripe
import logging

logger = logging.getLogger(__name__)

def index(request):
    latest_books_list = Book.objects.order_by("-date_posted")[:8]
    form = BookSearchForm()
    form2 = UserSearchForm()
    return render(request, "books/index.html", { "latest_books_list": latest_books_list, "form": form, "form2": form2})

def search_results(request):
    query = request.GET.get('query')
    if query:
        books = Book.objects.filter(Q(name__icontains=query) | Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
    else:
        books = Book.objects.all()
    form = BookSearchForm()
    return render(request, 'books/search_results.html', {'books': books, 'query': query, "form": form})

def search_results_users(request):
    query = request.GET.get('query')
    if query:
        users = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    else:
        users = User.objects.all()
    form = UserSearchForm()
    return render(request, 'books/search_results_users.html', {'users': users, 'query': query, "form": form})

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
    rated = False

    if request.user.is_authenticated:
        rated = Ratings.objects.filter(user=request.user, book=book).exists()


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
        rating_form = RatingForm()
    
    return render(request, "books/book_info.html", {
        "book": book, 
        "latest_reviews_list": latest_reviews_list, 
        "form": form,
        "rating_form": rating_form,
        "rated": rated,
    })

@login_required
def rate_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if Ratings.objects.filter(user=request.user, book=book).exists():
        return HttpResponseRedirect(reverse("books:book_info", args=[book_id]))
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['rating']
            book.add_rating(int(rating_value))
            Ratings.objects.create(user=request.user, book=book, rating=rating_value)
            return HttpResponseRedirect(reverse("books:book_info", args=[book_id]))
    else:
        form = RatingForm()
    return render(request, 'books/book_info.html', {'form': form, 'book': book})

def profile(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    return render(request, 'books/profile.html', {'user': user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('books:profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'books/edit_profile.html', {'form': form})

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

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow != request.user:
        request.user.following.add(user_to_follow)
    return redirect('books:user_profile', user_id=user_id)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    if user_to_unfollow != request.user:
        request.user.following.remove(user_to_unfollow)
    return redirect('books:user_profile', user_id=user_id)

def list_followers(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    followers = user.followers.all()

    return render(request, "books/list_followers.html", { "followers": followers})

def list_following(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    following = user.following.all()

    return render(request, "books/list_followers.html", { "followers": following})

def buy_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': book.name,
                    },
                    'unit_amount': int(book.price * 100),  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('books:purchase_success', args=[book.id])),
            cancel_url=request.build_absolute_uri(reverse('books:buy_book', args=[book.id])),
        )

        Purchase.objects.create(
            user=request.user,
            book=book,
            amount=book.price,
        )

        return redirect(session.url, code=303)

    return render(request, 'books/buy_book.html', {'book': book, 'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY})

def purchase_success(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/purchase_success.html', {
        'book': book
    })