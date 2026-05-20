from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Reader, Author, Genre, Publisher, Book, Booking, News, LibraryInfo, RejectionReason


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):  # Наследуемся от обычного ModelAdmin
    list_display = ('username', 'last_name', 'first_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'last_name')

    # Это позволит редактировать поля, но создание пароля теперь будет ручным
    fields = ('username', 'password', 'last_name', 'first_name', 'middle_name', 'email', 'phone', 'role', 'is_active',
              'is_staff', 'is_superuser')

    def save_model(self, request, obj, form, change):
        # Эта магия нужна, чтобы пароль зашифровался, а не сохранился текстом
        if obj.password and not obj.password.startswith('pbkdf2_'):
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'last_name', 'first_name', 'role', 'is_active', 'is_staff')
#     list_filter = ('role', 'is_active', 'is_staff')
#     search_fields = ('username', 'last_name', 'phone')
#
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Персональная информация', {'fields': ('first_name', 'last_name', 'middle_name', 'email', 'phone')}),
#         ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role')}),
#         ('Даты', {'fields': ('last_login', 'date_joined')}),
#     )

    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('username', 'password', 'first_name', 'last_name', 'role', 'is_active'),
    #     }),
    # )


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'user')
    search_fields = ('ticket_number', 'user__username', 'user__last_name')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date')
    search_fields = ('last_name', 'first_name')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'publish_year', 'issue_type', 'is_archived')
    list_filter = ('issue_type', 'is_archived', 'genres')
    search_fields = ('title', 'isbn', 'authors__last_name')
    filter_horizontal = ('authors', 'genres')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'reader', 'status', 'booking_date')
    list_filter = ('status', 'booking_date')
    search_fields = ('book__title', 'reader__username')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'author')
    list_filter = ('publish_date',)
    search_fields = ('title', 'short_description')

@admin.register(RejectionReason)
class RejectionReasonAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(LibraryInfo)
class LibraryInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)