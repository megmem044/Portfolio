# Serializers for shift request models

from rest_framework import serializers
from .models_request import VolunteerRequest, ShiftRequest
from .models import Volunteer
from .models_event import Event, EventShift


class VolunteerRequestSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.CharField(
        source="volunteer.name",
        read_only=True
    )

    volunteer_email = serializers.CharField(
        source="volunteer.email",
        read_only=True
    )

    volunteer_id = serializers.IntegerField(
        source="volunteer.id",
        read_only=True
    )

    event_name = serializers.CharField(
        source="event.name",
        read_only=True
    )

    class Meta:
        model = VolunteerRequest
        fields = [
            "id",
            "volunteer",
            "volunteer_id",
            "volunteer_name",
            "volunteer_email",
            "event",
            "event_name",
            "status",
            "coordinator_notes",
            "missing_certificates",
            "created_at",
            "updated_at",
        ]


class ShiftRequestSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.CharField(
        source="volunteer.name",
        read_only=True
    )

    volunteer_email = serializers.CharField(
        source="volunteer.email",
        read_only=True
    )

    event = serializers.IntegerField(
        source="shift.event.id",
        read_only=True
    )

    event_name = serializers.CharField(
        source="shift.event.name",
        read_only=True
    )

    shift_date = serializers.DateField(
        source="shift.shift_date",
        read_only=True
    )

    shift_start = serializers.TimeField(
        source="shift.start_time",
        read_only=True
    )

    shift_end = serializers.TimeField(
        source="shift.end_time",
        read_only=True
    )

    class Meta:
        model = ShiftRequest
        fields = [
            "id",
            "volunteer",
            "volunteer_name",
            "volunteer_email",
            "shift",
            "event",
            "event_name",
            "shift_date",
            "shift_start",
            "shift_end",
            "status",
            "coordinator_notes",
            "created_at",
            "updated_at",
        ]
