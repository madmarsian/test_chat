from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)
    members = models.ManyToManyField(User, through='UserRoom')


class UserRoom(models.Model):
    user = models.ForeignKey(User)
    room = models.ForeignKey(Room)
    deleted = models.BooleanField(default=False)


class Message(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, default=None, related_name='messages')
    room = models.ForeignKey(Room, related_name='messages')
    handle = models.TextField(blank=True, null=True, default=None, max_length=20)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return '[{timestamp}] {handle}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': self.formatted_timestamp}
