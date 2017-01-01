from django.db import transaction
from django.shortcuts import render, redirect
from haikunator import Haikunator
from .models import Room, UserRoom
from django.urls import reverse


def about(request):
    if not request.user.is_anonymous():
        active_chats = request.user.userroom_set.exclude(deleted=True).values_list('room__label', flat=True)

    return render(request, "chat/about.html", {'active_chats': active_chats, })


def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room = None
    while not new_room:
        with transaction.atomic():
            label = Haikunator().haikunate()
            if Room.objects.filter(label=label).exists():
                continue
            new_room = Room.objects.create(label=label)
    return redirect(chat_room, label=label)


def chat_room(request, label):
    """
    Room view - show the room, with latest messages.
    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    if not request.user.is_anonymous():
        user_room, created = UserRoom.objects.get_or_create(user_id=request.user.id, room_id=room.id)
        if not created:
            user_room.deleted = False
            user_room.save()

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "chat/room.html", {
        'room': room,
        'messages': messages,
})


def leave_chat(request, label):
    user = request.user
    try:
        room = Room.objects.get(label=label)
        connection = UserRoom.objects.get(room=room, user=user)
    except (Room.DoesNotExist, UserRoom.DoesNotExist):
        return redirect(reverse('about'))
    with transaction.atomic():
        connection.deleted = True
        connection.save()
    return redirect(reverse('about'))

