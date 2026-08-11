# VolunteerHub Implementation Report

**Project:** CMPT 370 - Team 9  
**Status:** All features fully implemented and tested  
**Date:** December 9, 2025

---

## Overview

VolunteerHub is a Django-based volunteer management platform with REST APIs serving five personas: StressedSally (event posting), PlannerPaco (volunteer recruitment), JudoArtist (progress tracking), and EmiExplorer (personalized recommendations).

---

## Feature Implementation Summary

### Persona 2: StressedSally - Event Posting

**Status:** Fully Implemented

Sally posts volunteer positions with title, detailed content, and optional images. Posts display in real-time to all volunteers. The Post model stores unrestricted text and auto-timestamps creation. Sally can edit posts to mark positions as filled by changing event status from PUBLISHED to CLOSED, preventing additional applications.

**Key Features:** Post creation with images, real-time visibility, status management  
**Models:** Post (title, content, author, image, created_at)  
**Acceptance Tests:** Both pass

---

### Persona 3: PlannerPaco - Volunteer Recruitment & Management

**Status:** Fully Implemented

Paco creates detailed events with multiple volunteer shifts. The system maintains a real-time volunteer signup list that updates automatically as volunteers apply and cancel. He can view volunteer profiles including contact information, hours worked, and certification status.

The Event model stores event details, max_volunteers, language requirements, and certification requirements. EventShift represents individual time slots. VolunteerRequest tracks applications with status (PENDING, APPROVED, DECLINED). The Certificate model tracks certifications with status (Pending, Verified). Hours are calculated automatically from shift duration.

**Key Features:** Multi-shift events, real-time signup tracking, volunteer hour calculation, certification verification  
**Models:** Event, EventShift, VolunteerRequest, ShiftRequest, Certificate  
**API Endpoints:** /api/events/, /api/events/{id}/volunteers/, /api/event-shifts/, /api/certificates/  
**Acceptance Tests:** Both pass - real-time updates and auto-calculations working

---

### Persona 4: JudoArtist - Progress Tracking & Portfolio

**Status:** Fully Implemented

Judo tracks volunteer projects organized by status (Upcoming, Ongoing, Completed). The Enrollment model stores project status and hours worked. Filter buttons allow quick categorization by status. Judo uploads artwork photos linked to projects through VolunteerWorkPhoto model. The portfolio gallery displays all contributions chronologically.

**Key Features:** Status-based project organization, visual progress indicators, multi-image upload per project, chronological gallery  
**Models:** Enrollment (status, hours_worked), VolunteerWorkPhoto (image, caption, enrollment_fk)  
**UI:** Status badges, filter buttons, responsive gallery layout  
**Acceptance Tests:** Both pass - status updates visible, photos display correctly

---

### Persona 5: EmiExplorer - Personalized Recommendations

**Status:** Fully Implemented

Emi sets her English proficiency level (Beginner/Intermediate/Advanced) and cultural interests in her profile. The system filters opportunities to match her language comfort level and interests. Events display with simplified instructions appropriate to proficiency level.

The recommendation algorithm retrieves events matching Emi's cultural_interests and language_level, ordering by relevance. Simplified event instructions use appropriate vocabulary and sentence structure. Event descriptions, reminders, and coordinator support all use beginner-friendly language.

**Key Features:** Language-level filtering, interest-based recommendations, simplified instructions, personalized dashboard  
**Models:** Volunteer (english_level, cultural_interests), Event (language_level, cultural_interests)  
**Filtering:** /api/events/?language_level={level}&cultural_interests={interest}  
**Acceptance Tests:** Both pass - correct filtering and simplified language verified

---

## Technical Architecture

**Stack:** Django 4.x + Django REST Framework, SQLite, HTML5/CSS3 custom styling, JavaScript ES6, Font Awesome 6.0

**Core Models:**
- User (Django built-in) extends to Volunteer/Coordinator (1:1 extended)
- Event links to EventShift (1:N), VolunteerRequest (1:N)
- Volunteer links to Certificate (1:N), VolunteerWorkPhoto (1:N)
- CulturalInterest (M:M junction across Event/Role/Volunteer)

**Key Endpoints:**
- Events: `/api/events/`, `/api/events/{id}/volunteers/`, `/api/events/{id}/shifts/`
- Volunteers: `/api/volunteers/`, `/api/volunteers/{id}/photos/`
- Requests: `/api/volunteer-requests/`, `/api/shift-requests/`
- Certificates: `/api/certificates/`
- Ratings: `/api/event-ratings/`

**Development:** manage.py for migrations, Django ORM for queries, REST APIs for platform-agnostic architecture
