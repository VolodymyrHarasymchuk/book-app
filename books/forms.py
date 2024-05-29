from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book, Review

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'type', 'bio_text', 'password1', 'password2')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'isbn', 'description', 'date_pub', 'image']
        widgets = {
            'date_pub': forms.DateInput(attrs={'type': 'date'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

class RatingForm(forms.Form):
    rating = forms.IntegerField(
        label='Rate the book:',
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'type': 'range', 'class': 'form-range', 'min': 1, 'max': 5})
    )