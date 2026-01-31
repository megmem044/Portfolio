# URL routing for volunteer pages

from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path("signup/", views.volunteer_signup_page, name="volunteer-signup"),
    path("signin/", views.volunteer_signin_page, name="volunteer-signin"),

    # Dashboard
    path("home/", views.home_page, name="volunteer-home"),

    # Profile
    path("profile/", views.volunteer_profile_page_simple, name="volunteer-profile"),

    # Preferences
    path("preferences/", views.emi_preferences_page, name="volunteer-preferences"),

    # Certificates
    path("certificates/", views.certificate_upload_page, name="volunteer-certificates"),

    # Opportunities
    path("opportunities/", views.browse_opportunities_page, name="volunteer-opportunities"),

    # Availability
    path("availability/", views.volunteer_availability_page, name="volunteer-availability"),

    # Hours Worked
    path("hours/", views.volunteer_hours_page, name="volunteer-hours"),

    # Event Rating
    path("rate/", views.volunteer_event_rating_page, name="volunteer-rate-events"),

    # Schedule
    path("schedule/", views.volunteer_schedule_page, name="volunteer-schedule"),
]
