from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, Booking, Reader
from .models import News, LibraryInfo

def catalog_view(request):
    # Динамический выбор активных книг из базы данных
    books = Book.objects.filter(is_archived=False)

    # Обработка поискового запроса
    query = request.GET.get('q')
    if query:
        books = books.filter(title__icontains=query) | books.filter(authors__last_name__icontains=query)

    return render(request, 'library/catalog.html', {'books': books})


def book_detail_view(request, book_id):
    # Получение подробной информации о книге
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'library/book_detail.html', {'book': book})


# Функция динамического ввода новой заявки на бронирование
@login_required
def book_booking_view(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_id)

        # Получаем профиль читателя текущего пользователя
        # Если пользователь - не читатель (например, админ), бронирование "запрещено"
        try:
            reader = request.user.reader_profile
        except:
            messages.error(request, "Бронирование доступно только читателям")
            return redirect('library:catalog')

        # Проверка бизнес-правила: не более 5 активных броней
        active_bookings = Booking.objects.filter(
            reader=reader,
            status__in=['pending', 'approved']
        ).count()

        if active_bookings < 5:
            # Динамический ввод записи в базу данных
            Booking.objects.create(reader=reader, book=book, status='pending')
            messages.success(request, f"Заявка на книгу '{book.title}' успешно создана!")
        else:
            messages.error(request, "Достигнут лимит: нельзя иметь более 5 активных заявок")

    return redirect('library:catalog')


# Функция динамического вывода ленты новостей
def news_view(request):
    # Получаем все новости, отсортированные по дате (свежие сверху)
    news_list = News.objects.all().order_by('-publish_date')

    # Передаем данные в шаблон
    return render(request, 'library/news.html', {'news': news_list})


# Страница "О нас" с динамической статистикой
def about_view(request):
    # Получаем единственную запись с настройками
    info = LibraryInfo.objects.first()

    # Считаем данные для блока статистики
    stats = {
        'total_books': Book.objects.filter(is_archived=False).count(),
        'active_bookings': Booking.objects.filter(status__in=['pending', 'approved']).count(),
        'completed_bookings': Booking.objects.filter(status='completed').count(),
    }

    return render(request, 'library/about.html', {
        'info': info,
        'stats': stats
    })
# Функция динамического вывода личного кабинета пользователя
@login_required
def profile_view(request):
    # Позже мы добавим сюда логику статистики, а пока просто открываем страницу
    return render(request, 'library/profile.html')

# Страница "Контакты"
def contacts_view(request):
    info = LibraryInfo.objects.first()
    return render(request, 'library/contacts.html', {'info': info})

# Функция динамического вывода полной статьи новости
def news_detail_view(request, news_id):
    # Получаем конкретную новость или выдаем 404, если её нет
    item = get_object_or_404(News, pk=news_id)
    return render(request, 'library/news_detail.html', {'item': item})