# Source Code File Documentation

## Overview
This document describes the purpose and functionality of each source code file in the VolunteerHub project.

---

## Core Application Files

### signups/models.py
Defines database models for core entities: Volunteer, Coordinator, Role, Enrollment, Certificate, CulturalInterest, Post, and VolunteerWorkPhoto. Each class represents a database table. Post model enables StressedSally to create and manage volunteer position announcements. VolunteerWorkPhoto allows JudoArtist to build artwork portfolios.

### signups/models_event.py
Defines event-related models: Event, EventShift, and EventRating. Event model stores event details, max volunteer count, language requirements, and certification needs. EventShift represents individual time slots within events. EventRating captures volunteer feedback and ratings for completed events. Supports PlannerPaco's event management workflow.

### signups/models_request.py
Defines request models: VolunteerRequest and ShiftRequest. VolunteerRequest tracks volunteer applications to events with status (PENDING, APPROVED, DECLINED). ShiftRequest tracks individual volunteer signup for specific event shifts. Manages the complete volunteer application workflow.

### signups/serializers.py
Converts model instances to JSON format for API responses. Serializers include VolunteerSerializer, CoordinatorSerializer, RoleSerializer, EnrollmentSerializer, CertificateSerializer, CulturalInterestSerializer, PostSerializer, and VolunteerWorkPhotoSerializer. Includes validation for certificate file types (PDF, JPEG) and size limits (5MB).

### signups/serializers_event.py
Serializes event models for API: EventSerializer, EventShiftSerializer, EventRatingSerializer. Includes nested data like volunteer names and event details for efficient API responses.

### signups/serializers_request.py
Serializes request models: VolunteerRequestSerializer, ShiftRequestSerializer. Includes related data like volunteer names, event names, and shift times for comprehensive API responses.

### signups/views.py
Main view file handling both HTML pages and API viewsets. Contains page rendering functions (landing_page, coordinator_signup_page, etc.) and API viewsets (VolunteerViewSet, CoordinatorViewSet, CertificateViewSet, RoleViewSet, EnrollmentViewSet, CulturalInterestViewSet, PostViewSet, VolunteerWorkPhotoViewSet). Handles authentication, user creation, and data management. CoordinatorViewSet.create() handles coordinator registration. VolunteerViewSet includes current() action for logged-in volunteer retrieval.

### signups/views_event.py
API viewsets for event management: EventViewSet, EventShiftViewSet, EventRatingViewSet. EventViewSet.volunteers() returns real-time signup list. EventViewSet.shifts() returns event shifts. EventViewSet.ratings() retrieves volunteer feedback. EventShiftViewSet.complete() marks shifts as finished and calculates hours worked. EventShiftViewSet.remove() deletes shifts and associated requests.

### signups/views_request.py
API viewsets for volunteer requests: VolunteerRequestViewSet, ShiftRequestViewSet. Manages volunteer applications to events and shift-level signups. Handles approval, declining, and status updates for applications.

### signups/admin.py
Registers all models with Django admin interface for database management. Includes VolunteerAdmin, CoordinatorAdmin, RoleAdmin, EnrollmentAdmin, CertificateAdmin, CulturalInterestAdmin, PostAdmin, VolunteerWorkPhotoAdmin.

### signups/urls.py
Main URL router for the application. Routes coordinator and volunteer URLs to their respective view functions.

### signups/urls_coordinator.py
Coordinator-specific URL patterns. Routes to coordinator dashboard, event management, shift management, volunteer profile viewing, and certificate review pages.

### signups/urls_volunteer.py
Volunteer-specific URL patterns. Routes to volunteer dashboard, event browsing, profile management, and schedule viewing.

### signups/api_urls.py
Central API router using Django REST Framework's DefaultRouter. Registers all viewsets to auto-generate REST endpoints. Routes include /api/volunteers/, /api/events/, /api/event-shifts/, /api/event-ratings/, /api/coordinators/, /api/certificates/, /api/roles/, /api/enrollments/, /api/cultural-interests/, /api/posts/, /api/volunteer-work-photos/, /api/volunteer-requests/, /api/shift-requests/.

### volunteerhub/settings.py
Django project configuration. Includes app definitions (signups, scheduling, posts), installed apps, database settings (SQLite), authentication configuration, and REST Framework settings. MEDIA_ROOT and MEDIA_URL configured for file uploads (certificates, photos).

### volunteerhub/urls.py
Root URL configuration. Includes admin interface, API routes, coordinator routes, volunteer routes, and static file serving.

---

## Template Files

### Coordinator Templates

**coordinator_dashboard.html**  
Main coordinator home page. Displays welcome message with coordinator name, shows dashboard with upcoming events summary, volunteer statistics, pending applications, and quick action buttons. Template uses Django template syntax {{ user.first_name }} for dynamic name display.

**coordinator_event_create.html**  
Form for creating new events. Input fields for event name, description, location, date/time, max volunteers, language level requirements, certification requirements (first aid, food safety), and cultural interests selection.

**coordinator_event_edit.html**  
Form for editing existing events. Same fields as create form plus status management (DRAFT, PUBLISHED, CLOSED, CANCELLED).

**coordinator_event_list.html**  
Displays all events created by coordinator. Shows event cards with name, date, volunteer count, status, and action buttons (view, edit, manage shifts, see ratings).

