from django.db import models
from django.utils.text import slugify
from django.forms import ValidationError
from users.models import User
from django.utils import timezone


class Event(models.Model):
    class EventStatusChoices(models.TextChoices):
        SKETCH = 'SKETCH', 'Sketch'
        PUBLISHED = 'PUBLISHED', 'Published'
        CANCELED = 'CANCELED', 'Canceled'
        FINISHED = 'FINISHED', 'Finished'

    title = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(null=False, blank=False)
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=False, blank=False)
    location = models.CharField(max_length=255, null=False, blank=False)
    total_capacity = models.IntegerField(null=False, blank=False)
    event_status = models.CharField(max_length=20, choices=EventStatusChoices.choices, default=EventStatusChoices.SKETCH, null=False, blank=False)
    organizer = models.ForeignKey(User, related_name='events', on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category', related_name='events')	
    created_at = models.DateTimeField(editable=False)
    last_modified = models.DateTimeField()

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError('The start date must be before the end date')       
        if self.total_capacity < 1:
            raise ValidationError('The total capacity must be greater than zero')
        
    def save(self, *args, **kwargs):
        self.clean()
        self.last_modified = timezone.now()
        if not self.id:
            self.created_at = self.last_modified
        if not self.slug:
            self.slug = slugify(self.title)
        return super(Event, self).save(*args, **kwargs)

class Category(models.Model):
    class CategoryStatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE'
        INACTIVE = 'INACTIVE'

    name = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    category_status = models.CharField(max_length=20, choices=CategoryStatusChoices.choices, default=CategoryStatusChoices.ACTIVE, null=False, blank=False)