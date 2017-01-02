from allauth.account.views import LoginView
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from haikunator import Haikunator

from .models import Room, UserRoom


def about(request):
    """
    Home page
    """
    active_chats = None
    if not request.user.is_anonymous():
        active_chats = request.user.userroom_set.exclude(deleted=True).values_list('room__label', flat=True)

    return render(request, "chat/about.html", {'active_chats': active_chats, })


def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room_ = None
    while not new_room_:
        with transaction.atomic():
            label = Haikunator().haikunate()
            if Room.objects.filter(label=label).exists():
                continue
            new_room_ = Room.objects.create(label=label)
    return redirect(chat_room, label=label)


def chat_room(request, label):
    """
    Room view - show the room, with messages.
    """
    room, created = Room.objects.get_or_create(label=label)

    if not request.user.is_anonymous():
        user_room, created = UserRoom.objects.get_or_create(user_id=request.user.id, room_id=room.id)
        if not created:
            user_room.deleted = False
            user_room.save()

    messages = reversed(room.messages.order_by('-timestamp'))

    return render(request, "chat/room.html", {
        'room': room,
        'messages': messages,
        })


def leave_chat(request, label):
    """
    remove chat from your list of used rooms
    """
    user = request.user
    if user.is_anonymous():
        return redirect(reverse('about'))
    try:
        room = Room.objects.get(label=label)
        connection = UserRoom.objects.get(room=room, user=user)
    except (Room.DoesNotExist, UserRoom.DoesNotExist):
        return redirect(reverse('about'))
    with transaction.atomic():
        connection.deleted = True
        connection.save()
    return redirect(reverse('about'))


class CustomLogInView(LoginView):
    """
    override template to remove link to forget-your-password functionality
    """
    template_name = 'chat/login.html'

login = CustomLogInView.as_view()
