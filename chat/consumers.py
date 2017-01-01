import re
import json
import logging
from channels import Group
from .models import Room
from channels.auth import channel_session_user, channel_session_user_from_http


log = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some other sort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefix, label = message['path'].strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug('chat connect room=%s client=%s:%s',
              room.label, message['client'][0], message['client'][1])

    Group('chat-' + label, channel_layer=message.channel_layer).add(message.reply_channel)

    data = {}
    user_name = message.user.username if message.user.is_authenticated() else 'Anonymous User'
    data['message'] = "{} has entered the room".format(user_name)
    data['handle'] = "SystemMessage"
    m = room.messages.create(**data)
    Group('chat-' + label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})

    message.channel_session['room'] = room.label


@channel_session_user
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, but room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", message['text'])
        return

    if not message.user.is_anonymous():
        data['user_id'] = message.user.id
        data['handle'] = message.user.username

    if data:
        log.debug('chat message room=%s handle=%s message=%s',
                  room.label, data['handle'], data['message'])
        m = room.messages.create(**data)

        # See above for the note about Group
        Group('chat-' + label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})


@channel_session_user
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        data = {}
        user_name = message.user.username if message.user.is_authenticated() else 'Anonymous User'
        data['message'] = "{} has left the room".format(user_name)
        data['handle'] = "SystemMessage"
        m = room.messages.create(**data)
        Group('chat-' + label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})
        Group('chat-' + label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        pass
