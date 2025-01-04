from django.db import models
from users.models import User
from django.utils import timezone

class EventStatus(models.TextChoices):
    SKETCH = 'SKETCH'
    PUBLISHED = 'PUBLISHED'
    CANCELED = 'CANCELED'
    FINISHED = 'FINISHED'

class Status(models.TextChoices):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class Event(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=False, blank=False)
    location = models.CharField(max_length=255, null=False, blank=False)
    total_capacity = models.IntegerField(null=False, blank=False)
    status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.SKETCH, null=False, blank=False)
    organizer = models.ForeignKey(User, related_name='events', on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category', related_name='events')	
    created_at = models.DateTimeField(editable=False)
    last_modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.last_modified = timezone.now()
        return super(User, self).save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, null=False, blank=False)