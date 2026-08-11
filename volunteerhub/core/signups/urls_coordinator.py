# URL routing for coordinator pages

from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.coordinator_signup_page, name="coordinator-signup"),
    path("signin/", views.coordinator_signin_page, name="coordinator-signin"),
    path("dashboard/", views.coordinator_dashboard_page, name="coordinator-dashboard"),
    path("profile/", views.coordinator_profile_page, name="coordinator-profile"),

    # NEW — event list page
    path("events/", views.coordinator_event_list_page, name="coordinator-event-list"),

    # Event CRUD routes
    path("events/create/", views.coordinator_event_create_page, name="coordinator-event-create"),
    path("events/<int:event_id>/manage/", views.coordinator_event_manage_page, name="coordinator-event-manage"),
    path("events/<int:event_id>/signups/", views.coordinator_event_signups_page, name="coordinator-event-signups"),
    path("events/<int:event_id>/edit/", views.coordinator_event_edit_page, name="coordinator-event-edit"),
    path("events/<int:event_id>/delete/", views.coordinator_event_delete_page, name="coordinator-event-delete"),
    path("events/<int:event_id>/details/", views.coordinator_event_details_page, name="coordinator-event-details"),
    path("events/<int:event_id>/dashboard/", views.coordinator_event_dashboard_page, name="coordinator-event-dashboard"),
    path("events/<int:event_id>/schedule/", views.coordinator_event_schedule_page, name="coordinator-event-schedule"),
    path("events/<int:event_id>/feedback/", views.coordinator_event_feedback_page, name="coordinator-event-feedback"),
    path("events/<int:event_id>/ratings/", views.coordinator_event_ratings_page, name="coordinator-event-ratings"),
    path("events/<int:event_id>/assign-shifts/", views.coordinator_shift_assignment_page, name="coordinator-shift-assignment"),

    # Volunteer signups
    path("signups/", views.coordinator_volunteer_signups_page, name="coordinator-signups"),

    # Shift management
    path("shifts/", views.coordinator_shifts_list_page, name="coordinator-shifts-list"),
    path("events/<int:event_id>/shifts/", views.coordinator_manage_shifts_page, name="coordinator-manage-shifts"),

    # Requests
    path("requests/", views.coordinator_request_list_page, name="coordinator-request-list"),
    path("requests/<int:request_id>/", views.coordinator_request_detail_page, name="coordinator-request-detail"),

    # Volunteers
    path("volunteers/<int:volunteer_id>/", views.coordinator_volunteer_profile_page, name="coordinator-volunteer-profile"),
    path("volunteers/<int:volunteer_id>/summary/", views.coordinator_volunteer_summary_page, name="coordinator-volunteer-summary"),

    # Certificate review
    path("certificates/", views.coordinator_certificate_review_page, name="coordinator-certificate-review"),
]
