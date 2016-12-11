from django.core import mail
from django.shortcuts import render_to_response

from RecordStudio import settings


def send_email(**kwargs):
    args = {}
    subject = ""
    message = ""
    email = ""
    # Send welcome mail
    if kwargs['type'] == "register":
        subject = "Успешная регистрация"
        email = kwargs['email']
        username = kwargs['username']
        __hash_code = kwargs['hash_code']
        message = "http://recordstudio.pythonanywhere.com/accounts/confirm?username=%s&hash=%s" \
                  % (username, __hash_code)
        args['register'] = "Вы успешно зарегистрировались на сайте. Осталось подтвердить email"

    elif kwargs['type'] == 'newsoundman':
        subject = "Добро пожаловать"
        email = kwargs['email']
        username = kwargs['username']
        password = kwargs['password']
        message = "Добро пожаловать в команду RecordStudio! Ваш логин и пароль для входа в профиль: %s %s " % \
                  (username, password)

    # resend email
    elif kwargs['type'] == 'resend':
        subject = "Повторное подтверждение почты"
        username = kwargs['username']
        email = kwargs['email']
        hash_code = kwargs['hash_code']
        message = "http://recordstudio.pythonanywhere.com/accounts/confirm?username=%s&hash=%s" % (username, hash_code)
        args['resent'] = "Ссылка для потдверждения почты была отправлена на вашу почту"

    # Send forget password mail
    elif kwargs['type'] == "forgetPassword":
        subject = "Восстановление пароля"
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']
        message = "Your data: " + username + " " + password
        args['forget'] = "Ваш новый пароль успешно отправлен на Ваш email"

    elif kwargs['type'] == 'cancel':
        subject = "Отмена брони"
        message = "Ваша бронь была отменена."
        email = kwargs['emailUser'], kwargs['emailSoundman']

    try:
        mail.send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
        return render_to_response("emailer/successful_page.html", args)
    except Exception:
        args['email_error'] = "Ошибка при отправке письма на email"
        return render_to_response("emailer/successful_page.html", args)
