from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    type = models.CharField(max_length=20, choices={"reader": "reader", "author": "author"})
    bio_text = models.CharField(max_length=1000, null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400)
    isbn = models.BigIntegerField()
    description = models.CharField(max_length=1000)
    date_pub = models.DateTimeField("book publishing date")
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    num_ratings = models.PositiveIntegerField(default=0)

    def add_rating(self, new_rating):
        total_rating = self.rating * self.num_ratings
        total_rating += new_rating
        self.num_ratings += 1
        self.rating = total_rating / self.num_ratings
        self.save()

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
