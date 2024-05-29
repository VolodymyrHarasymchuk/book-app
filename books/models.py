from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    type = models.CharField(max_length=20, choices={"reader": "reader", "author": "author"})
    bio_text = models.CharField(max_length=1000)

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400)
    isbn = models.IntegerField()
    description = models.CharField(max_length=1000)
    date_pub = models.DateTimeField("book publishing date")
    date_posted = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=1)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    date_posted = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=1)