**coordinator_event_dashboard.html**  
Summary view for single event. Shows event details, shift information, volunteer signup status, and event statistics.

**coordinator_event_schedule.html**  
Calendar view of event shifts. Displays shifts chronologically with volunteer assignments and capacity information.

**coordinator_event_ratings.html**  
Displays volunteer ratings and feedback for completed events. Shows event header with back button (no star icon per requirements). Lists feedback cards showing volunteer name, rating stars, feedback comment, and submission date.

**coordinator_event_feedback.html**  
Professional card-based layout showing volunteer feedback. Displays gradient-bordered feedback cards with volunteer name, star rating, feedback comment, submission date, and completion status badge. Clean visual hierarchy matching coordinator dashboard design.

**coordinator_manage_shifts.html**  
Interface for managing event shifts. Shows shift list with date, time, volunteer count, and edit/delete options. Allows creating new shifts for the event.

**coordinator_volunteer_profile.html**  
Comprehensive volunteer profile page. Shows volunteer contact info (name, email, phone), school affiliation, profile photo, language level, cultural interests, total hours worked, certificates (with verification status), and enrollment history.

**coordinator_volunteer_signups.html**  
Lists all volunteers signed up for an event. Shows volunteer names, email, phone, enrollment status (PENDING, APPROVED, DECLINED), coordinator notes field, and missing certificates indicator.

**coordinator_shift_assignment.html**  
Manages volunteer assignments to specific shifts. Shows shift details and list of assigned volunteers with hours tracked.

**coordinator_request_list.html**  
Lists all pending volunteer applications to events. Shows applicant name, event applied for, status (PENDING, APPROVED, DECLINED), and action buttons.

**coordinator_request_detail.html**  
Detailed view of single volunteer application. Shows applicant info, event details, status, coordinator notes, missing certificate flags, and approval/decline buttons.

**coordinator_signin.html**  
Login form for coordinators. Email and password input fields with authentication.

**coordinator_signup.html**  
Registration form for new coordinators. Input fields for name, email, phone, address, organization, and password.

**coordinator_certificate_review.html**  
Certificate verification interface. Shows uploaded certificates with status (Pending, Verified), document preview, volunteer info, and action buttons to verify or reject.

---

### Volunteer Templates

**volunteer_profile.html**  
Volunteer dashboard homepage. Shows volunteer info (name, email, school, language level, cultural interests), profile photo, total hours worked, enrollment summary, and quick access to opportunities and schedule.

**volunteer_profile_edit.html**  
Form for editing volunteer profile. Input fields for name, email, phone, school, language level selection, cultural interest checkboxes, and profile photo upload.

**volunteer_schedule.html**  
Displays volunteer's assigned projects organized by status. Filter buttons show All, Pending, or Completed projects. Shows cards with project name, status badge, enrollment date, hours worked, and coordinator notes.

**volunteer_opportunities.html**  
Browse available volunteer opportunities. For EmiExplorer, filters display opportunities matching her language level and cultural interests. Shows event cards with name, date, location, language level, volunteer count, and sign-up button. Opportunities ordered by relevance for personalized recommendations.

**volunteer_signup.html**  
Registration form for new volunteers. Input fields for name, email, phone, school, language level selection, cultural interest checkboxes, profile photo upload, and password.

**volunteer_signin.html**  
Login form for volunteers. Email and password input fields.

**volunteer_summary.html**  
Summary view of volunteer profile. Shows volunteer stats (hours, events, certifications) and recent activity.

---

### Shared Templates

**base.html**  
Base template for all pages. Includes navigation bar, styling, Font Awesome icons, and footer. Implements responsive design for mobile and desktop. Extends across both coordinator and volunteer views.

**index.html**  
Landing page. Shows choice between volunteer and coordinator signup/signin with descriptive text for each option.

**session_timeout.html**  
Session timeout warning page. Notifies user when session has expired and provides login link.

---

## Static Files

### scheduling/static/scheduling/

**availability.js**  
JavaScript for volunteer availability calendar. Handles calendar interactions, date selection, and availability updates.

**shift_assignments.js**  
JavaScript for managing shift assignments. Handles volunteer-to-shift mapping, drag-and-drop if implemented, and real-time updates.

**shifts.js**  
JavaScript for shift management interface. Handles shift creation, editing, deletion, and display.

**volunteer_shifts.js**  
JavaScript for volunteer shift view. Shows volunteer's assigned shifts with filtering and status updates.

---

## Configuration Files

**manage.py**  
Django management command tool. Used for migrations, running development server, creating superusers, and database management.

**urls.py (root)**  
Main URL configuration. Routes requests to appropriate app views.

**which_settings.py**  
Utility to identify which settings configuration is active.

---

## Documentation Files

**IMPLEMENTATION_REPORT.md**  
Comprehensive summary of implemented features across all personas (StressedSally, PlannerPaco, JudoArtist, EmiExplorer) with technical architecture and test results.

**README_INTEGRATION.md**  
Integration documentation describing API structure and endpoint usage.

**QUICK_REFERENCE.md**  
Quick reference guide for commonly used endpoints and workflows.

---

## Database

**db.sqlite3**  
SQLite database file containing all application data. Includes volunteer and coordinator records, events, shifts, applications, certificates, and posts.
