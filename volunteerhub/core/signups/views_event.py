# API viewsets for event management

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from .models_event import Event, EventRating, EventShift
from .models import Coordinator
from .serializers_event import EventSerializer, EventRatingSerializer, EventShiftSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for events.
    Coordinators will use this API for:
        - Creating events
        - Editing event details
        - Viewing event dashboards
        - Deleting events
        - Feeding schedule and volunteer assignment tools
    """

    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        """Override create to ensure coordinator is logged in"""
        # Check if coordinator is logged in
        coordinator_email = request.session.get('coordinator_email')
        if not coordinator_email:
            from rest_framework import status
            return Response(
                {"error": "Coordinator must be logged in to create events"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Override update to ensure coordinator is logged in"""
        # Check if coordinator is logged in
        coordinator_email = request.session.get('coordinator_email')
        if not coordinator_email:
            from rest_framework import status
            return Response(
                {"error": "Coordinator must be logged in to update events"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to ensure coordinator is logged in"""
        # Check if coordinator is logged in
        coordinator_email = request.session.get('coordinator_email')
        if not coordinator_email:
            from rest_framework import status
            return Response(
                {"error": "Coordinator must be logged in to delete events"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter events by the logged-in coordinator (for coordinators).
        For volunteers/public access, show only published events.
        """
        # Get coordinator from session
        coordinator_email = self.request.session.get('coordinator_email')
        if coordinator_email:
            # This is a coordinator - show only their events
            coordinator = Coordinator.objects.filter(email=coordinator_email).first()
            if coordinator:
                return Event.objects.filter(coordinator=coordinator).order_by("-updated_at", "-created_at")
            return Event.objects.none()
        
        # Not a coordinator - show only published events for volunteers
        queryset = Event.objects.filter(status='published').order_by("-updated_at", "-created_at")
        
        # Filter by status query parameter if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset

    def perform_create(self, serializer):
        """
        Override perform_create to automatically assign the logged-in coordinator.
        Gets coordinator from session.
        """
        # Get coordinator from session
        coordinator_email = self.request.session.get('coordinator_email')
        print(f"DEBUG: perform_create called")
        print(f"DEBUG: coordinator_email from session: {coordinator_email}")
        print(f"DEBUG: session keys: {self.request.session.keys()}")
        
        coordinator = None
        if coordinator_email:
            coordinator = Coordinator.objects.filter(email=coordinator_email).first()
            print(f"DEBUG: Found coordinator: {coordinator}")
        else:
            print(f"DEBUG: No coordinator_email in session")
        
        # Set language_level to default if not provided
        if 'language_level' not in serializer.validated_data or not serializer.validated_data['language_level']:
            serializer.validated_data['language_level'] = ''
        
        # Save with coordinator
        serializer.save(coordinator=coordinator)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        """
        Optional helper endpoint returning a compact event summary.
        Useful for dashboards that do not need full event detail.
        """

        event = self.get_object()
        data = {
            "id": event.id,
            "name": event.name,
            "start_datetime": event.start_datetime,
            "end_datetime": event.end_datetime,
            "location": event.location,
            "coordinator_id": event.coordinator_id,
            "max_volunteers": event.max_volunteers,
            "status": event.status,
        }
        return Response(data)

    @action(detail=True, methods=["patch"])
    def update_notes(self, request, pk=None):
        """
        Allows coordinators to update the notes section without
        modifying the rest of the event structure.
        """

        event = self.get_object()
        notes = request.data.get("notes")

        if notes is None:
            return Response(
                {"error": "Notes field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        event.notes = notes
        event.save()

        return Response(EventSerializer(event).data)

    @action(detail=True, methods=["get"])
    def volunteers(self, request, pk=None):
        """
        Returns all approved volunteers for a specific event.
        Used by coordinators in the schedule assignment tool.
        """
        from .models_request import VolunteerRequest
        
        event = self.get_object()
        # Get all approved volunteer requests for this event
        approved_requests = VolunteerRequest.objects.filter(
            event=event, 
            status__iexact='approved'
        )
        
        # Extract volunteer data
        volunteers_data = []
        for req in approved_requests:
            volunteers_data.append({
                'id': req.volunteer.id,
                'name': req.volunteer.name,
                'email': req.volunteer.email,
            })
        
        return Response(volunteers_data)

    @action(detail=True, methods=["get"])
    def shifts(self, request, pk=None):
        """
        Returns all shifts for a specific event.
        Used by coordinators in the schedule management interface.
        """
        event = self.get_object()
        event_shifts = event.shifts.all()
        serializer = EventShiftSerializer(event_shifts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def ratings(self, request, pk=None):
        """
        Returns all ratings and feedback for a specific event.
        Used by coordinators to review volunteer feedback.
        """

        event = self.get_object()
        ratings = event.ratings.all()
        serializer = EventRatingSerializer(ratings, many=True)
        return Response(serializer.data)


class EventShiftViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for event shifts.
    Provides API endpoints for managing shifts within events.
    """

    queryset = EventShift.objects.all()
    serializer_class = EventShiftSerializer

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Mark a shift as completed.
        Returns the shift with hours_worked.
        """
        shift = self.get_object()
        shift.completed = True
        shift.save()
        serializer = self.get_serializer(shift)
        return Response({
            "message": f"Shift marked as completed. Hours worked: {shift.hours_worked():.2f}",
            "shift": serializer.data
        })

    @action(detail=True, methods=["delete", "post"])
    def remove(self, request, pk=None):
        """
        Delete a shift and all associated shift requests.
        """
        shift = self.get_object()
        shift_id = shift.id
        shift.delete()
        return Response({"message": f"Shift {shift_id} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class EventRatingViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for event ratings.
    Allows volunteers to rate events and provide feedback.
    """

    queryset = EventRating.objects.all()
    serializer_class = EventRatingSerializer

    def get_queryset(self):
        """Filter ratings by volunteer and/or event if provided"""
        queryset = EventRating.objects.all()
        volunteer_id = self.request.query_params.get('volunteer')
        event_id = self.request.query_params.get('event')
        
        if volunteer_id:
            queryset = queryset.filter(volunteer_id=volunteer_id)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new event rating.
        Requires volunteer, event, rating, and optional comment.
        """
        return super().create(request, *args, **kwargs)
