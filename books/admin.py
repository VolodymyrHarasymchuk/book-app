from django.contrib import admin

from .models import User, Book, Review, Purchase, BookList, Ratings

class BookAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "date_posted"]

admin.site.register(User)
admin.site.register(Book, BookAdmin)
admin.site.register(Review)
admin.site.register(Purchase)
admin.site.register(BookList)
admin.site.register(Ratings)