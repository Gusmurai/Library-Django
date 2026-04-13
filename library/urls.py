from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.news_view, name='news'),
path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),
    path('book/booking/<int:book_id>/', views.book_booking_view, name='book_booking'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', LoginView.as_view(template_name='library/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]