# Serializers for event models

from rest_framework import serializers
from .models_event import Event, EventShift, EventRating
from .models import CulturalInterest


class EventSerializer(serializers.ModelSerializer):
    """
    Serializes event objects for API usage.
    Includes all coordinator-facing fields required for event creation,
    editing, dashboards, and scheduling.
    """

    coordinator_name = serializers.SerializerMethodField()
    cultural_interests = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CulturalInterest.objects.all()
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "start_datetime",
            "end_datetime",
            "location",
            "coordinator_name",
            "max_volunteers",
            "status",
            "notes",
            "language_level",
            "is_active",
            "created_at",
            "updated_at",
            "requires_first_aid",
            "requires_food_safety",
            "cultural_interests",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_coordinator_name(self, obj):
        """Return coordinator name or empty string if no coordinator assigned"""
        if obj.coordinator:
            return obj.coordinator.name
        return ""


class EventShiftSerializer(serializers.ModelSerializer):
    """
    Serializes EventShift objects for API usage.
    """
    volunteer_names = serializers.SerializerMethodField()
    hours_worked = serializers.SerializerMethodField()

    class Meta:
        model = EventShift
        fields = [
            "id",
            "event",
            "shift_date",
            "start_time",
            "end_time",
            "volunteers_needed",
            "description",
            "volunteer_names",
            "completed",
            "hours_worked",
        ]

    def get_volunteer_names(self, obj):
        """Return volunteer name assigned to this shift"""
        from .models import ShiftRequest
        requests = ShiftRequest.objects.filter(shift=obj)
        if requests.exists():
            return requests.first().volunteer.name
        return "Unassigned"

    def get_hours_worked(self, obj):
        """Calculate and return hours worked for this shift"""
        return round(obj.hours_worked(), 2)


class EventRatingSerializer(serializers.ModelSerializer):
    """
    Serializes EventRating objects for API usage.
    """
    
    volunteer_name = serializers.CharField(
        source="volunteer.name",
        read_only=True
    )
    
    event_name = serializers.CharField(
        source="event.name",
        read_only=True
    )
    
    rating_display = serializers.CharField(
        source="get_rating_display",
        read_only=True
    )

    class Meta:
        model = EventRating
        fields = [
            "id",
            "volunteer",
            "volunteer_name",
            "event",
            "event_name",
            "rating",
            "rating_display",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
