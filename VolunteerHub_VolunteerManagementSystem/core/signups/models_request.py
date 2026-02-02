# Models for volunteer shift requests

from django.db import models
from .models import Volunteer
from .models_event import Event, EventShift


class VolunteerRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DECLINED = "declined"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DECLINED, "Declined"),
    ]

    volunteer = models.ForeignKey(
        Volunteer,
        on_delete=models.CASCADE,
        related_name="requests"
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="requests"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    coordinator_notes = models.TextField(
        blank=True,
        null=True
    )

    missing_certificates = models.JSONField(
        blank=True,
        null=True,
        help_text="List of certificates the coordinator requires"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("volunteer", "event")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.volunteer.name} → {self.event.name} ({self.status})"


class ShiftRequest(models.Model):
    """Request from a volunteer to sign up for a specific event shift"""
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DECLINED = "declined"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DECLINED, "Declined"),
    ]

    volunteer = models.ForeignKey(
        Volunteer,
        on_delete=models.CASCADE,
        related_name="shift_requests"
    )

    shift = models.ForeignKey(
        EventShift,
        on_delete=models.CASCADE,
        related_name="requests"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    coordinator_notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("volunteer", "shift")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.volunteer.name} → {self.shift.event.name} ({self.shift.shift_date}) [{self.status}]"
