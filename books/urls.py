from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "books"

urlpatterns = [
    path("", views.index, name="index"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("upload_book/", views.upload_book, name="upload_book"),
    path("book_info/<int:book_id>/", views.book_info, name="book_info"),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path("rate_book/<int:book_id>/", views.rate_book, name="rate_book"),
    path("profile/", views.profile, name="profile"),
    path("profile/<int:user_id>/", views.profile, name="user_profile"),
    path('search/', views.search_results, name='search_results'),
    path('follow_user/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow_user/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('buy_book/<int:book_id>/', views.buy_book, name='buy_book'),
    path('purchase_success/<int:book_id>/', views.purchase_success, name='purchase_success'),
    path("logout_user/", TemplateView.as_view(template_name='registration/logout_user.html'), name='logout_user'),
]