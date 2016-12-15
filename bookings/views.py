from datetime import datetime, timezone, date, timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import csrf
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_time

from bookings.models import Booking, Schedule, Record
from emailer.views import send_email


def home(request):
    if request.user.groups.filter(name="Administrators").exists() \
            or request.user.groups.filter(name="Soundmans").exists():
        return redirect('/staff')
    return render(request, "bookings/home.html")


def about(request):
    if request.user.groups.filter(name="Administrators").exists() \
            or request.user.groups.filter(name="Soundmans").exists():
        return redirect('/staff')
    return render(request, "bookings/about.html")


@login_required
def show_soundmans(request):
    group = Group.objects.get(name="Soundmans")
    soundmans = group.user_set.all()

    if request.user.groups.filter(name='Customers').exists():
        context = {
            'soundmans': soundmans
        }
        return render(request, "bookings/show_soundmans.html", context)

    return redirect('/staff')


# solution for the bug
__date_for_booking = ""


@login_required
def show_calendar(request, soundman_id):
    return render(request, 'bookings/show_calendar.html')


@login_required
def show_schedule(request, soundman_id):
    args = {}
    context = {}
    args.update(csrf(request))
    soundman = get_object_or_404(User, id=soundman_id)
    schedules = Schedule.objects.all().filter(soundman=soundman)
    if request.method == "POST":
        bookings = Booking.objects.all().filter(schedule__soundman=soundman)
        datestr = request.POST['date']
        act_bookings = []
        today_schedule = []
        date = parse_date(datestr)
        global __date_for_booking
        __date_for_booking = date

        if date is not None:
            for schedule in schedules:
                if date.isoweekday() == schedule.working_day:
                    today_schedule.append(schedule)
                for booking in bookings:
                    if schedule == booking.schedule:
                        if booking.is_active == 1:
                            if booking.date == date:
                                act_bookings.append(booking)
                            context = {
                                'soundman': soundman,
                                'schedules': schedules,
                                'bookings': bookings,
                                'active_bookings': act_bookings,
                                'date': date,
                            }
        if date < datetime.today().date():
            today_schedule = None
            context['error'] = "На предыдущую дату невозможно создать бронь"
            return render(request, 'bookings/show_calendar.html', context)
        if request.user.groups.filter(name='Customers').exists():
            context['today_schedule'] = today_schedule
            return render(request, 'bookings/show_calendar.html', context)
        else:
            context['error'] = "Вы не являетесь клиентом системы,вы не имеете права создавать бронь"
            return render(request, 'bookings/show_calendar.html', context)


@login_required
def create_booking(request, soundman_id):
    args = {}
    args.update(csrf(request))
    context = {}
    new_booking = []
    soundman = get_object_or_404(User, id=soundman_id)
    if request.method == "POST":
        start = request.POST['start']
        end = request.POST['end']
        try:
            datetime.strptime(start, '%H:%M')
            datetime.strptime(end, '%H:%M')
        except ValueError:
            return HttpResponse("You are not so smart though")

        date = __date_for_booking
        schedule = Schedule.objects.all().filter(soundman=soundman, working_day=date.isoweekday()).first()
        user = request.user
        bookings = Booking.objects.all().filter(date=date, schedule=schedule,
                                                is_active=1)  # Лист всех активных броней на текущую дату

        new_booking = Booking(user=user, start=start, end=end, is_active=1, date=date,
                              schedule=schedule)
        flag = False
        start_time = parse_time(start)
        deltastart = timedelta(hours=start_time.hour, minutes=start_time.minute)
        end_time = parse_time(end)
        deltaend = timedelta(hours=end_time.hour, minutes=end_time.minute)
        delta = deltaend - deltastart

        for book in bookings:
            print(flag)
            if book.start <= parse_time(start) and book.end >= parse_time(end):
                flag = True
            if book.start >= parse_time(start) and book.end <= parse_time(end):
                flag = True
            if book.start <= parse_time(start) and book.end <= parse_time(end) and book.end >= parse_time(start):
                flag = True
            if book.start >= parse_time(start) and book.end >= parse_time(end) and book.start <= parse_time(end):
                flag = True

    if parse_time(start) < schedule.start_of_the_day or parse_time(end) > schedule.end_of_the_day or parse_time(
            start) > schedule.end_of_the_day or parse_time(end) < schedule.start_of_the_day:
        # for books in bookings:
        # ToDo: Надо сделать проверку в цикле времен создаваемой брони с временами активных броней других пользователей
        context['error'] = "Вы выбрали время, не совпадающее с временем работы звукорежиссера"
        return render(request, 'bookings/show_calendar.html', context)

    elif parse_time(start) >= parse_time(end):
        context['error'] = "Начало записи не может быть больше или равно концу записи"
        return render(request, 'bookings/show_calendar.html', context)
    elif flag:
        context['error'] = "На это время имеются брони"
        return render(request, 'bookings/show_calendar.html', context)
    elif delta < timedelta(minutes=30):
        context['error'] = "Минимальная подолжительность записи 30 минут"
        return render(request, 'bookings/show_calendar.html', context)

    else:
        new_booking.save()
        context['new_booking'] = new_booking
        context['duration'] = delta
        return render(request, 'bookings/show_calendar.html', context)


