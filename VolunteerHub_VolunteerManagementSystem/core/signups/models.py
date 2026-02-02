# File: signups/models.py
# Purpose:
#   This file defines all database tables for the project.
#   Each class becomes a table once migrations are created.
#   Adding the Post model here lets Katelyn create and view posts on the front end.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CulturalInterest(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Volunteer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=300, blank=True)
    school = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    
    # Cultural preferences for EmiExplorer
    english_level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'), 
        ('intermediate', 'Intermediate'), 
        ('advanced', 'Advanced')
    ], default='beginner', blank=True)
    cultural_interests = models.ManyToManyField(CulturalInterest, blank=True, related_name='interested_volunteers')

    # This helps the name show up nicely in the admin panel
    def __str__(self):
        return self.name


class Coordinator(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=300, blank=True)
    organization = models.CharField(max_length=200, blank=True, help_text="Organization or community group")
    active = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to="coordinator_profiles/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.organization})"


class Role(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200)
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, related_name='created_roles', null=True, blank=True)
    cultural_themes = models.ManyToManyField(CulturalInterest, blank=True)
    language_level = models.CharField(max_length=50, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner')
    task_complexity = models.CharField(max_length=50, choices=[('simple', 'Simple'), ('moderate', 'Moderate'), ('complex', 'Complex')], default='simple')

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'), 
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    enrolled_date = models.DateTimeField(default=timezone.now)
    completion_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Notes about the volunteer work")
    
    def __str__(self):
        return f"{self.volunteer.name} enrolled in {self.role.title}"


class VolunteerWorkPhoto(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='work_photos')
    image = models.ImageField(upload_to="volunteer_work_photos/")
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo for {self.enrollment.volunteer.name} - {self.enrollment.role.title}"


class Certificate(models.Model):
    user = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, null=True, blank=True, related_name='certificates')
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="Pending")
    remarks = models.TextField(blank=True)
    file = models.FileField(upload_to="certificates/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ---------------------------------------------------
# Post model for StressedSally
# ---------------------------------------------------
class Post(models.Model):
    # Title that appears in the post list
    title = models.CharField(max_length=200)

    # Main text of the post
    content = models.TextField()

    # A basic string field for author since the class does not use real accounts yet
    author = models.CharField(max_length=100, default="Anonymous")

    # Creation time so posts can be sorted and displayed in order
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional image for the post
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    # Helps with debugging and admin list readability
    def __str__(self):
        return self.title


# Import Event models from separate file
from .models_event import Event, EventShift, EventRating
from .models_request import ShiftRequest
