from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


# 1. ПОЛЬЗОВАТЕЛИ И ЧИТАТЕЛИ

class User(AbstractUser):
    ROLE_CHOICES = [
        ('reader', 'Читатель'),
        ('librarian', 'Библиотекарь'),
        ('admin', 'Администратор'),
    ]

    username = models.CharField('Логин', max_length=50, primary_key=True, unique=True)
    middle_name = models.CharField('Отчество', max_length=50, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='reader')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"


class Reader(models.Model):
    ticket_number = models.CharField('Номер читательского билета', max_length=20, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reader_profile',
                                verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Профиль читателя'
        verbose_name_plural = 'Профили читателей'

    def __str__(self):
        return f"Билет №{self.ticket_number} - {self.user.last_name}"


# 2. СПРАВОЧНИКИ

class Author(models.Model):
    last_name = models.CharField('Фамилия', max_length=50)
    first_name = models.CharField('Имя', max_length=50)
    middle_name = models.CharField('Отчество', max_length=50, blank=True, null=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        unique_together = ['last_name', 'first_name', 'middle_name', 'birth_date']

    def __str__(self):
        # Если отчество есть, выводим три слова, если нет — два
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField('Название издательства', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'

    def __str__(self):
        return self.name


# 3. КАТАЛОГ КНИГ

class Book(models.Model):
    ISSUE_CHOICES = [
        ('home', 'На дом'),
        ('reading_room', 'Только в читальном зале'),
    ]

    isbn = models.CharField('ISBN', max_length=20, blank=True, null=True)
    title = models.CharField('Название', max_length=255)
    publish_year = models.IntegerField('Год издания', blank=True, null=True)
    description = models.TextField('Аннотация')
    cover_image = models.ImageField('Обложка', upload_to='books/', blank=True, null=True)
    issue_type = models.CharField('Тип выдачи', max_length=20, choices=ISSUE_CHOICES, default='home')
    is_archived = models.BooleanField('В архиве', default=False)

    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, null=True, blank=True,
                                  verbose_name='Издательство')
    authors = models.ManyToManyField(Author, verbose_name='Авторы', blank=True)
    genres = models.ManyToManyField(Genre, verbose_name='Жанры')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return self.title


# 4. БРОНИРОВАНИЯ И ИНФОРМАЦИЯ

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
        ('completed', 'Выдана'),
        ('expired', 'Истекла'),
        ('cancelled', 'Отменена'),
    ]

    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, verbose_name='Читатель')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    librarian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='processed_bookings', verbose_name='Обработал(а)')

    booking_date = models.DateTimeField('Дата бронирования', auto_now_add=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    status_change_date = models.DateTimeField('Дата изменения статуса', auto_now=True)
    reject_reason = models.TextField('Причина отказа', blank=True, null=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self):
        return f"Заявка #{self.id} - {self.book.title}"


class News(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    publish_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    short_description = models.TextField('Краткое описание')
    full_description = models.TextField('Полный текст')
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Опубликовал')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title


class LibraryInfo(models.Model):
    name = models.CharField('Название библиотеки', max_length=255)
    description = models.TextField('Описание (О нас)')
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    schedule = models.TextField('Режим работы')
    map_code = models.TextField('Код карты', blank=True, null=True)
    admin = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Последний редактор')

    class Meta:
        verbose_name = 'Настройки библиотеки'
        verbose_name_plural = 'Настройки библиотеки'

    def clean(self):
        if LibraryInfo.objects.exists() and not self.pk:
            raise ValidationError("Можно создать только одну запись настроек.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name