from django import forms
from django.core.validators import RegexValidator

from .models import User, Reader, LibraryInfo, News, Author, Genre, Publisher, RejectionReason, Book
import re

# Валидатор: только буквы (русские/английские), пробелы и дефис
letters_only = RegexValidator(
    regex=r'^[а-яА-ЯёЁa-zA-Z\s-]+$',
    message='Разрешены только буквы, пробелы и дефис'
)


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    ticket_number = forms.CharField(required=False, label="Номер читательского билета")
    is_subscribed = forms.BooleanField(required=False, label="Подписка на уведомления")
    email = forms.EmailField(required=False, label="E-mail (необязательно)")
    phone = forms.CharField(required=False, label="Телефон (необязательно)")

    class Meta:
        model = User
        fields = ['username', 'password', 'last_name', 'first_name', 'middle_name', 'email', 'phone', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Обрабатываем None и пустые значения
        if email is None:
            return ''
        email = str(email).strip()
        if not email:
            return ''

        # Проверяем уникальность
        if User.objects.filter(email=email).exclude(email='').exists():
            raise forms.ValidationError("Этот электронный адрес уже используется.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Обрабатываем None и пустые значения
        if phone is None:
            return ''
        phone = str(phone).strip()
        if not phone:
            return ''

        # Очищаем телефон от лишних символов
        phone_clean = re.sub(r'[^\d+]', '', phone)

        if not re.match(r'^\+7\d{10}$', phone_clean):
            raise forms.ValidationError("Формат телефона: +7XXXXXXXXXX (например, +79001234567)")
        return phone_clean

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Этот логин уже занят.")
        return username

    def clean_ticket_number(self):
        ticket = self.cleaned_data.get('ticket_number')
        if ticket is None:
            ticket = ''
        else:
            ticket = str(ticket).strip()

        role = self.cleaned_data.get('role')
        if role == 'reader' or not role:
            if not ticket:
                raise forms.ValidationError("Для читателя номер билета обязателен.")
            if Reader.objects.filter(ticket_number=ticket).exists():
                raise forms.ValidationError("Этот номер билета уже занят.")
        return ticket


class UserEditForm(forms.ModelForm):
    ticket_number = forms.CharField(required=False, label="Номер читательского билета")
    is_subscribed = forms.BooleanField(required=False, label="Подписка на уведомления")

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'middle_name', 'username', 'email', 'phone', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(
                attrs={'readonly': 'readonly', 'style': 'background-color: #f0f0f0; cursor: not-allowed;'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@mail.ru'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'role' in self.fields:
            # 1. Снимаем обязательность, чтобы форма не падала, если поле не пришло в POST
            self.fields['role'].required = False

            # 2. Если редактируем читателя -> делаем поле скрытым (библиотекарь не должен его менять)
            if self.instance.pk and self.instance.role == 'reader':
                self.fields['role'].widget = forms.HiddenInput()

            # 3. Если редактируем сотрудника -> убираем из выбора роль "читатель"
            elif self.instance.pk:
                current_choices = self.fields['role'].choices
                self.fields['role'].choices = [c for c in current_choices if c[0] != 'reader']

    def clean_role(self):
        role = self.cleaned_data.get('role')
        # Если роль не пришла (библиотекарь скрыл поле) или пустая -> возвращаем старую роль из БД
        if not role:
            return self.instance.role
        return role

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is None: return ''
        email = str(email).strip()
        if not email: return ''

        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exclude(email='').exists():
            raise forms.ValidationError("Этот электронный адрес уже используется.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone is None: return ''
        phone = str(phone).strip()
        if not phone: return ''

        phone_clean = re.sub(r'[^\d+]', '', phone)
        if not re.match(r'^\+7\d{10}$', phone_clean):
            raise forms.ValidationError("Формат телефона: +7XXXXXXXXXX")
        return phone_clean

    def clean_username(self):
        return self.instance.username

    def clean_ticket_number(self):
        ticket = self.cleaned_data.get('ticket_number')
        if ticket is None:
            ticket = ''
        else:
            ticket = str(ticket).strip()

        # Запрещаем менять номер билета!
        if self.instance.pk and hasattr(self.instance, 'reader_profile'):
            old_ticket = self.instance.reader_profile.ticket_number
            if ticket != old_ticket:
                raise forms.ValidationError(
                    "Номер читательского билета нельзя изменить. "
                )

        if self.instance.role == 'reader':
            if not ticket:
                raise forms.ValidationError("Для читателя номер билета обязателен.")
            # Проверяем уникальность, исключая текущего читателя
            if Reader.objects.filter(ticket_number=ticket).exclude(user=self.instance).exists():
                raise forms.ValidationError("Этот номер билета уже занят.")
        return ticket
class LibraryInfoForm(forms.ModelForm):
    class Meta:
        model = LibraryInfo
        fields = ['name', 'description', 'address', 'phone', 'email', 'schedule', 'map_code']
        labels = {
            'name': 'Название библиотеки',
            'description': 'Описание (для раздела "О нас")',
            'address': 'Физический адрес',
            'phone': 'Контактный телефон',
            'email': 'Электронная почта',
            'schedule': 'Режим работы (поддерживается Markdown)',
            'map_code': 'HTML-код Яндекс/Google карты (iframe)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'schedule': forms.Textarea(attrs={'rows': 4}),
            'map_code': forms.Textarea(attrs={'rows': 4, 'placeholder': '<iframe src="..."></iframe>'}),
        }

    # Валидация телефона
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+7\d{10}$', phone):
            raise forms.ValidationError("Формат телефона: +7xxxxxxxxxx (без пробелов)")
        return phone

    # Валидация кода карты
    def clean_map_code(self):
        map_code = self.cleaned_data.get('map_code')
        # Проверяем, что если код ввели, он содержит тег <iframe>
        if map_code and '<iframe' not in map_code.lower():
            raise forms.ValidationError("Код карты должен содержать тег <iframe>. Скопируйте его из Яндекс или Google Карт.")
        return map_code
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'short_description', 'full_description', 'image']
        labels = {
            'title': 'Заголовок',
            'short_description': 'Краткое описание (для ленты)',
            'full_description': 'Полный текст',
            'image': 'Изображение',
        }



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields =['last_name', 'first_name', 'middle_name', 'username', 'phone', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем логин неизменяемым для всех пользователей
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].help_text = "Логин нельзя изменить."
class ChangePasswordForm(forms.Form):
    # Делаем все поля необязательными в форме (required=False)
    old_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль", required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, label="Новый пароль", required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Подтвердите новый пароль", required=False)

    def clean(self):
        cleaned_data = super().clean()
        old = cleaned_data.get("old_password")
        new = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")

        # Если пользователь заполнил ХОТЯ БЫ ОДНО поле пароля, требуем остальные
        if old or new or confirm:
            if not old or not new or not confirm:
                raise forms.ValidationError("Для смены пароля необходимо заполнить все три поля.")
            if new != confirm:
                raise forms.ValidationError("Новые пароли не совпадают.")
        return cleaned_data


class AuthorForm(forms.ModelForm):
    last_name = forms.CharField(label='Фамилия', validators=[letters_only],
                                widget=forms.TextInput(attrs={'class': 'form-input'}))
    first_name = forms.CharField(label='Имя', validators=[letters_only],
                                 widget=forms.TextInput(attrs={'class': 'form-input'}))
    middle_name = forms.CharField(label='Отчество', required=False, validators=[letters_only],
                                  widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Author
        fields = ['last_name', 'first_name', 'middle_name', 'birth_date']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})}


class GenreForm(forms.ModelForm):
    name = forms.CharField(label='Название жанра', validators=[letters_only],
                           widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Genre
        fields = ['name']


class PublisherForm(forms.ModelForm):
    name = forms.CharField(label='Название издательства',
                           widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Publisher
        fields = ['name']

class RejectionReasonForm(forms.ModelForm):
    name = forms.CharField(label='Название причины', validators=[letters_only], widget=forms.TextInput(attrs={'class': 'form-input'}))
    class Meta:
        model = RejectionReason
        fields = ['name']

# === ФОРМА КНИГИ ===
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields =['isbn', 'title', 'publish_year', 'description', 'cover_image', 'issue_type', 'is_archived', 'publisher', 'authors', 'genres']
        widgets = {
            'isbn': forms.TextInput(attrs={
                'class': 'form-input',
                'maxlength': '13',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '')",
            }),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'publish_year': forms.NumberInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'issue_type': forms.Select(attrs={'class': 'form-input'}),
            #'publisher': forms.Select(attrs={'class': 'form-input'}),
            'authors': forms.SelectMultiple(attrs={'class': 'select2-field'}),
            'genres': forms.SelectMultiple(attrs={'class': 'select2-field'}),
            'publisher': forms.Select(attrs={'class': 'select2-field'}),
        }

# library/forms.py

class AdminSetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Подтвердите пароль")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("new_password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data