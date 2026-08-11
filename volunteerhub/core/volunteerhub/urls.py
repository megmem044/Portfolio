# File: volunteerhub/urls.py
# Purpose:
#   Central routing for the entire VolunteerHub project.
#   This version adds routing for the new scheduling system.
#   Comments stay simple and explain why things are included.

from django.contrib import admin
from django.urls import path, include
from signups import views as signups_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    # Main landing page
    path("", signups_views.landing_page, name="landing"),

    # All existing signups routes
    path("", include("signups.urls")),

    # Coordinator routes
    path("coordinator/", include("signups.urls_coordinator")),

    # Existing API routes
    path("api/", include("signups.api_urls")),
]

# Media files support
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
