from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .decorators import author_required
from .models import Book, Review, Ratings, User, Purchase, BookList
from .forms import CustomUserCreationForm, BookForm, ReviewForm, RatingForm, BookSearchForm, EditProfileForm, UserSearchForm, ReportForm, BookListForm
import stripe
import logging
import PyPDF2
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
import io

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
    
    book_lists = BookList.objects.filter(user=user)
    return render(request, 'books/profile.html', {'user': user, 'book_lists': book_lists})

@login_required
def create_book_list(request):
    search_query = request.GET.get('search', '')
    books = Book.objects.all()

    if search_query:
        books = books.filter(Q(name__icontains=search_query) | Q(user__first_name__icontains=search_query) | Q(user__last_name__icontains=search_query))

    if request.method == 'POST':
        form = BookListForm(request.POST)
        if form.is_valid():
            book_list = form.save(commit=False)
            book_list.user = request.user
            book_list.save()
            form.save_m2m()  # Save the many-to-many data for the form
            return redirect('profile')  # Redirect to the profile page or any other page you prefer
    else:
        form = BookListForm()

    form.fields['books'].queryset = books  # Update the queryset for the books field

    return render(request, 'books/create_book_list.html', {'form': form, 'search_query': search_query})

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
                    'currency': 'uah',
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

def create_text_watermark(text, filename):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create a canvas and set font
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set smaller font size
    c.setFont("Helvetica", 20)
    
    # Create a semi-transparent color (alpha value between 0 and 1)
    semi_transparent_gray = Color(0.5, 0.5, 0.5, alpha=0.3)
    c.setFillColor(semi_transparent_gray)
    
    c.saveState()
    c.translate(300, 50)
    c.rotate(45)
    
    # Draw the watermark text
    c.drawString(0, 0, text)
    c.restoreState()
    c.showPage()
    c.save()

    # Write the PDF data to the buffer
    with open(filename, 'wb') as f:
        f.write(buffer.getvalue())

    buffer.close()

def add_text_watermark(input_pdf, output_pdf, watermark_text):
    # Create watermark PDF with text
    watermark_pdf = "text_watermark.pdf"
    create_text_watermark(watermark_text, watermark_pdf)

    # Read the watermark PDF
    watermark = PyPDF2.PdfReader(watermark_pdf)
    watermark_page = watermark.pages[0]
    
    # Read the original PDF
    pdf_reader = PyPDF2.PdfReader(input_pdf)
    pdf_writer = PyPDF2.PdfWriter()

    # Add watermark to each page
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    
    # Write out the watermarked PDF
    with open(output_pdf, 'wb') as out:
        pdf_writer.write(out)

@receiver(post_save, sender=Book)
def create_watermark(sender, instance, **kwargs):
    if instance.file and not instance.watermarked_file:
        original_path = instance.file.path
        watermarked_dir = os.path.join('media', 'watermarked_files')
        os.makedirs(watermarked_dir, exist_ok=True)
        watermarked_path = os.path.join(watermarked_dir, f'watermarked_{os.path.basename(original_path)}')
        
        add_text_watermark(original_path, watermarked_path, instance.copyright_notice)
        
        instance.watermarked_file.name = os.path.relpath(watermarked_path, 'media')
        instance.save()

@login_required
def download_watermarked_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    file_path = os.path.join(settings.MEDIA_ROOT, book.watermarked_file.name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    else:
        return HttpResponseNotFound("The requested file was not found.")
    
@login_required
def report_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.book = book
            report.save()
            return redirect('books:book_info', book_id=book_id)
    else:
        form = ReportForm()
    
    return render(request, 'books/report_book.html', {'form': form, 'book': book})