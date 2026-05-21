from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking


@receiver(post_save, sender=Booking)
def send_booking_notification(sender, instance, created, **kwargs):
    # Если читатель не подписан или нет e-mail — ничего не шлем
    if not instance.reader.user.email or not instance.reader.is_subscribed:
        return

    subject = 'Центральная Библиотека Мурома: Статус вашей заявки'
    message = f"Здравствуйте, {instance.reader.user.first_name}!\n\n"

    # Логика текстов в зависимости от статуса
    if instance.status == 'pending':
        message += f"Ваша заявка на книгу '{instance.book.title}' принята на рассмотрение."

    elif instance.status == 'approved':
        message += f"Ваша заявка на книгу '{instance.book.title}' одобрена!\n" \
                   f"Книга ждет вас в библиотеке. Бронь действует 3 дня.\n"
        if instance.reject_comment:
            message += f"Комментарий библиотекаря: {instance.reject_comment}"

    elif instance.status == 'completed':
        message += f"Книга '{instance.book.title}' успешно выдана вам на руки. Приятного чтения!"

    elif instance.status == 'rejected':
        message += f"К сожалению, ваша заявка на книгу '{instance.book.title}' была отклонена.\n"
        if instance.rejection_type:
            message += f"Причина: {instance.rejection_type.name}\n"
        if instance.reject_comment:
            message += f"Комментарий: {instance.reject_comment}"

    elif instance.status == 'expired':
        message += f"Внимание! Срок бронирования книги '{instance.book.title}' истек. Заявка закрыта."

    elif instance.status == 'cancelled':
        message += f"Заявка на книгу '{instance.book.title}' была успешно отменена."

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.reader.user.email], fail_silently=False)
    except Exception as e:
        print(f"Ошибка отправки почты: {e}")