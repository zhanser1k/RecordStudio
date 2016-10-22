from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import auth
from bookings.models import Reservation
import datetime
from pytimeparse.timeparse import timeparse


def home(request):
    # soundman = User.objects.filter(groups='soundman')

    group = Group.objects.get(name='soundmans')
    users = group.user_set.all()
    context = {
        'sounmanlist': users
    }
    print(users)
    return render(request, 'bookings/create_booking.html',context)


def create_booking(request):
    duration = request.POST['duration']
    start = request.POST['start']
    soundman = request.POST['soundman']
    print(start)
    print(soundman)
    
    user = request.user
    new_booking = Reservation(user=user, start=start, is_active=1,
                              duration=datetime.timedelta(minutes=timeparse(duration)),
                              soundman=request.user)
    new_booking.save()
    reserv = Reservation.objects.all()
    context = {
        'bookings': new_booking
    }
    return render(request, 'bookings/show_booking.html', context)
