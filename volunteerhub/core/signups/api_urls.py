# File: signups/api_urls.py
# Purpose:
# Central router for all API endpoints.
# Every API viewset is registered here so Django builds the URLs automatically.
# This keeps routing simple and avoids manual paths everywhere.

from rest_framework.routers import DefaultRouter

from .views import (
    VolunteerViewSet,
    CoordinatorViewSet,
    CertificateViewSet,
    RoleViewSet,
    EnrollmentViewSet,
    CulturalInterestViewSet,
    PostViewSet,
    VolunteerWorkPhotoViewSet,
)

from .views_event import EventViewSet, EventShiftViewSet, EventRatingViewSet
from .views_request import VolunteerRequestViewSet, ShiftRequestViewSet

router = DefaultRouter()

# Volunteers and summary endpoint
router.register(r"volunteers", VolunteerViewSet, basename="volunteers")

# Events API
router.register(r"events", EventViewSet, basename="events")

# Event Shifts API
router.register(r"event-shifts", EventShiftViewSet, basename="event-shifts")

# Event Ratings API
router.register(r"event-ratings", EventRatingViewSet, basename="event-ratings")

# Coordinators API
router.register(r"coordinators", CoordinatorViewSet, basename="coordinators")

# Certificates API
router.register(r"certificates", CertificateViewSet, basename="certificates")

# Roles API
router.register(r"roles", RoleViewSet, basename="roles")

# Enrollments API
router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")

# Cultural interests
router.register(r"interests", CulturalInterestViewSet, basename="interests")

# Posts for StressedSally and general announcements
router.register(r"posts", PostViewSet, basename="posts")

# Volunteer work photos
router.register(r"volunteer-work-photos", VolunteerWorkPhotoViewSet, basename="volunteer-work-photos")

# Volunteer requests
router.register(r"volunteer-requests", VolunteerRequestViewSet, basename="volunteer-requests")

# Shift requests
router.register(r"shift-requests", ShiftRequestViewSet, basename="shift-requests")

urlpatterns = router.urls
