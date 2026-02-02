# File: signups/urls.py
# Purpose:
#   Defines front-end template routes for the VolunteerHub system.
#   These routes render HTML templates. They never expose API data.

from django.urls import path, include
from . import views

urlpatterns = [

    # Student volunteer signup
    path('volunteer-signup/', views.signup_landing_page, name='volunteer-signup'),

    # Coordinator signup
    path('coordinator-signup/', views.coordinator_signup_page, name='coordinator-signup'),

    # Coordinator dashboard
    path('coordinator-dashboard/', views.coordinator_dashboard_page, name='coordinator-dashboard'),

    # Home page after signup
    path("home/", views.home_page, name="home"),

    # Volunteer list page
    path("volunteer-list/", views.volunteer_list_page, name="volunteer-list-page"),

    # Certificate upload page
    path("certificates-page/", views.certificate_upload_page, name="certificate-upload-page"),

    # EmiExplorer Preferences page
    # This must match the name used in the template
    path("preferences/", views.emi_preferences_page, name="emi-preferences-page"),

    # Posts page
    path("posts/", views.posts_list_page, name="posts-list-page"),

    # Create post page
    path("create-post/", views.create_post_page, name="create-post-page"),

    # Edit post page
    path("edit-post/", views.edit_post_page, name="edit-post-page"),

    # Volunteer profile page
    path('volunteer-profile/<int:volunteer_id>/', views.volunteer_profile_page, name='volunteer-profile'),

    # Role creation page
    path("role-create/", views.role_create_page, name="role-create-page"),

    # Signin pages
    path("volunteer/signin/", views.volunteer_signin_page, name="volunteer-signin"),
    path("volunteer/signup/", views.volunteer_signup_page, name="volunteer-signup-alt"),
    path("volunteer/home/", views.volunteer_dashboard_page, name="volunteer-home-alt"),
    path("volunteer/profile/", views.volunteer_profile_page_simple, name="volunteer-profile-simple"),
    path("volunteer/opportunities/", views.volunteer_opportunities_page, name="volunteer-opportunities"),
    path("volunteer/schedule/", views.volunteer_schedule_page, name="volunteer-schedule"),
    path("volunteer/certificates/", views.volunteer_certificates_page, name="volunteer-certificates"),
    path("volunteer/rate/", views.volunteer_event_rating_page, name="volunteer-event-rating"),
    path("volunteer/photos/", views.volunteer_photos_page, name="volunteer-photos"),
    path("coordinator/signin/", views.coordinator_signin_page, name="coordinator-signin"),
    path("coordinator/signup/", views.coordinator_signup_page, name="coordinator-signup-alt"),
    
    # Logout
    path("logout/", views.logout_view, name="logout"),
    
    # Coordinator sub-routes
    path("coordinator/", include("signups.urls_coordinator")),
]
