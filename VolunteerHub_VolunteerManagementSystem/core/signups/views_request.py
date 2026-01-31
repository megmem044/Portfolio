# API endpoints for shift request management

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models_request import VolunteerRequest, ShiftRequest
from .serializers_request import VolunteerRequestSerializer, ShiftRequestSerializer
from .models import Volunteer
from .models_event import Event, EventShift


class VolunteerRequestViewSet(viewsets.ModelViewSet):
    queryset = VolunteerRequest.objects.all().order_by("-created_at")
    serializer_class = VolunteerRequestSerializer

    def get_queryset(self):
        queryset = VolunteerRequest.objects.all().order_by("-created_at")
        
        # Filter by event if provided
        event_id = self.request.query_params.get('event', None)
        if event_id is not None:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by volunteer if provided
        volunteer_id = self.request.query_params.get('volunteer', None)
        if volunteer_id is not None:
            queryset = queryset.filter(volunteer_id=volunteer_id)
        
        return queryset

    # ------------------------------------------------------------
    # Volunteer: submit a request for an event
    # ------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        volunteer_id = request.data.get("volunteer")
        event_id = request.data.get("event")

        if not volunteer_id or not event_id:
            return Response(
                {"error": "volunteer and event fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            volunteer = Volunteer.objects.get(id=volunteer_id)
            event = Event.objects.get(id=event_id)
        except (Volunteer.DoesNotExist, Event.DoesNotExist):
            return Response(
                {"error": "Volunteer or event does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prevent duplicate requests for the same event
        if VolunteerRequest.objects.filter(volunteer=volunteer, event=event).exists():
            return Response(
                {"error": "A request for this event already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        req = VolunteerRequest.objects.create(
            volunteer=volunteer,
            event=event,
        )

        serializer = self.get_serializer(req)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------
    # Coordinator: list only pending requests
    # ------------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="pending")
    def pending_requests(self, request):
        pending = VolunteerRequest.objects.filter(status="pending")
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------
    # Coordinator: approve a request
    # ------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="approve")
    def approve_request(self, request, pk=None):
        req = self.get_object()
        req.status = "approved"
        req.coordinator_notes = request.data.get("notes", "")
        req.missing_certificates = []
        req.save()
        return Response({"success": "Request approved"})

    # ------------------------------------------------------------
    # Coordinator: decline a request
    # ------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="decline")
    def decline_request(self, request, pk=None):
        req = self.get_object()
        req.status = "declined"
        req.coordinator_notes = request.data.get("notes", "")
        req.save()
        return Response({"success": "Request declined"})

    # ------------------------------------------------------------
    # Coordinator: request missing certificates from volunteer
    # ------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="require-certificates")
    def require_certificates(self, request, pk=None):
        req = self.get_object()
        certs = request.data.get("missing_certificates", [])
        if not isinstance(certs, list):
            return Response(
                {"error": "missing_certificates must be a list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        req.missing_certificates = certs
        req.status = "pending"
        req.save()
        return Response({"success": "Certificate requirements updated"})

    # ------------------------------------------------------------
    # Volunteer: view only their own requests
    # ------------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="by-volunteer")
    def requests_by_volunteer(self, request):
        volunteer_id = request.query_params.get("volunteer_id")
        if not volunteer_id:
            return Response(
                {"error": "volunteer_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        requests = VolunteerRequest.objects.filter(volunteer_id=volunteer_id)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)


class ShiftRequestViewSet(viewsets.ModelViewSet):
    """API endpoints for managing volunteer shift signup requests"""
    queryset = ShiftRequest.objects.all().order_by("-created_at")
    serializer_class = ShiftRequestSerializer

    def get_queryset(self):
        queryset = ShiftRequest.objects.all().order_by("-created_at")
        
        # Filter by shift if provided
        shift_id = self.request.query_params.get('shift', None)
        if shift_id is not None:
            queryset = queryset.filter(shift_id=shift_id)
        
        # Filter by volunteer if provided
        volunteer_id = self.request.query_params.get('volunteer', None)
        if volunteer_id is not None:
            queryset = queryset.filter(volunteer_id=volunteer_id)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Volunteer submits a request for a specific shift"""
        volunteer_id = request.data.get("volunteer")
        shift_id = request.data.get("shift")

        if not volunteer_id or not shift_id:
            return Response(
                {"error": "volunteer and shift fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            volunteer = Volunteer.objects.get(id=volunteer_id)
            shift = EventShift.objects.get(id=shift_id)
        except (Volunteer.DoesNotExist, EventShift.DoesNotExist):
            return Response(
                {"error": "Volunteer or shift does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prevent duplicate requests for the same shift
        if ShiftRequest.objects.filter(volunteer=volunteer, shift=shift).exists():
            return Response(
                {"error": "You have already requested this shift"},
                status=status.HTTP_409_CONFLICT,
            )

        req = ShiftRequest.objects.create(
            volunteer=volunteer,
            shift=shift,
        )

        serializer = self.get_serializer(req)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="pending")
    def pending_requests(self, request):
        """Get all pending shift requests"""
        pending = ShiftRequest.objects.filter(status="pending")
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_request(self, request, pk=None):
        """Coordinator approves a shift request"""
        req = self.get_object()
        req.status = "approved"
        req.coordinator_notes = request.data.get("notes", "")
        req.save()
        return Response({"success": "Request approved"})

    @action(detail=True, methods=["post"], url_path="decline")
    def decline_request(self, request, pk=None):
        """Coordinator declines a shift request"""
        req = self.get_object()
        req.status = "declined"
        req.coordinator_notes = request.data.get("notes", "")
        req.save()
        return Response({"success": "Request declined"})
