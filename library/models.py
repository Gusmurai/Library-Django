from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
isbn_validator = RegexValidator(
    regex=r'^\d{13}$',
    message="ISBN должен состоять ровно из 13 цифр."
)
phone_regex = RegexValidator(
    regex=r'^\+7\d{10}$',
    message="Телефон должен быть в формате: +7XXXXXXXXXX"
)

# Для ФИО: только русские буквы, дефисы и пробелы
cyrillic_regex = RegexValidator(
    regex=r'^[а-яёА-ЯЁ\s-]+$',
    message="Разрешены только русские буквы"
)
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

    # Применяем валидатор кириллицы к полям ФИО
    last_name = models.CharField('Фамилия', max_length=50, validators=[cyrillic_regex])
    first_name = models.CharField('Имя', max_length=50, validators=[cyrillic_regex])
    middle_name = models.CharField('Отчество', max_length=50, blank=True, null=True, validators=[cyrillic_regex])

    # Применяем валидатор телефона
    phone = models.CharField('Телефон', max_length=12, blank=True, null=True, validators=[phone_regex])

    # EmailField в Django уже имеет встроенную проверку формата почты
    # Уберите unique=True у email или используйте unique_together с условием
    email = models.EmailField('Email', blank=True, null=True)  # Убрали unique=True

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"


class Reader(models.Model):
    ticket_number = models.CharField('Номер читательского билета', unique=True, max_length=20, primary_key=True, error_messages={
            'unique': "В базе данных уже есть есть читатель с этим номером билета."
        })
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reader_profile',
                                verbose_name='Пользователь')
    is_subscribed = models.BooleanField('Подписка на уведомления', default=False)

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
        constraints = [
            models.UniqueConstraint(
                fields=['last_name', 'first_name', 'middle_name', 'birth_date'],
                name='unique_author_constraint',
                violation_error_message='Автор уже есть в базе данных.'
            )
        ]

    def __str__(self):
        # Если отчество есть, выводим три слова, если нет — два
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=50, unique=True, error_messages={
            'unique': "Жанр с таким названием уже есть в базе данных."
        } )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField('Название издательства', max_length=100, unique=True, error_messages={
            'unique': "Издательство с таким названием уже есть в базе данных."
        })

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'

    def __str__(self):
        return self.name


# 3. КАТАЛОГ КНИГ

class Book(models.Model):
    ISSUE_CHOICES = [
        ('home', 'На дом/Читальный зал'),
        ('reading_room', 'Только читальный зал'),
    ]

    isbn = models.CharField('ISBN', validators=[isbn_validator],  max_length=13, unique=True, blank=True, null=True, help_text="Введите 13 цифр без пробелов и тире", error_messages={
            'unique': "Книга с таким ISBN уже есть в базе данных."
        } )
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

    @property
    def formatted_isbn(self):
        if self.isbn and len(self.isbn) == 13:
            return f"{self.isbn[:3]}-{self.isbn[3:4]}-{self.isbn[4:9]}-{self.isbn[9:12]}-{self.isbn[12:]}"
        return self.isbn

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return self.title

class RejectionReason(models.Model):
    name = models.CharField(
        'Причина отказа',
        max_length=255,
        unique=True, # Запрещаем дубликаты
        error_messages={
            'unique': "Такая причина уже существует в справочнике."
        }
    )

    class Meta:
        verbose_name = 'Причина отказа'
        verbose_name_plural = 'Причины отказов'

    def __str__(self):
        return self.name
# 4. БРОНИРОВАНИЯ И ИНФОРМАЦИЯ

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
        ('completed', 'Завершена'), # завершена
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
    rejection_type = models.ForeignKey(RejectionReason, on_delete=models.PROTECT, null=True, blank=True,
                                       verbose_name='Причина отказа')
    # Можно оставить и текстовое поле для доп. комментария:
    reject_comment = models.TextField('Комментарий библиотекаря', blank=True, null=True)

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

# library/models.py

class Favorite(models.Model):
    # Теперь привязываем строго к Читателю (Reader)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='favorites', verbose_name='Читатель')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favored_by', verbose_name='Книга')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('reader', 'book')

    def __str__(self):
        return f"{self.reader.ticket_number} - {self.book.title}"