# VolunteerHub Setup & Testing Guide

## System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (included with Python)
- Web browser (Chrome, Firefox, Safari, or Edge)

---

## Installation & Setup

### 1. Extract Project from Git Repository
Clone or extract the project repository to your local machine.

### 2. Create Virtual Environment
```
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```
venv\Scripts\activate
```

**Mac/Linux:**
```
source venv/bin/activate
```

### 4. Install Dependencies
```
pip install django djangorestframework django-cors-headers pillow python-dateutil
```

### 5. Run Migrations
```
python manage.py migrate
```

### 6. Create Superuser (Optional - for admin panel)
```
python manage.py createsuperuser
```

### 7. Start Development Server
```
python manage.py runserver
```

The application runs at `http://127.0.0.1:8000`

---

## Feature Testing Guide

### Test 1: StressedSally - Create and Manage Posts
1. Navigate to `http://127.0.0.1:8000/coordinator/signup/` to create coordinator account
2. Go to Create Post section and fill title, content, and optional image
3. Submit and post appears immediately in posts list: `http://127.0.0.1:8000/coordinator/posts/`
4. Edit post to mark as filled and status changes to CLOSED visible in post list

### Test 2: PlannerPaco - Create Event with Real-Time Signups
1. Log in as coordinator
2. Navigate to Create Event (`http://127.0.0.1:8000/coordinator/events/create/`)
3. Fill event details: name, date, location, max volunteers, language level
4. Create 2-3 shifts with different times
5. Publish event
6. In separate browser window, log in as volunteer and sign up for event
7. Return to coordinator event view and signup list updates in real-time showing new volunteer

### Test 3: PlannerPaco - Track Hours and Certifications
1. As coordinator, navigate to volunteer profile (`http://127.0.0.1:8000/coordinator/volunteers/{volunteer_id}/`)
2. View volunteer's total hours worked and certificate status (Pending/Verified)
3. Go to certificate review page (`http://127.0.0.1:8000/coordinator/certificates/`)
4. Verify or reject uploaded certificates and status updates immediately

### Test 4: JudoArtist - Track Project Progress
1. Log in as volunteer
2. Go to My Schedule (`http://127.0.0.1:8000/volunteer/schedule/`)
3. See projects with status badges (Upcoming/Ongoing/Completed)
4. Click filter buttons and display changes to show only selected status
5. Update project status from "Ongoing" to "Completed" and badge updates immediately

### Test 5: JudoArtist - Upload and View Portfolio
1. As volunteer, navigate to My Portfolio section
2. Upload 2-3 artwork photos with captions
3. Go to volunteer profile to view portfolio gallery
4. Verify photos display chronologically with captions and project association

### Test 6: EmiExplorer - Language-Level Filtering
1. Create volunteer account with English level set to "Beginner"
2. Set cultural interests to "Local Festivals" and "Community Events"
3. Navigate to Find Opportunities (`http://127.0.0.1:8000/volunteer/opportunities/`)
4. Verify only Beginner-level events display
5. Create event with Intermediate language level and verify it does NOT appear in volunteer's filtered list
6. Create event with Beginner language level and verify it appears immediately

### Test 7: EmiExplorer - Personalized Recommendations
1. Log in as beginner English volunteer with cultural interests selected
2. Go to Home Dashboard (`http://127.0.0.1:8000/volunteer/`)
3. View Personalized Recommendations section showing events matching interests
4. Verify events matching MORE interests appear higher in list
5. Verify event instructions use simple, beginner-friendly language

### Test 8: Real-Time Updates - Volunteer Signup
1. Coordinator opens event at `http://127.0.0.1:8000/api/events/{event_id}/volunteers/`
2. Volunteer signs up for event in separate window
3. Refresh coordinator view or check API endpoint and volunteer appears in signup list
4. Volunteer cancels signup and coordinator view updates showing volunteer removed

### Test 9: API Testing - Get All Events
```
curl http://127.0.0.1:8000/api/events/
```
Should return JSON list of all events with details (name, date, max_volunteers, status, etc.)

### Test 10: API Testing - Get Specific Volunteer
```
curl http://127.0.0.1:8000/api/volunteers/{volunteer_id}/
```
Should return JSON with volunteer details (name, email, school, hours_worked, certificates, etc.)

### Test 11: API Testing - Get Event Ratings
```
curl http://127.0.0.1:8000/api/event-ratings/?event={event_id}
```
Should return JSON list of all ratings/feedback for the event with volunteer names and comments

### Test 12: API Testing - Get Shift Details
```
curl http://127.0.0.1:8000/api/event-shifts/{shift_id}/
```
Should return shift details including shift_date, start_time, end_time, hours_worked calculation, and volunteer count

---

## Common Commands

**View Database in Admin Panel**
```
python manage.py createsuperuser
```
Then navigate to `http://127.0.0.1:8000/admin/` and log in

**Reset Database**
```
python manage.py migrate zero
python manage.py migrate
```

**Create Test Data**
```
python manage.py shell
# Run Django shell to insert test data manually
```

**Check Server Status**
Visit `http://127.0.0.1:8000/` - Should display landing page with signup/signin options

**Access API Root**
Visit `http://127.0.0.1:8000/api/` - Should list all available API endpoints

---

## Troubleshooting

**Port Already in Use**
If port 8000 is in use, run: `python manage.py runserver 8001`

**Database Locked**
Delete `db.sqlite3` and re-run migrations: `python manage.py migrate`

**Module Not Found**
Ensure virtual environment is activated and all packages installed: `pip list`

**Template Not Found**
Verify template files exist in `signups/templates/` directory with correct folder structure

**Static Files Not Loading**
Run: `python manage.py collectstatic --noinput`

---

## Accessing the Application

**Volunteer Interface:** `http://127.0.0.1:8000/volunteer/`
**Coordinator Interface:** `http://127.0.0.1:8000/coordinator/`
**API Root:** `http://127.0.0.1:8000/api/`
**Admin Panel:** `http://127.0.0.1:8000/admin/`
**Landing Page:** `http://127.0.0.1:8000/`

---

## Next Steps After Setup

1. Run through all 12 feature tests above to verify functionality
2. Check API endpoints using curl or Postman
3. Review data in admin panel at `/admin/`
4. Test on mobile device or responsive browser tools
5. Create test accounts for both coordinator and volunteer roles
6. Walk through complete workflows from signup to project completion

