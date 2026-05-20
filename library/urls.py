from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.news_view, name='news'),
    path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    path('news/edit/<int:news_id>/', views.news_edit_view, name='news_edit'),
    path('news/delete/<int:news_id>/', views.news_delete_view, name='news_delete'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),
    path('book/booking/<int:book_id>/', views.book_booking_view, name='book_booking'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', LoginView.as_view(template_name='library/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin_panel/', views.admin_panel_view, name='admin_panel'),
    path('admin_panel/edit/<str:username>/', views.edit_user_view, name='edit_user'),
    path('admin_panel/toggle/<str:username>/', views.toggle_user_status_view, name='toggle_user'),
    path('librarian/', views.librarian_view, name='librarian'),
    path('settings/', views.settings_view, name='settings'),
    path('reports/', views.reports_list_view, name='reports_list'),

    # Отчеты Администратора
    path('reports/admin/system-stats/', views.report_system_stats_excel, name='report_system_stats'),
    path('reports/admin/rejections/', views.report_rejections_excel, name='report_rejections'),
    path('reports/admin/staff-activity/', views.report_staff_activity_excel, name='report_staff_activity'),
    path('reports/admin/top-books/', views.report_top_books_excel, name='report_top_books'),

    # Отчеты Библиотекаря
    path('reports/librarian/booked-period/', views.report_booked_period_excel, name='report_booked_period'),
    path('reports/librarian/available-books/', views.report_available_books_excel, name='report_available_books'),
    path('reports/librarian/user-history/', views.report_user_history_excel, name='report_user_history'),
path('librarian/process/<int:booking_id>/<str:action>/', views.process_booking_view, name='process_booking'),
    path('catalog/toggle-archive/<int:book_id>/', views.toggle_archive_view, name='toggle_archive'),

    # Управление справочниками (CRUD)
    path('dictionary/delete/<str:item_type>/<int:item_id>/', views.delete_dict_item, name='delete_dict_item'),
    path('dictionary/edit/<str:item_type>/<int:item_id>/', views.edit_dict_item, name='edit_dict_item'),
path('catalog/book/add/', views.book_create_view, name='book_create'),
    path('catalog/book/edit/<int:book_id>/', views.book_edit_view, name='book_edit'),
path('catalog/favorite/<int:book_id>/', views.toggle_favorite_view, name='toggle_favorite'),
path('booking/cancel/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
]