class RecordView:
    @permission_required("bookings.change_record", raise_exception=True)
    def details(self, booking_id):
        context = {
            'id': booking_id
        }
        date_booking = Booking.objects.get(pk=booking_id).date
        if not date_booking == datetime.now().date():
            if date_booking < datetime.now().date():
                _reservation = Booking.objects.get(pk=booking_id)
                _reservation.is_active = 3
                _reservation.save()
            return HttpResponse(
                "Сегодня не день брони! Бронь будет действительна %s"
                % Booking.objects.get(pk=booking_id).date
            )
        return render(self, "records/user_record_page.html", context)

    @permission_required("bookings.change_record", raise_exception=True)
    def start_record_method(self, booking_id):
        if self.POST:
            args = {}
            args.update(csrf(self))
            # reservationId = request.POST['id']
            try:
                # Если статус брони = "отменен" / "завершен" то выбросит ошибку
                if Booking.objects.get(pk=booking_id).is_active == 4 \
                        or Booking.objects.get(pk=booking_id).is_active == 5:
                    return HttpResponse("Бронь отменена или уже завершена!")

                # Если начало записи уже есть в БД то выбросит сообщение, что запись уже начата
                elif Record.objects.get(reservation_id=booking_id).start_record is not None:
                    return HttpResponse("Запись уже начата!")

                # Проверка опоздал ли пользоватеь или нет
                elif (datetime.now(timezone.utc) - Booking.objects.get(pk=booking_id).start) > timedelta(minutes=15):
                    return HttpResponse("Пользователь опоздал!")

            except ObjectDoesNotExist:
                # Проверка опоздал ли пользоватеь или нет
                if datetime.combine(date.min, datetime.now().time()) - datetime.combine(
                        date.min, Booking.objects.get(
                            pk=booking_id
                        ).start) > timedelta(minutes=15):
                    return HttpResponse("Пользователь опоздал!")

                _new_record = Record(reservation_id=booking_id, start_record=datetime.now(timezone.utc))
                _new_record.save()

                _reservation = Booking.objects.get(pk=booking_id)
                _reservation.is_active = 2
                _reservation.save()
                return HttpResponse('Запись началась!')

        return HttpResponse('Запись началась!')

    @permission_required("bookings.change_record", raise_exception=True)
    def stop_record_method(self, booking_id):
        if self.POST:
            args = {}
            args.update(csrf(self))
            try:
                # Если статус брони = "отменен" / "завершен" то выбросит ошибку
                if Booking.objects.get(pk=booking_id).is_active == 3 \
                        or Booking.objects.get(pk=booking_id).is_active == 4:
                    return HttpResponse("Бронь отменена или запись уже заверщена!")

                if Record.objects.get(reservation_id=booking_id).stop_record is None:
                    _new_record = Record.objects.get(reservation_id=booking_id)
                    _new_record.stop_record = datetime.now(timezone.utc)

                    # duration is in minutes
                    duration = (_new_record.stop_record - _new_record.start_record).seconds / 60
                    price_per_minute = 100  # ToDO: Указать цену

                    if duration > 5:
                        _new_record.money_back = duration * price_per_minute
                    else:
                        _new_record.money_back = 0

                    _new_record.save()

                    _reservation = Booking.objects.get(pk=booking_id)
                    _reservation.is_active = 5
                    _reservation.save()
                    return HttpResponse("Запись остановлена!")

                else:
                    return HttpResponse("Запись уже остановлена!")

            except ObjectDoesNotExist:
                return HttpResponse("Запись даже не начиналась")


def cancel_booking(request, booking_id):
    booking_object = Booking.objects.get(id=booking_id)
    booking_object.is_active = 4
    booking_object.save()
    emailSoundman = booking_object.schedule.soundman.email
    emailUser = booking_object.user.email
    send_email(type='cancel', emailUser=emailUser, emailSoundman=emailSoundman)
    if request.user.groups.filter(name="Customers").exists():
        return redirect('/accounts/my_profile')
    return redirect('/staff/profile')
