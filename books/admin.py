from django.contrib import admin

from .models import User, Book, Review

class BookAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "date_posted"]

admin.site.register(User)
admin.site.register(Book, BookAdmin)
admin.site.register(Review)