from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Book, Review, Ratings

User = get_user_model()

class BookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(
            user=self.user,
            name='Test Book',
            isbn=1234567890,
            description='A test book description.',
            date_pub=timezone.make_aware(timezone.datetime(2023, 1, 1, 0, 0, 0)),
            image=None,
            file=None,
            rating=0,
            num_ratings=0
        )

    def test_book_creation(self):
        self.assertEqual(self.book.name, 'Test Book')
        self.assertEqual(self.book.isbn, 1234567890)
        self.assertEqual(self.book.description, 'A test book description.')
        self.assertEqual(self.book.rating, 0)
        self.assertEqual(self.book.num_ratings, 0)

    def test_submit_review(self):
        self.client.login(username='testuser', password='testpass')
        review_data = {
            'text': 'This is a test review.',
        }
        response = self.client.post(reverse('books:book_info', args=[self.book.id]), review_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(text='This is a test review.', book=self.book).exists())

    def test_rate_book(self):
        self.client.login(username='testuser', password='testpass')
        rating_data = {
            'rating': 4
        }
        response = self.client.post(reverse('books:rate_book', args=[self.book.id]), rating_data)
        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.rating, 4)
        self.assertEqual(self.book.num_ratings, 1)
