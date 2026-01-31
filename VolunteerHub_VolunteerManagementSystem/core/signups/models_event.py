# Models for events, shifts, and event ratings

from django.db import models
from django.utils import timezone
from .models import Coordinator, CulturalInterest  # Coordinator lives in models.py


class Event(models.Model):
    """
    Represents a volunteer event created by a coordinator.
    Coordinators can later review volunteer requests, assign shifts,
    track attendance, and add feedback.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    # Basic details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Scheduling — allow null during migration, enforce later
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=250)

    # Coordinator — allow null during migration, enforce later
    coordinator = models.ForeignKey(
        Coordinator,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True,
    )

    # Capacity
    max_volunteers = models.PositiveIntegerField(default=1)

    # Status workflow
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    notes = models.TextField(blank=True)

    # Language level requirement for volunteers
    language_level = models.CharField(
        max_length=50,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        blank=True,
        default=''
    )

    # Certificate requirements
    requires_first_aid = models.BooleanField(default=False)
    requires_food_safety = models.BooleanField(default=False)

    # Cultural interests associated with this event
    cultural_interests = models.ManyToManyField(
        CulturalInterest,
        blank=True,
        related_name='events'
    )

    # Archival + timestamps
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.start_datetime:%Y-%m-%d})" if self.start_datetime else self.name


class EventShift(models.Model):
    """
    Represents a specific shift within an event.
    Coordinators specify multiple shifts when creating an event.
    Each shift has a date, start/end time, and volunteer capacity.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="shifts"
    )
    
    shift_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    volunteers_needed = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=200, blank=True)
    completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['shift_date', 'start_time']
    
    def __str__(self):
        return f"{self.event.name} - {self.shift_date} {self.start_time}-{self.end_time}"
    
    def hours_worked(self):
        """Calculate hours worked between start and end time"""
        from datetime import datetime, date
        # Ensure shift_date is a date object
        if isinstance(self.shift_date, str):
            shift_date = datetime.strptime(self.shift_date, '%Y-%m-%d').date()
        else:
            shift_date = self.shift_date
        
        start = datetime.combine(shift_date, self.start_time)
        end = datetime.combine(shift_date, self.end_time)
        duration = end - start
        return duration.total_seconds() / 3600


class EventRating(models.Model):
    """
    Volunteer feedback and rating for a completed event/shift.
    """
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    volunteer = models.ForeignKey(
        'Volunteer',
        on_delete=models.CASCADE,
        related_name='event_ratings'
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('volunteer', 'event')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.volunteer.name} rated {self.event.name} - {self.rating} stars"
