from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from book_app import settings

class User(AbstractUser):
    type = models.CharField(max_length=20, choices={"reader": "reader", "author": "author"})
    bio_text = models.CharField(max_length=1000, null=True, blank=True)
    image = models.ImageField(upload_to="images/pfps/", default="/images/pfps/pfp.jpg")
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    
    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400)
    isbn = models.BigIntegerField()
    description = models.CharField(max_length=1000)
    date_pub = models.DateTimeField("book publishing date")
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    watermarked_file = models.FileField(upload_to='watermarked_files/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    num_ratings = models.PositiveIntegerField(default=0)
    copyright_notice = models.CharField(max_length=500, default="© Author Name. All rights reserved.")

    def add_rating(self, new_rating):
        total_rating = self.rating * self.num_ratings
        total_rating += new_rating
        self.num_ratings += 1
        self.rating = total_rating / self.num_ratings
        self.save()

    def __str__(self):
        return self.name 

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    date_posted = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=1)

class Ratings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    date_rated = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'book')

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.user} bought {self.book} for ${self.amount}'
    
class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    description = models.TextField()
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report by {self.user.username} on {self.book.name}'
    
class BookList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    books = models.ManyToManyField(Book, blank=True)

    def __str__(self):
        return f'{self.name} by {self.user.username}'
    
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]