from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)


class User(AbstractUser):
    pass


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages')
    handle = models.TextField()
    message = models.TextField()
    user = models.ForeignKey(User, null=True, blank=True, default=None)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return '[{timestamp}] {handle}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': self.formatted_timestamp}


