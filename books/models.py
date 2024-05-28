from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    type = models.CharField(max_length=20)
    bio_text = models.CharField(max_length=1000)

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400)
    isbn = models.IntegerField()
    description = models.CharField(max_length=1000)
    date_pub = models.DateTimeField("book publishing date")
    rating = models.IntegerField(default=1)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    date_pub = models.DateTimeField("review publishing date")
    rating = models.IntegerField(default=1)
