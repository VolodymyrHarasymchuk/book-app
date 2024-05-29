from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'type', 'bio_text', 'password1', 'password2')

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'isbn', 'description', 'date_pub', 'image']